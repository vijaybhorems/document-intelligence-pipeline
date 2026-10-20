"""Score predictions against gold, then roll results up (SPEC §10.4).

``score_document`` produces one ``FieldResult`` per (contract, field, metric).
``aggregate`` pools them per field, per field type and per clause family:

- **micro**: add up TP/FP/FN across fields, then compute P/R/F1. Dominated by
  common fields.
- **macro**: compute F1 per field, then average. Every field counts equally, so
  rare fields are visible.

The headline metric is *presence* for clauses and *value* for typed fields.
"""

from collections import defaultdict
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from enum import StrEnum
from statistics import fmean

from dip.eval import matchers
from dip.eval.matchers import Counts
from dip.eval.slices import Slice, phrasing_slice
from dip.schema.domain import (
    ClauseField,
    ContractFields,
    DateField,
    DurationField,
    JurisdictionField,
    PartyListField,
    TextField,
    field_of,
    is_present,
)
from dip.schema.registry import FIELDS, FieldSpec, FieldType


class Metric(StrEnum):
    PRESENCE = "presence"
    VALUE = "value"
    SPAN = "span"


def headline_metric(field_type: FieldType) -> Metric:
    return Metric.PRESENCE if field_type is FieldType.CLAUSE else Metric.VALUE


@dataclass(frozen=True)
class FieldResult:
    doc_id: str
    field: str
    field_type: FieldType
    field_group: str
    metric: Metric
    counts: Counts
    slice: Slice | None = None


def _value_counts(spec: FieldSpec, pred: object, gold: object) -> Counts | None:
    match pred, gold:
        case DateField(), DateField():
            return matchers.value_date(pred, gold)
        case DurationField(), DurationField():
            return matchers.value_duration(pred, gold)
        case JurisdictionField(), JurisdictionField():
            return matchers.value_jurisdiction(pred, gold)
        case PartyListField(), PartyListField():
            return matchers.value_parties(pred, gold)
        case TextField(), TextField():
            return matchers.value_text(pred, gold)
    raise TypeError(f"{spec.name}: no value matcher for {type(pred).__name__}")


def _score_field(
    doc_id: str, spec: FieldSpec, pred: ContractFields, gold: ContractFields
) -> list[FieldResult]:
    p, g = field_of(pred, spec.name), field_of(gold, spec.name)
    base = (doc_id, spec.name, spec.field_type, spec.group.value)
    results = [
        FieldResult(
            *base,
            Metric.PRESENCE,
            matchers.presence(is_present(p), is_present(g)),
            phrasing_slice(spec, g.evidence),
        )
    ]
    if isinstance(p, ClauseField) and isinstance(g, ClauseField):
        results.append(FieldResult(*base, Metric.SPAN, matchers.spans(p, g)))
    elif (value := _value_counts(spec, p, g)) is not None:
        results.append(FieldResult(*base, Metric.VALUE, value))
    return results


def score_document(doc_id: str, pred: ContractFields, gold: ContractFields) -> list[FieldResult]:
    return [r for spec in FIELDS for r in _score_field(doc_id, spec, pred, gold)]


def score(
    predictions: dict[str, ContractFields], gold: dict[str, ContractFields]
) -> list[FieldResult]:
    """Score every gold contract. A missing prediction counts as "found nothing"."""
    empty = ContractFields()
    return [
        r
        for doc_id in sorted(gold)
        for r in score_document(doc_id, predictions.get(doc_id, empty), gold[doc_id])
    ]


# ── Aggregation ──────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class GroupScore:
    micro: Counts
    macro_f1: float | None
    fields: int

    @property
    def micro_f1(self) -> float | None:
        return self.micro.f1


def wants(result: FieldResult, metric: Metric | None) -> bool:
    """Select results for ``metric``, or each field's headline metric when ``metric`` is None."""
    return result.metric is (metric or headline_metric(result.field_type))


def per_field(results: Iterable[FieldResult], metric: Metric | None) -> dict[str, Counts]:
    totals: dict[str, Counts] = defaultdict(Counts)
    for r in results:
        if wants(r, metric):
            totals[r.field] += r.counts
    return dict(totals)


def aggregate(
    field_counts: dict[str, Counts], group_of: Callable[[str], str | None]
) -> dict[str, GroupScore]:
    """Roll per-field counts up into groups (field type, clause family, or one overall group)."""
    members: dict[str, list[str]] = defaultdict(list)
    for field in field_counts:
        if (group := group_of(field)) is not None:
            members[group].append(field)
    scores: dict[str, GroupScore] = {}
    for group, fields in members.items():
        micro = sum((field_counts[f] for f in fields), Counts())
        f1s = [f1 for f in fields if (f1 := field_counts[f].f1) is not None]
        scores[group] = GroupScore(micro, fmean(f1s) if f1s else None, len(fields))
    return scores


def slice_recall(results: Iterable[FieldResult]) -> dict[str, dict[Slice, Counts]]:
    """Presence counts per field, split into canonical / non-canonical gold phrasing."""
    out: dict[str, dict[Slice, Counts]] = defaultdict(lambda: defaultdict(Counts))
    for r in results:
        if r.metric is Metric.PRESENCE and r.slice is not None:
            out[r.field][r.slice] += r.counts
    return {field: dict(by_slice) for field, by_slice in out.items()}
