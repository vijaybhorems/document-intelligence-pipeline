"""Consistency rules (SPEC §8.1, layer L4).

Severity means "worth asking the model again" (D6): errors are re-asked,
warnings are only reported.

Every rule here was run against the 510 gold contracts first: a rule that fires
on expert labels is a false alarm. "Cap On Liability and Uncapped Liability both
present" was proposed in the spec and dropped, because 21.8% of gold contracts
legitimately have both (a cap with carve-outs). Gold fire rates are noted on
each rule.
"""

from collections.abc import Callable
from typing import Literal

from dip.schema.domain import ContractFields, Duration, DurationUnit, ValidationIssue

Rule = Callable[[ContractFields], list[ValidationIssue]]

_DAYS = {
    DurationUnit.DAYS: 1,
    DurationUnit.WEEKS: 7,
    DurationUnit.MONTHS: 30,
    DurationUnit.YEARS: 365,
}
MAX_PLAUSIBLE_YEARS = 50


def _issue(
    field: str, code: str, severity: Literal["error", "warning"], message: str
) -> ValidationIssue:
    return ValidationIssue(field=field, code=code, severity=severity, message=message)


def expiration_before_start(f: ContractFields) -> list[ValidationIssue]:
    """Gold: 0.4%. Expiry can't precede the agreement/effective date."""
    expiries = [d.to_date() for d in f.expiration_date.values]
    starts = [d.to_date() for d in f.effective_date.values + f.agreement_date.values]
    expiries_known = [d for d in expiries if d]
    starts_known = [d for d in starts if d]
    if expiries_known and starts_known and max(expiries_known) < min(starts_known):
        return [
            _issue(
                "expiration_date",
                "date_order",
                "error",
                f"expiration {max(expiries_known)} is before the start date {min(starts_known)}",
            )
        ]
    return []


def implausible_duration(f: ContractFields) -> list[ValidationIssue]:
    """Gold: 0%. Renewal or notice periods over 50 years are almost certainly misreads."""
    issues = []
    for name, field in (
        ("renewal_term", f.renewal_term),
        ("notice_period_to_terminate_renewal", f.notice_period_to_terminate_renewal),
    ):
        long: list[Duration] = [
            d for d in field.values if d.value * _DAYS[d.unit] > 365 * MAX_PLAUSIBLE_YEARS
        ]
        if long:
            issues.append(
                _issue(name, "implausible_duration", "error", f"{long[0].value} {long[0].unit}")
            )
    return issues


def too_few_parties(f: ContractFields) -> list[ValidationIssue]:
    """Gold: 3.3% (unsigned templates, single-filer exhibits), hence only a warning."""
    if len(f.parties.parties) < 2:
        return [_issue("parties", "too_few_parties", "warning", f"{len(f.parties.parties)} found")]
    return []


def license_property_without_grant(f: ContractFields) -> list[ValidationIssue]:
    """Gold: 1.2%. A license can't be non-transferable or irrevocable if none is granted.

    An error, not a warning: on Phase 3 dev predictions the flagged clause was a
    false positive every time it fired (1/1).
    """
    c = f.clauses
    implied = {
        "non_transferable_license": c.non_transferable_license.present,
        "irrevocable_or_perpetual_license": c.irrevocable_or_perpetual_license.present,
        "unlimited_all_you_can_eat_license": c.unlimited_all_you_can_eat_license.present,
        "affiliate_license_licensee": c.affiliate_license_licensee.present,
    }
    if c.license_grant.present:
        return []
    return [
        _issue(name, "license_property_without_grant", "error", "no License Grant found")
        for name, present in implied.items()
        if present
    ]


def exception_without_restriction(f: ContractFields) -> list[ValidationIssue]:
    """Gold: 0.4%. An exception to a competitive restriction needs a restriction.

    An error: on Phase 3 dev predictions the flagged clause was a false positive 5/6 times.
    """
    c = f.clauses
    restricted = c.non_compete.present or c.exclusivity.present or c.no_solicit_of_customers.present
    if c.competitive_restriction_exception.present and not restricted:
        return [
            _issue(
                "competitive_restriction_exception",
                "exception_without_restriction",
                "error",
                "no Non-Compete, Exclusivity or No-Solicit of Customers found",
            )
        ]
    return []


def notice_without_renewal(f: ContractFields) -> list[ValidationIssue]:
    """Gold: 0.4%. A notice period to stop renewal implies a renewal term."""
    renewal = f.renewal_term
    has_renewal = bool(renewal.values or renewal.perpetual or renewal.evidence)
    if f.notice_period_to_terminate_renewal.values and not has_renewal:
        return [
            _issue(
                "notice_period_to_terminate_renewal",
                "notice_without_renewal",
                "warning",
                "no Renewal Term found",
            )
        ]
    return []


# Rules whose flagged field can be dropped outright under ``enforce_rules``: a
# dependent clause predicted without the clause it depends on.
ENFORCEABLE = frozenset({"exception_without_restriction", "license_property_without_grant"})

RULES: tuple[Rule, ...] = (
    expiration_before_start,
    implausible_duration,
    too_few_parties,
    license_property_without_grant,
    exception_without_restriction,
    notice_without_renewal,
)


def check(fields: ContractFields) -> list[ValidationIssue]:
    return [issue for rule in RULES for issue in rule(fields)]
