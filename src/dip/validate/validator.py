"""Validation pass: ground evidence, apply rules, enforce a policy (SPEC §8, decisions D6/D7).

Layers (SPEC §8.1):
- L1 structural: strict Structured Outputs + extractor issues (refusal, truncation, nulls)
- L2 semantic: normalizer issues (unparseable dates, unknown jurisdictions)
- L3 grounding: ``dip.validate.grounding``
- L4 consistency: ``dip.validate.rules``

Policies (D7):
- ``warn``: keep every value; flag ungrounded quotes and unsupported values.
- ``drop``: remove ungrounded quotes; a value left with no grounded evidence is
  removed (a clause becomes absent, a typed field becomes empty).
"""

from dataclasses import dataclass
from enum import StrEnum

from dip.schema.domain import (
    ContractFields,
    Evidence,
    FieldValue,
    ValidationIssue,
    field_of,
    has_value,
)
from dip.schema.registry import FIELDS, FieldType
from dip.validate import rules
from dip.validate.grounding import DEFAULT_THRESHOLD, SourceText


class Policy(StrEnum):
    WARN = "warn"
    DROP = "drop"


@dataclass(frozen=True)
class Validated:
    fields: ContractFields
    issues: list[ValidationIssue]

    @property
    def errors(self) -> list[ValidationIssue]:
        return [i for i in self.issues if i.severity == "error"]


def _empty_like(field: FieldValue) -> FieldValue:
    return type(field)()


def _validate_field(
    name: str, field: FieldValue, source: SourceText, policy: Policy
) -> tuple[FieldValue, list[ValidationIssue]]:
    grounded: list[Evidence] = [source.ground(e) for e in field.evidence]
    issues: list[ValidationIssue] = []
    for e in grounded:
        if not e.grounded:
            issues.append(
                ValidationIssue(
                    field=name,
                    code="ungrounded_quote",
                    severity="warning",
                    message=f"not found in contract (score {e.match_score:.2f}): {e.quote[:120]!r}",
                )
            )
    supported = [e for e in grounded if e.grounded]
    if has_value(field) and not supported:
        issues.append(
            ValidationIssue(
                field=name,
                code="unsupported_value",
                severity="error",
                message="value has no evidence found in the contract",
            )
        )
        if policy is Policy.DROP:
            return _empty_like(field), issues
    kept = supported if policy is Policy.DROP else grounded
    return field.model_copy(update={"evidence": kept}), issues


def validate(
    fields: ContractFields,
    text: str | None,
    policy: Policy,
    threshold: float = DEFAULT_THRESHOLD,
    enforce_rules: bool = False,
) -> Validated:
    """Ground evidence, apply ``policy``, then check consistency rules.

    ``text=None`` means there is no source text to ground against (a scan read
    multimodally). Grounding is then *unavailable*: evidence keeps
    ``grounded=None`` rather than passing as grounded, and only the consistency
    rules run (SPEC §6.2).

    ``enforce_rules`` also drops dependent clauses that rules flag (for example a
    competitive-restriction exception with no restriction to be an exception to).
    """
    issues: list[ValidationIssue] = []
    if text is None:
        validated = fields
    else:
        source = SourceText(text, threshold)
        typed: dict[str, FieldValue] = {}
        clauses: dict[str, FieldValue] = {}
        for spec in FIELDS:
            new, field_issues = _validate_field(
                spec.name, field_of(fields, spec.name), source, policy
            )
            issues += field_issues
            (clauses if spec.field_type is FieldType.CLAUSE else typed)[spec.name] = new
        validated = ContractFields.model_validate(
            {**typed, "clauses": fields.clauses.model_validate(clauses)}
        )
    rule_issues = rules.check(validated)
    if enforce_rules:
        dropped = {i.field for i in rule_issues if i.code in rules.ENFORCEABLE}
        validated = validated.model_copy(
            update={
                "clauses": validated.clauses.model_copy(
                    update={name: type(getattr(validated.clauses, name))() for name in dropped}
                )
            }
        )
    return Validated(validated, issues + rule_issues)


def ground_all(
    fields: ContractFields, text: str, threshold: float = DEFAULT_THRESHOLD
) -> ContractFields:
    """Grounding only (no policy), for measuring an unvalidated run."""
    return validate(fields, text, Policy.WARN, threshold).fields
