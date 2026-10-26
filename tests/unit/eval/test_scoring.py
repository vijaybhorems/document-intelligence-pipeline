"""Scorer, aggregation, bootstrap, slices, baselines and the run lifecycle."""

import json
from pathlib import Path

import pytest

from dip.eval.baselines import AllAbsent, KeywordBaseline
from dip.eval.bootstrap import bootstrap
from dip.eval.matchers import Counts
from dip.eval.report import render
from dip.eval.runs import load_meta, load_results, predict, score_run
from dip.eval.scorer import (
    FieldResult,
    Metric,
    aggregate,
    per_field,
    score,
    score_document,
    slice_recall,
)
from dip.eval.slices import Slice, phrasing_slice
from dip.schema.domain import (
    ClauseField,
    ContractFields,
    Evidence,
    GoldRecord,
    JurisdictionField,
)
from dip.schema.registry import FIELDS, FIELDS_BY_NAME, FieldType

TEXT = (
    "DISTRIBUTOR AGREEMENT\n\nThis Agreement is dated May 8, 2014 by and between Acme Corp. "
    '("Supplier") and Beta LLC ("Distributor"). This Agreement shall be governed by the laws of '
    "the State of New York. Distributor shall not assign this Agreement without consent. "
    "Supplier may audit the books of Distributor."
)


def _gold() -> ContractFields:
    return ContractFields(
        governing_law=JurisdictionField(
            values=["New York"], evidence=[Evidence(quote="governed by the laws of New York")]
        ),
        clauses=ContractFields().clauses.model_copy(
            update={
                "anti_assignment": ClauseField(
                    present=True,
                    evidence=[Evidence(quote="Distributor shall not assign this Agreement")],
                ),
                "non_compete": ClauseField(
                    present=True, evidence=[Evidence(quote="Supplier shall not sell elsewhere.")]
                ),
            }
        ),
    )


def _result(field: str, metric: Metric, counts: Counts, doc: str = "d1") -> FieldResult:
    spec = FIELDS_BY_NAME[field]
    return FieldResult(doc, field, spec.field_type, spec.group.value, metric, counts)


# ── score_document ───────────────────────────────────────────────────────────


def test_every_field_gets_presence_and_one_other_metric() -> None:
    results = score_document("d1", ContractFields(), _gold())

    by_field: dict[str, set[Metric]] = {}
    for r in results:
        by_field.setdefault(r.field, set()).add(r.metric)
    assert set(by_field) == {f.name for f in FIELDS}
    assert by_field["anti_assignment"] == {Metric.PRESENCE, Metric.SPAN}
    assert by_field["governing_law"] == {Metric.PRESENCE, Metric.VALUE}


def test_empty_prediction_misses_gold_positives() -> None:
    results = score_document("d1", ContractFields(), _gold())
    presence = per_field(results, Metric.PRESENCE)

    assert presence["anti_assignment"] == Counts(fn=1)
    assert presence["audit_rights"] == Counts(tn=1)


def test_missing_prediction_counts_as_empty() -> None:
    assert score({}, {"d1": _gold()}) == score({"d1": ContractFields()}, {"d1": _gold()})


# ── Aggregation ──────────────────────────────────────────────────────────────


def test_micro_pools_counts_and_macro_averages_f1() -> None:
    field_counts = {
        "anti_assignment": Counts(tp=9, fp=1),  # common, F1 = 18/19
        "source_code_escrow": Counts(fn=1),  # rare, F1 = 0
    }
    (group,) = aggregate(field_counts, lambda f: "clause").values()

    assert group.micro == Counts(tp=9, fp=1, fn=1)
    assert group.micro_f1 == pytest.approx(18 / 20)
    assert group.macro_f1 == pytest.approx((18 / 19 + 0.0) / 2)  # rare field drags macro down


def test_macro_skips_fields_with_nothing_to_score() -> None:
    (group,) = aggregate(
        {"anti_assignment": Counts(tp=1), "audit_rights": Counts(tn=3)}, lambda f: "g"
    ).values()

    assert group.macro_f1 == 1.0


def test_headline_metric_is_presence_for_clauses_value_for_typed() -> None:
    results = [
        _result("anti_assignment", Metric.PRESENCE, Counts(tp=1)),
        _result("anti_assignment", Metric.SPAN, Counts(fn=1)),
        _result("governing_law", Metric.PRESENCE, Counts(tp=1)),
        _result("governing_law", Metric.VALUE, Counts(fp=1, fn=1)),
    ]

    assert per_field(results, None) == {
        "anti_assignment": Counts(tp=1),
        "governing_law": Counts(fp=1, fn=1),
    }


# ── Bootstrap ────────────────────────────────────────────────────────────────


def _many_docs() -> list[FieldResult]:
    return [
        _result(
            "anti_assignment", Metric.PRESENCE, Counts(tp=1) if i % 4 else Counts(fn=1), f"d{i}"
        )
        for i in range(40)
    ]


def test_bootstrap_is_deterministic_and_brackets_the_point_estimate() -> None:
    results = _many_docs()
    point = aggregate(per_field(results, Metric.PRESENCE), lambda f: "all")["all"].micro_f1
    first = bootstrap(results, Metric.PRESENCE, lambda f: "all", iterations=200, seed=1)
    second = bootstrap(results, Metric.PRESENCE, lambda f: "all", iterations=200, seed=1)

    assert first == second
    interval = first["micro"]["all"]
    assert point is not None
    assert interval.low <= point <= interval.high
    assert interval.low < interval.high


# ── Slices ───────────────────────────────────────────────────────────────────


def test_phrasing_slice() -> None:
    spec = FIELDS_BY_NAME["change_of_control"]

    assert (
        phrasing_slice(spec, [Evidence(quote="upon a Change of Control of Licensee")])
        is Slice.CANONICAL
    )
    assert (
        phrasing_slice(spec, [Evidence(quote="if Licensee merges with a competitor")])
        is Slice.NON_CANONICAL
    )
    assert phrasing_slice(spec, []) is None
    assert phrasing_slice(FIELDS_BY_NAME["parties"], [Evidence(quote="Acme")]) is None  # no cues


def test_cues_match_word_prefixes_only() -> None:
    spec = FIELDS_BY_NAME["ip_ownership_assignment"]

    assert (
        phrasing_slice(spec, [Evidence(quote="Ownership of all work product")]) is Slice.CANONICAL
    )
    assert phrasing_slice(spec, [Evidence(quote="well-known techniques")]) is Slice.NON_CANONICAL


def test_slice_recall_groups_presence_by_slice() -> None:
    results = [
        FieldResult(
            "d1",
            "exclusivity",
            FieldType.CLAUSE,
            "g",
            Metric.PRESENCE,
            Counts(tp=1),
            Slice.CANONICAL,
        ),
        FieldResult(
            "d2",
            "exclusivity",
            FieldType.CLAUSE,
            "g",
            Metric.PRESENCE,
            Counts(fn=1),
            Slice.NON_CANONICAL,
        ),
    ]

    assert slice_recall(results) == {
        "exclusivity": {Slice.CANONICAL: Counts(tp=1), Slice.NON_CANONICAL: Counts(fn=1)}
    }


# ── Baselines ────────────────────────────────────────────────────────────────


def test_all_absent_predicts_nothing() -> None:
    assert AllAbsent().predict(TEXT) == ContractFields()


def test_keyword_baseline_on_a_small_contract() -> None:
    fields = KeywordBaseline().predict(TEXT)

    assert fields.document_name.value == "DISTRIBUTOR AGREEMENT"
    assert fields.governing_law.values == ["New York"]
    assert [d.year for d in fields.agreement_date.values] == [2014]
    assert [p.name for p in fields.parties.parties] == ["Acme Corp", "Beta LLC"]
    assert fields.clauses.anti_assignment.present
    assert fields.clauses.audit_rights.present
    assert not fields.clauses.source_code_escrow.present
    for evidence in fields.clauses.anti_assignment.evidence:
        assert evidence.char_start is not None
        assert TEXT[evidence.char_start : evidence.char_end] == evidence.quote


# ── Run lifecycle ────────────────────────────────────────────────────────────


@pytest.fixture
def data_dir(tmp_path: Path) -> Path:
    """A one-contract dataset laid out like data/."""
    (tmp_path / "raw" / "CUAD_v1" / "full_contract_txt").mkdir(parents=True)
    (tmp_path / "raw" / "CUAD_v1" / "full_contract_txt" / "d1.txt").write_text(TEXT)
    (tmp_path / "gold").mkdir()
    record = GoldRecord(
        doc_id="d1",
        title="d1",
        contract_type="Distributor",
        txt_path="d1.txt",
        pdf_path="x.pdf",
        text_sha256="0",
        text_chars=len(TEXT),
        fields=_gold(),
    )
    (tmp_path / "gold" / "d1.json").write_text(record.model_dump_json())
    (tmp_path / "splits.json").write_text(json.dumps({"splits": {"dev": ["d1"]}}))
    return tmp_path


def test_predict_score_report_round_trip(data_dir: Path, tmp_path: Path) -> None:
    run_dir = predict(KeywordBaseline(), "dev", data_dir, tmp_path / "runs")
    results = score_run(run_dir, data_dir)

    assert load_meta(run_dir).n_docs == 1
    assert sorted(load_results(run_dir), key=repr) == sorted(results, key=repr)
    presence = per_field(results, Metric.PRESENCE)
    assert presence["anti_assignment"] == Counts(tp=1)
    assert presence["non_compete"] == Counts(fn=1)

    text = render(load_meta(run_dir), results)
    assert "## Headline by field type" in text
    assert "`anti_assignment`" in text


def test_paired_delta_detects_a_consistent_improvement_and_not_noise() -> None:
    from dip.eval.bootstrap import paired_delta

    docs = [f"d{i}" for i in range(30)]
    worse = [_result("anti_assignment", Metric.PRESENCE, Counts(tp=1, fp=1), d) for d in docs]
    better = [_result("anti_assignment", Metric.PRESENCE, Counts(tp=1), d) for d in docs]

    up = paired_delta(worse, better, lambda _: "all", iterations=300)["all"]
    assert up.diff > 0
    assert up.significant  # every contract improved: the CI excludes zero

    same = paired_delta(worse, worse, lambda _: "all", iterations=300)["all"]
    assert same.diff == 0
    assert not same.significant
