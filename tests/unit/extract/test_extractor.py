"""Extraction without the network: a fake client stands in for OpenAI (SPEC §17)."""

import json
import re
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest
from openai.lib._pydantic import to_strict_json_schema
from pydantic import BaseModel

from dip.eval.runs import load_meta, predict, spent_usd
from dip.extract.convert import parse_llm_date, to_domain
from dip.extract.estimate import estimate
from dip.extract.extractor import OpenAIExtractor, Strategy, call_plan
from dip.extract.pricing import UnknownModelPriceError, cost_usd
from dip.schema.domain import PartialDate, Party
from dip.schema.llm import (
    LLMClause,
    LLMDate,
    LLMDuration,
    LLMDurations,
    LLMDurationUnit,
    LLMJurisdictions,
    LLMParties,
    LLMParty,
    LLMText,
    output_model,
)
from dip.schema.registry import FIELDS, FieldType

MODEL = "gpt-5.6-luna"
TEXT = "Distributor shall not assign this Agreement. Governed by the laws of the State of Texas."

_EMPTY = {
    FieldType.CLAUSE: LLMClause(quotes=[], present=False),
    FieldType.TEXT: LLMText(quotes=[], value=None),
    FieldType.ENTITY_LIST: LLMParties(quotes=[], parties=[]),
    FieldType.DATE: LLMDate(quotes=[], dates=[], perpetual=False),
    FieldType.DURATION: LLMDurations(quotes=[], durations=[], perpetual=False),
    FieldType.JURISDICTION: LLMJurisdictions(quotes=[], jurisdictions=[]),
}
_SPEC = {f.name: f for f in FIELDS}


class FakeResponses:
    """Plays the part of ``client.responses``: returns scripted answers, records calls."""

    def __init__(
        self,
        answers: dict[str, Any],
        incomplete_first: bool = False,
        refuse: set[str] | None = None,
    ) -> None:
        self.answers = answers
        self.incomplete_first = incomplete_first
        self.refuse = refuse or set()
        self.calls: list[dict[str, Any]] = []

    async def parse(self, **kwargs: Any) -> SimpleNamespace:
        self.calls.append(kwargs)
        model_cls: type[BaseModel] = kwargs["text_format"]
        names = list(model_cls.model_fields)
        usage = SimpleNamespace(
            input_tokens=1000,
            input_tokens_details=SimpleNamespace(cached_tokens=800 if len(self.calls) > 1 else 0),
            output_tokens=100,
            output_tokens_details=SimpleNamespace(reasoning_tokens=40),
        )
        if self.incomplete_first and len(self.calls) == 1:
            return SimpleNamespace(
                status="incomplete",
                output_parsed=None,
                usage=usage,
                incomplete_details=SimpleNamespace(reason="max_output_tokens"),
            )
        requested = set(re.findall(r"^- (\w+):", kwargs["input"][2]["content"], re.MULTILINE))
        if self.refuse & requested:
            return SimpleNamespace(
                status="completed", output_parsed=None, usage=usage, incomplete_details=None
            )
        parsed = model_cls(
            **{
                n: self.answers[n] if n in self.answers else _EMPTY[_SPEC[n].field_type]
                for n in names
            }
        )
        return SimpleNamespace(
            status="completed", output_parsed=parsed, usage=usage, incomplete_details=None
        )


def _extractor(responses: FakeResponses, strategy: Strategy = Strategy.GROUPED) -> OpenAIExtractor:
    client: Any = SimpleNamespace(responses=responses)
    return OpenAIExtractor(MODEL, strategy=strategy, client=client, max_concurrency=4)


ANSWERS = {
    "anti_assignment": LLMClause(
        quotes=["Distributor shall not assign this Agreement."], present=True
    ),
    "governing_law": LLMJurisdictions(
        quotes=["laws of the State of Texas"], jurisdictions=["State of Texas"]
    ),
    "audit_rights": LLMClause(quotes=["something irrelevant"], present=False),
}


# ── Plans and schema ─────────────────────────────────────────────────────────


@pytest.mark.parametrize(("strategy", "calls"), [("single", 1), ("grouped", 6), ("per_field", 41)])
def test_call_plans_cover_every_field_exactly_once(strategy: str, calls: int) -> None:
    plan = call_plan(Strategy(strategy))

    assert len(plan) == calls
    names = [spec.name for _, specs in plan for spec in specs]
    assert sorted(names) == sorted(f.name for f in FIELDS)


def test_output_model_is_valid_for_strict_structured_outputs() -> None:
    model = output_model("All", list(FIELDS))
    schema = to_strict_json_schema(model)  # raises if not strict-compatible

    assert schema["additionalProperties"] is False
    assert set(schema["required"]) == {f.name for f in FIELDS}
    assert "governs" in json.dumps(schema)  # registry definitions become descriptions


def test_quotes_come_before_answers() -> None:
    assert next(iter(LLMClause.model_fields)) == "quotes"
    assert next(iter(LLMDate.model_fields)) == "quotes"


# ── Conversion ───────────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("2014-05-08", PartialDate(year=2014, month=5, day=8)),
        ("2014-05", PartialDate(year=2014, month=5)),
        ("2014", PartialDate(year=2014)),
        ("May 8, 2014", PartialDate(year=2014, month=5, day=8)),
        ("2014-02-30", None),
        ("unknown", None),
    ],
)
def test_parse_llm_date(text: str, expected: PartialDate | None) -> None:
    assert parse_llm_date(text) == expected


def test_to_domain_normalizes_like_gold() -> None:
    fields, issues = to_domain(
        {
            **ANSWERS,
            "parties": LLMParties(
                quotes=[], parties=[LLMParty(name=" Acme Corp. ", aliases=["Seller", " "])]
            ),
            "effective_date": LLMDate(quotes=["q"], dates=["2020-01-01", "soon"], perpetual=False),
            "renewal_term": LLMDurations(
                quotes=[],
                durations=[LLMDuration(value=1, unit=LLMDurationUnit.YEARS, successive=True)],
                perpetual=False,
            ),
        }
    )

    assert fields.governing_law.values == ["Texas"]  # canonicalized, as in gold
    assert fields.clauses.anti_assignment.present
    assert fields.clauses.audit_rights.evidence == []  # absent clause keeps no evidence
    assert fields.parties.parties == [Party(name="Acme Corp.", aliases=["Seller"])]
    assert fields.effective_date.values == [PartialDate(year=2020, month=1, day=1)]
    assert fields.renewal_term.values[0].successive
    assert issues == ["effective_date: unparseable date 'soon'"]


# ── Extractor ────────────────────────────────────────────────────────────────


def test_predict_all_grouped_end_to_end() -> None:
    responses = FakeResponses(ANSWERS)
    out = _extractor(responses).predict_all({"d1": TEXT})["d1"]

    assert out.fields.clauses.anti_assignment.present
    assert out.fields.governing_law.values == ["Texas"]
    assert out.usage.calls == 6
    assert out.usage.input_tokens == 6000
    assert out.usage.cached_tokens == 5 * 800
    assert out.usage.cost_usd == pytest.approx(cost_usd(MODEL, 6000, 4000, 600))
    assert out.issues == []


def test_every_call_shares_the_cacheable_prefix() -> None:
    """OpenAI caches [schema + system + contract]; all three must match across calls."""
    responses = FakeResponses(ANSWERS)
    _extractor(responses).predict_all({"d1": TEXT})

    prefixes = {json.dumps(c["input"][:2]) for c in responses.calls}
    assert len(prefixes) == 1  # system + contract identical across calls
    assert len({c["text_format"] for c in responses.calls}) == 1  # one shared schema
    assert len({c["prompt_cache_key"] for c in responses.calls}) == 1
    assert all(c["store"] is False for c in responses.calls)


def test_own_schema_variant_sends_a_schema_per_call() -> None:
    responses = FakeResponses(ANSWERS)
    client: Any = SimpleNamespace(responses=responses)
    extractor = OpenAIExtractor(MODEL, client=client, shared_schema=False)
    out = extractor.predict_all({"d1": TEXT})["d1"]

    assert len({c["text_format"] for c in responses.calls}) == 6
    assert "-own_schema" in extractor.name
    assert out.fields.governing_law.values == ["Texas"]


def test_requested_field_returned_null_is_an_issue() -> None:
    responses = FakeResponses({**ANSWERS, "governing_law": None})
    out = _extractor(responses).predict_all({"d1": TEXT})["d1"]

    assert out.fields.governing_law.values == []
    assert any("returned null for governing_law" in i for i in out.issues)


def test_truncated_output_is_retried_with_more_room() -> None:
    responses = FakeResponses(ANSWERS, incomplete_first=True)
    out = _extractor(responses, Strategy.PER_FIELD).predict_all({"d1": TEXT})["d1"]

    first, retry = responses.calls[0], responses.calls[1]
    assert retry["max_output_tokens"] == 2 * first["max_output_tokens"]
    assert retry["text_format"] is first["text_format"]  # same call, more room
    assert out.fields.clauses.anti_assignment.present
    assert out.usage.calls == 42  # 41 calls + 1 retry, all paid for


def test_no_pointless_retry_when_already_at_the_cap() -> None:
    responses = FakeResponses(ANSWERS, incomplete_first=True)
    out = _extractor(responses, Strategy.SINGLE).predict_all({"d1": TEXT})["d1"]

    assert len(responses.calls) == 1
    assert out.issues == ["all: output truncated at 32000 tokens"]


def test_refusal_becomes_an_issue_not_a_crash() -> None:
    responses = FakeResponses(ANSWERS, refuse={"anti_assignment"})
    out = _extractor(responses).predict_all({"d1": TEXT})["d1"]

    assert not out.fields.clauses.anti_assignment.present
    assert out.fields.governing_law.values == ["Texas"]  # other groups still land
    assert any("no parsed output" in issue for issue in out.issues)


def test_budget_cap_stops_new_contracts() -> None:
    responses = FakeResponses(ANSWERS)
    outputs = _extractor(responses).predict_all({"d1": TEXT, "d2": TEXT}, max_cost_usd=0.0)

    assert outputs == {}
    assert responses.calls == []


def test_unknown_model_fails_before_spending() -> None:
    with pytest.raises(UnknownModelPriceError):
        OpenAIExtractor("gpt-unpriced")


# ── Estimate, runs and the spend ledger ──────────────────────────────────────


def test_estimate_counts_calls_and_caching() -> None:
    extractor = _extractor(FakeResponses({}))
    est = estimate(extractor, {"d1": TEXT, "d2": TEXT})

    assert est.calls == 12
    assert est.cost_with_cache_usd < est.cost_no_cache_usd
    assert est.cacheable_tokens > 0


def test_llm_run_records_usage_and_ledger(tmp_path: Path) -> None:
    data = tmp_path / "data"
    (data / "raw" / "CUAD_v1" / "full_contract_txt").mkdir(parents=True)
    (data / "raw" / "CUAD_v1" / "full_contract_txt" / "d1.txt").write_text(TEXT)
    (data / "gold").mkdir()
    from dip.schema.domain import ContractFields, GoldRecord

    record = GoldRecord(
        doc_id="d1",
        title="d1",
        contract_type="x",
        txt_path="d1.txt",
        pdf_path="x.pdf",
        text_sha256="0",
        text_chars=len(TEXT),
        fields=ContractFields(),
    )
    (data / "gold" / "d1.json").write_text(record.model_dump_json())
    (data / "splits.json").write_text(json.dumps({"splits": {"dev": ["d1"]}}))

    run_dir = predict(_extractor(FakeResponses(ANSWERS)), "dev", data, tmp_path / "runs")
    meta = load_meta(run_dir)

    assert meta.complete
    assert meta.config["strategy"] == "grouped"
    assert meta.usage.calls == 6
    assert spent_usd(tmp_path / "runs") == pytest.approx(meta.usage.cost_usd)


class ExplodingResponses(FakeResponses):
    """Raises a non-API exception for one group, like an unexpected SDK parsing error."""

    async def parse(self, **kwargs: Any) -> SimpleNamespace:
        if "- governing_law:" in kwargs["input"][2]["content"]:
            raise ValueError("unexpected response shape")
        return await super().parse(**kwargs)


def test_unexpected_exception_is_contained_to_its_call() -> None:
    out = _extractor(ExplodingResponses(ANSWERS)).predict_all({"d1": TEXT})["d1"]

    assert out.fields.clauses.anti_assignment.present  # other groups still land
    assert any("ValueError: unexpected response shape" in i for i in out.issues)


def test_every_paid_call_is_reported_as_it_happens() -> None:
    seen: list[float] = []
    out = _extractor(FakeResponses(ANSWERS)).predict_all(
        {"d1": TEXT}, on_usage=lambda u: seen.append(u.cost_usd)
    )["d1"]

    assert len(seen) == 6
    assert sum(seen) == pytest.approx(out.usage.cost_usd)


def test_spend_ledger_survives_a_run_without_run_json(tmp_path: Path) -> None:
    from dip.eval.runs import USAGE_LEDGER
    from dip.extract.system import Usage

    crashed = tmp_path / "runs" / "crashed-run"
    crashed.mkdir(parents=True)
    (crashed / USAGE_LEDGER).write_text(
        Usage(calls=1, cost_usd=0.25).model_dump_json()
        + "\n"
        + Usage(cost_usd=0.5).model_dump_json()
        + "\n"
    )

    assert spent_usd(tmp_path / "runs") == pytest.approx(0.75)


def test_contract_span_records_cost_and_strategy() -> None:
    from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

    from dip.observability import tracing

    exporter = InMemorySpanExporter()
    provider = tracing.configure_tracing(None, exporter=exporter)
    assert provider is not None
    try:
        _extractor(FakeResponses(ANSWERS)).predict_all({"d1": TEXT})
        provider.force_flush()
        (span,) = [s for s in exporter.get_finished_spans() if s.name == "extract.contract"]
    finally:
        tracing.shutdown_tracing()

    assert span.attributes is not None
    assert span.attributes["dip.strategy"] == "grouped"
    assert span.attributes["dip.calls"] == 6
    assert span.attributes["dip.cost_usd"] == pytest.approx(cost_usd(MODEL, 6000, 4000, 600))


def test_tracing_is_off_without_an_endpoint() -> None:
    from dip.observability.tracing import configure_tracing

    assert configure_tracing(None) is None
