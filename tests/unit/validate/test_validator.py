from dip.schema.domain import (
    ClauseField,
    ContractFields,
    DateField,
    Evidence,
    JurisdictionField,
    PartialDate,
    Party,
    PartyListField,
)
from dip.validate import rules
from dip.validate.validator import Policy, validate

TEXT = "Governed by the laws of Texas. The Licensee may sublicense to its Affiliates."


def _fields(**clauses: ClauseField) -> ContractFields:
    return ContractFields(
        governing_law=JurisdictionField(
            values=["Texas"], evidence=[Evidence(quote="Governed by the laws of Texas.")]
        ),
        parties=PartyListField(
            parties=[Party(name="Licensee"), Party(name="Licensor")],
            evidence=[Evidence(quote="The Licensee")],
        ),
        clauses=ContractFields().clauses.model_copy(update=clauses),
    )


def _clause(quote: str) -> ClauseField:
    return ClauseField(present=True, evidence=[Evidence(quote=quote)])


def test_grounded_values_pass_untouched_under_drop() -> None:
    result = validate(_fields(), TEXT, Policy.DROP)

    assert result.fields.governing_law.values == ["Texas"]
    assert result.fields.governing_law.evidence[0].grounded is True
    assert result.errors == []


def test_drop_removes_values_with_no_grounded_evidence() -> None:
    fields = _fields(audit_rights=_clause("Licensor may audit the books at any time."))

    result = validate(fields, TEXT, Policy.DROP)

    assert result.fields.clauses.audit_rights.present is False
    assert {(i.field, i.code) for i in result.issues} >= {
        ("audit_rights", "ungrounded_quote"),
        ("audit_rights", "unsupported_value"),
    }


def test_warn_keeps_the_value_but_flags_it() -> None:
    fields = _fields(audit_rights=_clause("Licensor may audit the books at any time."))

    result = validate(fields, TEXT, Policy.WARN)

    assert result.fields.clauses.audit_rights.present is True
    assert result.fields.clauses.audit_rights.evidence[0].grounded is False
    assert [i.code for i in result.errors] == ["unsupported_value"]


def test_rules_fire_on_dependent_clause_without_parent() -> None:
    fields = _fields(affiliate_license_licensee=_clause("may sublicense to its Affiliates"))

    issues = validate(fields, TEXT, Policy.WARN).issues

    assert ("affiliate_license_licensee", "license_property_without_grant") in {
        (i.field, i.code) for i in issues
    }


def test_enforce_rules_drops_the_dependent_clause() -> None:
    fields = _fields(affiliate_license_licensee=_clause("may sublicense to its Affiliates"))

    result = validate(fields, TEXT, Policy.WARN, enforce_rules=True)

    assert result.fields.clauses.affiliate_license_licensee.present is False
    assert result.fields.governing_law.values == ["Texas"]  # unrelated fields untouched


def test_date_order_rule() -> None:
    fields = ContractFields(
        agreement_date=DateField(values=[PartialDate(year=2020, month=1, day=1)]),
        expiration_date=DateField(values=[PartialDate(year=2019, month=1, day=1)]),
    )

    assert [i.code for i in rules.check(fields)] == ["date_order", "too_few_parties"]


def test_no_rule_fires_on_a_consistent_contract() -> None:
    assert rules.check(_fields()) == []
