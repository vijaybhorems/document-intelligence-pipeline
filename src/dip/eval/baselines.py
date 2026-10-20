"""Baselines every real system must beat (SPEC §10.9).

- ``all_absent``: predicts nothing. Recall is zero by construction; it shows how
  imbalanced each field is, and why accuracy would be a misleading metric.
- ``keyword``: a clause is "present" if any canonical cue appears anywhere in the
  contract, with the surrounding sentence as evidence. Typed fields come from
  regexes. Fast, free, and a useful floor: per field it's sometimes hard to beat.

Because the keyword baseline searches for the same cues that define the phrasing
slice, its non-canonical recall comes only from cues appearing *elsewhere* in the
contract. That's the gap a good prompt has to close.
"""

import re
from collections.abc import Iterator
from typing import Any

from dip.eval.slices import has_cue
from dip.extract.system import System, SystemOutput
from dip.schema.domain import (
    ClauseField,
    ClauseSet,
    ContractFields,
    DateField,
    DurationField,
    Evidence,
    JurisdictionField,
    Party,
    PartyListField,
    TextField,
)
from dip.schema.registry import FIELDS, FieldType
from dip.validate.normalize import find_dates, parse_durations, parse_jurisdictions

MAX_EVIDENCE_PER_FIELD = 3
MAX_QUOTE_CHARS = 600


class SimpleSystem:
    """A free, deterministic system: predicts one contract at a time, no API calls."""

    name = "simple"

    def predict(self, text: str) -> ContractFields:
        raise NotImplementedError

    def config(self) -> dict[str, Any]:
        return {}

    def predict_all(
        self, texts: dict[str, str], max_cost_usd: float | None = None
    ) -> dict[str, SystemOutput]:
        return {doc_id: SystemOutput(fields=self.predict(text)) for doc_id, text in texts.items()}


class AllAbsent(SimpleSystem):
    name = "all_absent"

    def predict(self, text: str) -> ContractFields:
        return ContractFields()


# ── Keyword baseline ─────────────────────────────────────────────────────────

_SENTENCE = re.compile(r"[^.;\n]+(?:[.;]|\n|$)")


def _sentences(text: str) -> Iterator[tuple[int, int]]:
    for m in _SENTENCE.finditer(text):
        if m.group().strip():
            yield m.start(), m.end()


def _evidence(text: str, start: int, end: int) -> Evidence:
    start += len(text[start:end]) - len(text[start:end].lstrip())
    end = min(end, start + MAX_QUOTE_CHARS)
    return Evidence(
        quote=text[start:end].rstrip(),
        char_start=start,
        char_end=start + len(text[start:end].rstrip()),
    )


_NUMBER = r"\d+|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirty|sixty|ninety"
_RENEWAL_TERM = re.compile(
    rf"(?P<succ>successive\s+)?(?:additional\s+)?(?P<num>{_NUMBER})(?:\s*\(\d+\))?[\s-]+(?P<unit>year|month)s?",
    re.I,
)
_NOTICE = re.compile(
    rf"(?P<num>{_NUMBER})(?:\s*\(\d+\))?\s+(?P<unit>day|month)s?['\u2019]?\s+"
    r"(?:prior\s+)?(?:written\s+)?(?:notice|prior)",
    re.I,
)
_WORD_TO_DIGITS = {"thirty": "30", "sixty": "60", "ninety": "90"}
_GOVERNED_BY = re.compile(
    r"governed\s+by[^.;]{0,80}?\blaws?\s+of\s+(?:the\s+)?(?P<place>[^.;()]{3,70})", re.I
)
_BETWEEN = re.compile(
    r"\bbetween\s+(?P<a>[^,(\n\"“]{3,120})[\s\S]{0,400}?\band\s+(?P<b>[^,(\n\"“]{3,120})",
    re.I,
)


class KeywordBaseline(SimpleSystem):
    name = "keyword"

    def predict(self, text: str) -> ContractFields:
        sentences = list(_sentences(text))
        return ContractFields(
            document_name=self._document_name(text),
            parties=self._parties(text),
            agreement_date=self._agreement_date(text),
            effective_date=self._date_near(text, sentences, re.compile(r"\beffective\b", re.I)),
            expiration_date=self._date_near(
                text, sentences, re.compile(r"\b(?:expire|terminate)s?\s+on\b", re.I)
            ),
            renewal_term=self._renewal_term(text, sentences),
            notice_period_to_terminate_renewal=self._renewal_notice(text, sentences),
            governing_law=self._governing_law(text),
            clauses=self._clauses(text, sentences),
        )

    # Clauses: cue anywhere means present.
    def _clauses(self, text: str, sentences: list[tuple[int, int]]) -> ClauseSet:
        clauses: dict[str, ClauseField] = {}
        for spec in FIELDS:
            if spec.field_type is not FieldType.CLAUSE:
                continue
            hits = [(s, e) for s, e in sentences if has_cue(spec, text[s:e])]
            evidence = [_evidence(text, s, e) for s, e in hits[:MAX_EVIDENCE_PER_FIELD]]
            clauses[spec.name] = ClauseField(present=bool(hits), evidence=evidence)
        return ClauseSet(**clauses)

    @staticmethod
    def _document_name(text: str) -> TextField:
        offset = 0
        for line in text[:1000].splitlines(keepends=True):
            stripped = line.strip()
            if "agreement" in stripped.casefold() and len(stripped) <= 120:
                start = offset + line.index(stripped)
                return TextField(
                    value=stripped,
                    evidence=[
                        Evidence(quote=stripped, char_start=start, char_end=start + len(stripped))
                    ],
                )
            offset += len(line)
        return TextField()

    @staticmethod
    def _parties(text: str) -> PartyListField:
        m = _BETWEEN.search(text[:3000])
        if not m:
            return PartyListField()
        names = [m["a"].strip(" ,.\t"), m["b"].strip(" ,.\t")]
        parties = [Party(name=n) for n in names if n]
        evidence = [Evidence(quote=m.group(), char_start=m.start(), char_end=m.end())]
        return PartyListField(parties=parties, evidence=evidence)

    @staticmethod
    def _agreement_date(text: str) -> DateField:
        dates = find_dates(text[:1500])
        if not dates:
            return DateField()
        first = dates[0]
        quote = text[first.start : first.end]
        return DateField(
            values=[first.value],
            raw_text=quote,
            evidence=[Evidence(quote=quote, char_start=first.start, char_end=first.end)],
        )

    @staticmethod
    def _date_near(
        text: str, sentences: list[tuple[int, int]], trigger: re.Pattern[str]
    ) -> DateField:
        for s, e in sentences:
            sentence = text[s:e]
            if (hit := trigger.search(sentence)) and (dates := find_dates(sentence[hit.start() :])):
                return DateField(
                    values=[dates[0].value],
                    raw_text=sentence.strip()[:MAX_QUOTE_CHARS],
                    evidence=[_evidence(text, s, e)],
                )
        return DateField()

    @staticmethod
    def _duration(match: re.Match[str], successive: bool) -> DurationField | None:
        number = _WORD_TO_DIGITS.get(match["num"].lower(), match["num"])
        phrase = f"{'successive ' if successive else ''}{number} {match['unit']}s"
        parsed = parse_durations(phrase)
        return (
            DurationField(values=parsed.values, raw_text=match.group()) if parsed.values else None
        )

    def _renewal_term(self, text: str, sentences: list[tuple[int, int]]) -> DurationField:
        for s, e in sentences:
            sentence = text[s:e]
            m = _RENEWAL_TERM.search(sentence) if re.search(r"\brenew", sentence, re.I) else None
            if m and (field := self._duration(m, successive=bool(m["succ"]))):
                return field.model_copy(update={"evidence": [_evidence(text, s, e)]})
        return DurationField()

    def _renewal_notice(self, text: str, sentences: list[tuple[int, int]]) -> DurationField:
        for s, e in sentences:
            sentence = text[s:e]
            m = _NOTICE.search(sentence) if re.search(r"\brenew", sentence, re.I) else None
            if m and (field := self._duration(m, successive=False)):
                return field.model_copy(update={"evidence": [_evidence(text, s, e)]})
        return DurationField()

    @staticmethod
    def _governing_law(text: str) -> JurisdictionField:
        for m in _GOVERNED_BY.finditer(text):
            parsed = parse_jurisdictions(m["place"])
            if parsed.values:
                return JurisdictionField(
                    values=parsed.values,
                    raw_text=m["place"].strip(),
                    evidence=[Evidence(quote=m.group(), char_start=m.start(), char_end=m.end())],
                )
        return JurisdictionField()


SYSTEMS: dict[str, System] = {s.name: s for s in (AllAbsent(), KeywordBaseline())}
