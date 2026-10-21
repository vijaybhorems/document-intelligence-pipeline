"""Turn validation failures into re-ask feedback, and merge the answers back (decision D6)."""

from collections import defaultdict

from dip.schema.domain import ContractFields, ValidationIssue, field_of
from dip.schema.registry import FIELDS, FIELDS_BY_NAME, FieldGroup

_CALL_NAMES = {"all", *(g.value for g in FieldGroup)}


def problems_for(
    fields: ContractFields, extraction_issues: list[str], issues: list[ValidationIssue]
) -> dict[str, list[str]]:
    """Field -> feedback for everything worth re-asking: validation errors and L1/L2 issues."""
    problems: dict[str, list[str]] = defaultdict(list)
    for issue in issues:
        if issue.severity != "error":
            continue
        if issue.code == "unsupported_value":
            quotes = [e.quote[:200] for e in field_of(fields, issue.field).evidence]
            quoted = "; ".join(repr(q) for q in quotes) or "no quote"
            problems[issue.field].append(
                f"Your answer had no supporting text in the contract (you quoted: {quoted})."
            )
        elif issue.code in ("exception_without_restriction", "license_property_without_grant"):
            problems[issue.field].append(
                f"You marked this present, but {issue.message}. Check whether the contract "
                "really contains this clause."
            )
        elif issue.code == "date_order":
            for name in ("expiration_date", "effective_date", "agreement_date"):
                problems[name].append(f"Dates are inconsistent: {issue.message}.")
        else:
            problems[issue.field].append(issue.message)
    for raw in extraction_issues:
        target, _, message = raw.partition(":")
        if target in FIELDS_BY_NAME:
            problems[target].append(f"Your answer couldn't be used:{message}")
        elif target in _CALL_NAMES:  # a whole call failed (refusal, truncation, API error)
            for spec in FIELDS:
                if target in ("all", spec.group.value):
                    problems[spec.name].append("Your previous answer for this was missing.")
    return dict(problems)


def merge(base: ContractFields, fresh: ContractFields, fields: set[str]) -> ContractFields:
    """Replace ``fields`` in ``base`` with their re-asked values."""
    typed = {n: getattr(fresh, n) for n in fields if n in ContractFields.model_fields}
    clauses = {n: getattr(fresh.clauses, n) for n in fields if n not in ContractFields.model_fields}
    return base.model_copy(update={**typed, "clauses": base.clauses.model_copy(update=clauses)})
