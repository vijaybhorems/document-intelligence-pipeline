"""Compare one predicted field with its gold label (SPEC §10.3).

Every matcher returns ``Counts`` for one (contract, field, metric):

- **presence**: was the field found at all? Scored for every field.
- **value**: is the normalized value right? Typed fields only. ``None`` when gold
  marks the relevant text but has no usable value (CUAD's 160
  ``span_without_answer`` labels), because there is nothing to compare against.
- **span**: do the evidence quotes match gold spans? Clause fields only.

A wrong value is both a false positive (we asserted something false) and a
false negative (we missed the true value), so it costs precision *and* recall.
"""

import re
import unicodedata
from collections.abc import Callable, Sequence
from dataclasses import dataclass

from rapidfuzz import fuzz

from dip.schema.domain import (
    ClauseField,
    DateField,
    Duration,
    DurationField,
    DurationUnit,
    JurisdictionField,
    PartialDate,
    PartyListField,
    TextField,
    has_value,
    is_present,
)
from dip.validate.normalize import parse_jurisdictions

SPAN_JACCARD_THRESHOLD = 0.5  # CUAD paper convention
PARTY_NAME_THRESHOLD = 90.0
DOCUMENT_NAME_THRESHOLD = 85.0
DURATION_TOLERANCE = 0.02  # "6 months" == "180 days", "12 months" == "1 year"


@dataclass(frozen=True)
class Counts:
    tp: int = 0
    fp: int = 0
    fn: int = 0
    tn: int = 0

    def __add__(self, other: "Counts") -> "Counts":
        return Counts(
            self.tp + other.tp, self.fp + other.fp, self.fn + other.fn, self.tn + other.tn
        )

    @property
    def precision(self) -> float | None:
        return self.tp / (self.tp + self.fp) if self.tp + self.fp else None

    @property
    def recall(self) -> float | None:
        return self.tp / (self.tp + self.fn) if self.tp + self.fn else None

    @property
    def f1(self) -> float | None:
        """Harmonic mean of P and R. ``None`` when there's nothing to score (no tp, fp or fn)."""
        if self.tp + self.fp + self.fn == 0:
            return None
        return 2 * self.tp / (2 * self.tp + self.fp + self.fn)

    @property
    def support(self) -> int:
        """Gold positives."""
        return self.tp + self.fn


def presence(pred_present: bool, gold_present: bool) -> Counts:
    if pred_present and gold_present:
        return Counts(tp=1)
    if pred_present:
        return Counts(fp=1)
    if gold_present:
        return Counts(fn=1)
    return Counts(tn=1)


# ── Single-answer values: dates, durations, document name ───────────────────


def _single_value[T](pred: Sequence[T], gold: Sequence[T], same: Callable[[T, T], bool]) -> Counts:
    """One decision per field: right if any predicted value matches any gold value.

    CUAD's multi-valued answers for these fields are mostly alternatives for one
    fact ("07/31/2000; 07/[]/2000"), so any match counts.
    """
    if not gold:
        return Counts(fp=1) if pred else Counts(tn=1)
    if not pred:
        return Counts(fn=1)
    if any(same(p, g) for p in pred for g in gold):
        return Counts(tp=1)
    return Counts(fp=1, fn=1)


def date_matches(pred: PartialDate, gold: PartialDate) -> bool:
    """Equal on every component gold knows. A year-only gold date matches any date that year."""
    return all(
        getattr(gold, part) is None or getattr(pred, part) == getattr(gold, part)
        for part in ("year", "month", "day")
    )


_DAYS_PER_UNIT = {
    DurationUnit.DAYS: 1.0,
    DurationUnit.WEEKS: 7.0,
    DurationUnit.MONTHS: 365.25 / 12,
    DurationUnit.YEARS: 365.25,
}


def duration_matches(pred: Duration, gold: Duration) -> bool:
    """Same length within 2%, across units. Ignores successive/count: that's the renewal pattern."""
    pred_days = pred.value * _DAYS_PER_UNIT[pred.unit]
    gold_days = gold.value * _DAYS_PER_UNIT[gold.unit]
    return abs(pred_days - gold_days) <= DURATION_TOLERANCE * gold_days


_PERPETUAL = "perpetual"


def _date_tokens(field: DateField) -> list[PartialDate | str]:
    return [*field.values, *([_PERPETUAL] if field.perpetual else [])]


def _duration_tokens(field: DurationField) -> list[Duration | str]:
    return [*field.values, *([_PERPETUAL] if field.perpetual else [])]


def _same_date(pred: PartialDate | str, gold: PartialDate | str) -> bool:
    if isinstance(pred, str) or isinstance(gold, str):
        return pred == gold
    return date_matches(pred, gold)


def _same_duration(pred: Duration | str, gold: Duration | str) -> bool:
    if isinstance(pred, str) or isinstance(gold, str):
        return pred == gold
    return duration_matches(pred, gold)


def _normalize_text(text: str) -> str:
    folded = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().casefold()
    return " ".join(re.findall(r"[a-z0-9]+", folded))


def _same_document_name(pred: str, gold: str) -> bool:
    return fuzz.ratio(_normalize_text(pred), _normalize_text(gold)) >= DOCUMENT_NAME_THRESHOLD


def _unscorable(
    gold: TextField | PartyListField | DateField | DurationField | JurisdictionField,
) -> bool:
    """Gold points at the text but carries no value (e.g. an event-based expiry)."""
    return is_present(gold) and not has_value(gold)


def value_date(pred: DateField, gold: DateField) -> Counts | None:
    if _unscorable(gold):
        return None
    return _single_value(_date_tokens(pred), _date_tokens(gold), _same_date)


def value_duration(pred: DurationField, gold: DurationField) -> Counts | None:
    if _unscorable(gold):
        return None
    return _single_value(_duration_tokens(pred), _duration_tokens(gold), _same_duration)


def value_text(pred: TextField, gold: TextField) -> Counts | None:
    if _unscorable(gold):
        return None
    to_list = lambda f: [f.value] if f.value and f.value.strip() else []  # noqa: E731
    return _single_value(to_list(pred), to_list(gold), _same_document_name)


# ── Set values: jurisdictions, parties ───────────────────────────────────────


def _match_sets[T](
    pred: Sequence[T], gold: Sequence[T], score: Callable[[T, T], float], threshold: float
) -> Counts:
    """Greedy one-to-one matching, best pairs first. Each value is its own TP/FP/FN."""
    if not pred and not gold:
        return Counts(tn=1)
    pairs = sorted(
        ((score(p, g), i, j) for i, p in enumerate(pred) for j, g in enumerate(gold)),
        key=lambda x: (-x[0], x[1], x[2]),
    )
    used_pred: set[int] = set()
    used_gold: set[int] = set()
    for value, i, j in pairs:
        if value < threshold:
            break
        if i not in used_pred and j not in used_gold:
            used_pred.add(i)
            used_gold.add(j)
    matched = len(used_pred)
    return Counts(tp=matched, fp=len(pred) - matched, fn=len(gold) - matched)


def _canonical_jurisdictions(values: list[str]) -> list[str]:
    canonical: list[str] = []
    for value in values:
        parsed = parse_jurisdictions(value)
        for name in parsed.values or [value.strip()]:
            if name not in canonical:
                canonical.append(name)
    return canonical


def value_jurisdiction(pred: JurisdictionField, gold: JurisdictionField) -> Counts | None:
    if _unscorable(gold):
        return None
    return _match_sets(
        _canonical_jurisdictions(pred.values),
        _canonical_jurisdictions(gold.values),
        lambda p, g: 1.0 if p.casefold() == g.casefold() else 0.0,
        1.0,
    )


_LEGAL_SUFFIXES = re.compile(
    r"\b(inc|incorporated|corp|corporation|co|company|llc|l l c|ltd|limited|lp|l p|llp|plc|"
    r"gmbh|ag|sa|s a|nv|bv|pte|pty|the)\b"
)


def normalize_party_name(name: str) -> str:
    """For matching only: 'NETGEAR, Inc.' and 'Netgear Inc' compare equal."""
    return " ".join(_LEGAL_SUFFIXES.sub(" ", _normalize_text(name)).split())


def value_parties(pred: PartyListField, gold: PartyListField) -> Counts | None:
    if _unscorable(gold):
        return None
    return _match_sets(
        [normalize_party_name(p.name) for p in pred.parties],
        [normalize_party_name(p.name) for p in gold.parties],
        fuzz.ratio,
        PARTY_NAME_THRESHOLD,
    )


# ── Clause evidence spans ────────────────────────────────────────────────────


def _tokens(text: str) -> set[str]:
    return set(re.findall(r"\w+", text.casefold()))


def token_jaccard(a: str, b: str) -> float:
    ta, tb = _tokens(a), _tokens(b)
    if not ta and not tb:
        # Spans with no words, e.g. redaction marks like "[●]": compare them verbatim.
        return 1.0 if a.strip() and a.strip() == b.strip() else 0.0
    return len(ta & tb) / len(ta | tb)


def spans(pred: ClauseField, gold: ClauseField) -> Counts:
    """Match predicted quotes to gold spans one-to-one by token Jaccard >= 0.5."""
    return _match_sets(
        [e.quote for e in pred.evidence],
        [e.quote for e in gold.evidence],
        token_jaccard,
        SPAN_JACCARD_THRESHOLD,
    )
