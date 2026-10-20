"""The phrasing slice (SPEC §10.6): does extraction survive unusual wording?

A gold-present (contract, field) is **canonical** if any gold span contains one of
the field's ``canonical_cues``, and **non-canonical** otherwise. Recall on the
non-canonical slice approaching recall on the canonical slice means the prompt
copes with how contracts actually phrase things.
"""

import re
from enum import StrEnum
from functools import cache

from dip.schema.domain import Evidence
from dip.schema.registry import FieldSpec


class Slice(StrEnum):
    CANONICAL = "canonical"
    NON_CANONICAL = "non_canonical"


@cache
def _cue_pattern(cues: tuple[str, ...]) -> re.Pattern[str]:
    return re.compile("|".join(rf"\b{re.escape(cue)}" for cue in cues), re.IGNORECASE)


def has_cue(spec: FieldSpec, text: str) -> bool:
    return bool(spec.canonical_cues) and bool(_cue_pattern(spec.canonical_cues).search(text))


def phrasing_slice(spec: FieldSpec, gold_evidence: list[Evidence]) -> Slice | None:
    """``None`` when the field has no cues or gold has no spans to classify."""
    if not spec.canonical_cues or not gold_evidence:
        return None
    if any(has_cue(spec, e.quote) for e in gold_evidence):
        return Slice.CANONICAL
    return Slice.NON_CANONICAL
