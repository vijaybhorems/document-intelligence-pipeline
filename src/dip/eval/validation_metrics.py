"""Validation metrics for a run (SPEC §10.4).

- **grounding rate**: share of predicted quotes found in the contract.
- **unsupported values**: predicted values with no grounded evidence.
- **hallucination rate**: of the false positives (predicted present, gold absent),
  the share with no grounded evidence. The rest are **over-triggers**: real
  text, wrong legal reading (SPEC §10.8). The two need different fixes.
- **valid-output rate**: share of contracts with no L1/L2 issues (no refusal,
  truncation, null field or unparseable value).
"""

from collections import Counter

from pydantic import BaseModel

from dip.schema.domain import ContractFields, ValidationIssue, field_of, has_value, is_present
from dip.schema.registry import FIELDS
from dip.validate.validator import ground_all


class ValidationMetrics(BaseModel):
    contracts: int = 0
    contracts_valid: int = 0  # no L1/L2 issues
    quotes: int = 0
    quotes_grounded: int = 0
    values: int = 0  # predicted fields carrying a value
    values_unsupported: int = 0
    false_positives: int = 0
    false_positives_ungrounded: int = 0  # hallucinated
    true_positives_ungrounded: int = 0  # right answer, quote not found
    issues_by_code: dict[str, int] = {}

    @property
    def valid_output_rate(self) -> float | None:
        return self.contracts_valid / self.contracts if self.contracts else None

    @property
    def grounding_rate(self) -> float | None:
        return self.quotes_grounded / self.quotes if self.quotes else None

    @property
    def unsupported_rate(self) -> float | None:
        return self.values_unsupported / self.values if self.values else None

    @property
    def hallucination_rate(self) -> float | None:
        return (
            self.false_positives_ungrounded / self.false_positives if self.false_positives else None
        )


def measure(
    predictions: dict[str, ContractFields],
    gold: dict[str, ContractFields],
    texts: dict[str, str],
    extraction_issues: dict[str, list[str]],
    validation_issues: dict[str, list[ValidationIssue]] | None = None,
) -> ValidationMetrics:
    m = ValidationMetrics()
    codes: Counter[str] = Counter()
    for doc_id, gold_fields in gold.items():
        m.contracts += 1
        m.contracts_valid += not extraction_issues.get(doc_id)
        pred = predictions.get(doc_id)
        if pred is None:
            continue
        # Runs that went through validation already carry grounding; raw runs get it here.
        already = all(
            e.grounded is not None for s in FIELDS for e in field_of(pred, s.name).evidence
        )
        grounded = pred if already else ground_all(pred, texts[doc_id])
        for spec in FIELDS:
            p, g = field_of(grounded, spec.name), field_of(gold_fields, spec.name)
            m.quotes += len(p.evidence)
            supported = any(e.grounded for e in p.evidence)
            m.quotes_grounded += sum(bool(e.grounded) for e in p.evidence)
            if has_value(p):
                m.values += 1
                m.values_unsupported += not supported
            if is_present(p) and not is_present(g):
                m.false_positives += 1
                m.false_positives_ungrounded += not supported
            if is_present(p) and is_present(g) and not supported:
                m.true_positives_ungrounded += 1
        codes.update(i.code for i in (validation_issues or {}).get(doc_id, []))
    m.issues_by_code = dict(codes.most_common())
    return m
