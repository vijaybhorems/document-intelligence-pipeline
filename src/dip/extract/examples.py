"""Field notes for prompts v2+, built from TRAIN gold only (SPEC §7.2, decision D5).

For each field:

- **variants**: the shortest gold spans that *don't* contain the field's obvious
  wording (non-canonical). They teach the model how the clause is actually
  phrased when the keywords aren't there.
- **positive**: one short, typical gold span.
- **hard negative**: a sentence that contains the field's keywords, from a
  contract whose expert labels say the clause is *absent*. The dominant Phase 4
  error is over-triggering on exactly this kind of text.

Only clause-like text is used: a complete sentence with obligation language
("shall", "may", "agrees"...), no redactions. CUAD often labels a clause as
several disjoint fragments, and the shortest fragment ("and which the Company
has not repurchased.") teaches nothing out of context.

Using dev or test contracts here would leak labels into the prompt and inflate
every score, so ``build_field_notes`` only ever receives the train split.
Selection is deterministic (shortest first, then doc_id), so the committed
``field_notes.json`` can be regenerated exactly.
"""

import json
import re
from collections.abc import Iterable
from pathlib import Path

from pydantic import BaseModel

from dip.eval.slices import has_cue
from dip.schema.domain import GoldRecord, field_of, is_present
from dip.schema.registry import FIELDS, FieldSpec

MAX_VARIANTS = 3
MIN_EXAMPLE_CHARS = 80
MAX_EXAMPLE_CHARS = 320

_SENTENCE = re.compile(r"[^.;\n]+[.;]")
_OBLIGATION = re.compile(
    r"\b(shall|will|may|must|agrees?|agreed|is entitled|has the right|undertakes?)\b", re.I
)
_REDACTED = re.compile(r"\[\s*\*+\s*\]|\[\s*\]|\*{3,}")


class FieldNotes(BaseModel):
    variants: list[str] = []
    positive: str | None = None
    hard_negative: str | None = None


_ZERO_WIDTH = dict.fromkeys(map(ord, (chr(0x200B), chr(0x200C), chr(0x200D), chr(0xFEFF))))


def _clean(text: str) -> str:
    return " ".join(text.translate(_ZERO_WIDTH).split())


def _fits(text: str) -> bool:
    """A complete, readable clause: right length, starts like a sentence, creates an obligation."""
    return (
        MIN_EXAMPLE_CHARS <= len(text) <= MAX_EXAMPLE_CHARS
        and (text[0].isupper() or text[0] == "(")
        and text[-1] in ".;"
        and bool(_OBLIGATION.search(text))
        and not _REDACTED.search(text)
    )


def _notes_for(spec: FieldSpec, train: list[tuple[GoldRecord, str]]) -> FieldNotes:
    spans: list[tuple[int, str, str]] = []  # (length, doc_id, quote)
    negatives: list[tuple[int, str, str]] = []
    for record, text in train:
        field = field_of(record.fields, spec.name)
        if is_present(field):
            for e in field.evidence:
                quote = _clean(e.quote)
                if _fits(quote):
                    spans.append((len(quote), record.doc_id, quote))
        elif spec.canonical_cues:
            for m in _SENTENCE.finditer(text):
                sentence = _clean(m.group())
                if _fits(sentence) and has_cue(spec, sentence):
                    negatives.append((len(sentence), record.doc_id, sentence))
    spans.sort()
    negatives.sort()
    canonical = [q for _, _, q in spans if has_cue(spec, q)]
    non_canonical = [q for _, _, q in spans if not has_cue(spec, q)]
    variants: list[str] = []
    for quote in non_canonical:
        if quote not in variants:
            variants.append(quote)
        if len(variants) == MAX_VARIANTS:
            break
    return FieldNotes(
        variants=variants if spec.canonical_cues else [],
        positive=(canonical or [q for _, _, q in spans] or [None])[0],
        hard_negative=negatives[0][2] if negatives else None,
    )


def build_field_notes(train: Iterable[tuple[GoldRecord, str]]) -> dict[str, FieldNotes]:
    records = list(train)
    return {spec.name: _notes_for(spec, records) for spec in FIELDS}


def write_field_notes(notes: dict[str, FieldNotes], path: Path) -> None:
    payload = {name: n.model_dump(exclude_none=True) for name, n in notes.items()}
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def load_field_notes(path: Path) -> dict[str, FieldNotes]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    return {name: FieldNotes.model_validate(value) for name, value in raw.items()}
