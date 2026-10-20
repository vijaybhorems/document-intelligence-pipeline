"""Derived validation runs, including re-ask with a fake model."""

import json
from pathlib import Path
from typing import Any

import pytest

from dip.eval.derive import problems_for, validate_run
from dip.eval.runs import Prediction, load_meta, load_predictions, predict, score_run, spent_usd
from dip.eval.validation_metrics import ValidationMetrics
from dip.extract.system import SystemOutput, Usage
from dip.schema.domain import (
    ClauseField,
    ContractFields,
    Evidence,
    GoldRecord,
    ValidationIssue,
)
from dip.schema.llm import LLMClause
from dip.validate.validator import Policy

TEXT = "Licensee shall not assign this Agreement. Licensor may audit the books of Licensee."
HALLUCINATED = ClauseField(
    present=True, evidence=[Evidence(quote="Licensee waives all claims forever.")]
)
REAL = ClauseField(
    present=True, evidence=[Evidence(quote="Licensor may audit the books of Licensee.")]
)


class OneShotSystem:
    """Predicts a fixed set of fields, like a model that hallucinated one clause."""

    name = "fixed"

    def config(self) -> dict[str, Any]:
        return {"model": "gpt-5.6-luna"}

    def predict_all(
        self, texts: dict[str, str], max_cost_usd: float | None = None, on_usage: Any = None
    ) -> dict[str, SystemOutput]:
        clauses = ContractFields().clauses.model_copy(
            update={"covenant_not_to_sue": HALLUCINATED, "audit_rights": REAL}
        )
        return {
            d: SystemOutput(fields=ContractFields(clauses=clauses), usage=Usage(cost_usd=0.01))
            for d in texts
        }


class FakeReasker:
    """Stands in for OpenAIExtractor.reask: withdraws the hallucinated clause."""

    def __init__(self) -> None:
        self.asked: dict[str, dict[str, list[str]]] = {}

    def reask(
        self,
        texts: dict[str, str],
        problems: dict[str, dict[str, list[str]]],
        max_cost_usd: float | None = None,
        on_usage: Any = None,
    ) -> dict[str, Any]:
        self.asked = problems
        out = {}
        for doc_id, fields in problems.items():
            usage = Usage(calls=1, cost_usd=0.002)
            if on_usage:
                on_usage(usage)
            out[doc_id] = (
                {name: LLMClause(quotes=[], present=False) for name in fields},
                usage,
                [],
            )
        return out


@pytest.fixture
def data(tmp_path: Path) -> Path:
    data = tmp_path / "data"
    (data / "raw" / "CUAD_v1" / "full_contract_txt").mkdir(parents=True)
    (data / "raw" / "CUAD_v1" / "full_contract_txt" / "d1.txt").write_text(TEXT)
    (data / "gold").mkdir()
    gold = ContractFields(
        clauses=ContractFields().clauses.model_copy(update={"audit_rights": REAL})
    )
    record = GoldRecord(
        doc_id="d1",
        title="d1",
        contract_type="x",
        txt_path="d1.txt",
        pdf_path="x.pdf",
        text_sha256="0",
        text_chars=len(TEXT),
        fields=gold,
    )
    (data / "gold" / "d1.json").write_text(record.model_dump_json())
    (data / "splits.json").write_text(json.dumps({"splits": {"dev": ["d1"]}}))
    return data


def test_problems_for_maps_errors_and_extraction_issues_to_fields() -> None:
    prediction = Prediction(
        doc_id="d1",
        fields=ContractFields(
            clauses=ContractFields().clauses.model_copy(
                update={"covenant_not_to_sue": HALLUCINATED}
            )
        ),
        issues=["effective_date: unparseable date 'soon'"],
    )
    issues = [
        ValidationIssue(
            field="covenant_not_to_sue", code="unsupported_value", severity="error", message="x"
        )
    ]

    problems = problems_for(prediction, issues)

    assert set(problems) == {"covenant_not_to_sue", "effective_date"}
    assert "waives all claims" in problems["covenant_not_to_sue"][0]


def test_measure_separates_hallucinations_from_over_triggers(data: Path, tmp_path: Path) -> None:
    run = predict(OneShotSystem(), "dev", data, tmp_path / "runs")
    score_run(run, data)
    m = ValidationMetrics.model_validate_json((run / "validation.json").read_text())

    assert m.false_positives == 1  # covenant_not_to_sue
    assert m.false_positives_ungrounded == 1  # ...and its quote isn't in the text
    assert m.hallucination_rate == 1.0
    assert m.grounding_rate == 0.5


def test_validate_drop_is_free_and_removes_the_hallucination(data: Path, tmp_path: Path) -> None:
    runs = tmp_path / "runs"
    base = predict(OneShotSystem(), "dev", data, runs)
    derived = validate_run(base, data, runs, Policy.DROP)

    fields = load_predictions(derived)["d1"].fields
    assert not fields.clauses.covenant_not_to_sue.present
    assert fields.clauses.audit_rights.present
    meta = load_meta(derived)
    assert meta.derived_from == base.name
    assert spent_usd(runs) == pytest.approx(0.01)  # base run only; a derived run adds nothing


def test_reask_sends_only_failing_fields_and_records_spend(data: Path, tmp_path: Path) -> None:
    runs = tmp_path / "runs"
    base = predict(OneShotSystem(), "dev", data, runs)
    reasker = FakeReasker()
    derived = validate_run(base, data, runs, Policy.WARN, reasker)  # type: ignore[arg-type]

    assert reasker.asked == {
        "d1": {"covenant_not_to_sue": reasker.asked["d1"]["covenant_not_to_sue"]}
    }
    fields = load_predictions(derived)["d1"].fields
    assert not fields.clauses.covenant_not_to_sue.present  # model withdrew it
    assert fields.clauses.audit_rights.present  # untouched
    assert spent_usd(runs) == pytest.approx(0.01 + 0.002)  # base + re-ask, nothing double-counted
