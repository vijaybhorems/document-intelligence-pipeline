"""The registry and the domain schema must describe exactly the same fields."""

import pytest

from dip.schema.domain import ClauseSet, ContractFields, PartialDate
from dip.schema.registry import FIELDS, FIELDS_BY_NAME, FieldType, fields_of_type


def test_registry_has_all_41_cuad_categories_once() -> None:
    assert len(FIELDS) == 41
    assert len({f.name for f in FIELDS}) == 41
    assert len({f.cuad_category for f in FIELDS}) == 41


def test_field_type_counts_match_cuad() -> None:
    # CUAD README: 33 Yes/No categories, 8 with typed answers.
    assert len(fields_of_type(FieldType.CLAUSE)) == 33


def test_clause_set_matches_registry_clauses() -> None:
    assert set(ClauseSet.model_fields) == {f.name for f in fields_of_type(FieldType.CLAUSE)}


def test_contract_fields_match_registry_typed_fields() -> None:
    typed = {f.name for f in FIELDS if f.field_type is not FieldType.CLAUSE}

    assert set(ContractFields.model_fields) - {"clauses"} == typed


def test_notice_period_uses_cuads_misspelled_answer_column() -> None:
    spec = FIELDS_BY_NAME["notice_period_to_terminate_renewal"]

    assert spec.csv_answer_column == "Notice Period To Terminate Renewal- Answer"
    assert FIELDS_BY_NAME["governing_law"].csv_answer_column == "Governing Law-Answer"


def test_clause_family_only_for_clauses() -> None:
    assert FIELDS_BY_NAME["audit_rights"].clause_family is not None
    assert FIELDS_BY_NAME["governing_law"].clause_family is None


@pytest.mark.parametrize("kwargs", [{}, {"year": 2020, "month": 2, "day": 30}])
def test_partial_date_rejects_empty_or_impossible(kwargs: dict[str, int]) -> None:
    with pytest.raises(ValueError):  # noqa: PT011
        PartialDate(**kwargs)


def test_partial_date_complete_converts_to_date() -> None:
    assert PartialDate(year=2014, month=5, day=8).to_date() is not None
    assert PartialDate(year=2014).to_date() is None
