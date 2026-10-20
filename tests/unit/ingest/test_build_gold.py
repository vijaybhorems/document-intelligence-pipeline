from pathlib import Path

import duckdb
import pytest

from dip.ingest.build_gold import gold_record, write_gold
from dip.ingest.cuad import CuadDocument
from dip.schema.domain import GoldRecord, PartialDate, Party
from dip.schema.registry import FIELDS

TEXT = (
    'LICENSE AGREEMENT dated May 8, 2014 between Acme Corp. ("Licensor") and Beta LLC '
    '("Licensee"). This Agreement is governed by the laws of the State of New York. '
    "Licensee may not assign this Agreement without consent."
)


def _span(quote: str) -> dict[str, int | str]:
    return {"text": quote, "answer_start": TEXT.index(quote)}


def _doc(tmp_path: Path, csv_overrides: dict[str, str] | None = None) -> CuadDocument:
    txt = tmp_path / "doc.txt"
    txt.write_text(TEXT, encoding="utf-8")
    csv_row = {f.csv_answer_column: "No" for f in FIELDS}
    csv_row |= {
        "Document Name-Answer": "LICENSE AGREEMENT",
        "Parties-Answer": 'Acme Corp. ("Licensor"); Beta LLC ("Licensee")',
        "Agreement Date-Answer": "5/8/14",
        "Effective Date-Answer": "None",
        "Expiration Date-Answer": "None",
        "Renewal Term-Answer": "successive 1 year",  # answer with no span -> label issue
        "Notice Period To Terminate Renewal- Answer": "None",
        "Governing Law-Answer": "New York",
        "Anti-Assignment-Answer": "Yes",
    }
    csv_row |= csv_overrides or {}
    return CuadDocument(
        doc_id="doc-1",
        title="doc",
        contract_type="License",
        text=TEXT,
        txt_path=txt,
        pdf_path=tmp_path / "Part_I" / "License_Agreements" / "doc.pdf",
        csv_row=csv_row,
        qas={
            "Document Name": [_span("LICENSE AGREEMENT")],
            "Parties": [_span("Acme Corp."), _span("Beta LLC")],
            "Agreement Date": [_span("May 8, 2014")],
            "Governing Law": [_span("governed by the laws of the State of New York")],
            "Anti-Assignment": [_span("Licensee may not assign this Agreement without consent.")],
        },
    )


def test_typed_values_come_from_normalized_csv_answers(tmp_path: Path) -> None:
    fields = gold_record(_doc(tmp_path)).fields

    assert fields.document_name.value == "LICENSE AGREEMENT"
    assert fields.agreement_date.values == [PartialDate(year=2014, month=5, day=8)]
    assert fields.governing_law.values == ["New York"]
    assert fields.parties.parties == [
        Party(name="Acme Corp.", aliases=["Licensor"]),
        Party(name="Beta LLC", aliases=["Licensee"]),
    ]


def test_evidence_offsets_point_into_the_text(tmp_path: Path) -> None:
    record = gold_record(_doc(tmp_path))

    for evidence in record.fields.governing_law.evidence + record.fields.parties.evidence:
        assert evidence.char_start is not None
        assert evidence.char_end is not None
        assert TEXT[evidence.char_start : evidence.char_end] == evidence.quote
        assert evidence.grounded is True


def test_clause_presence_comes_from_spans(tmp_path: Path) -> None:
    clauses = gold_record(_doc(tmp_path)).fields.clauses

    assert clauses.anti_assignment.present is True
    assert clauses.audit_rights.present is False


def test_records_label_issues_instead_of_hiding_them(tmp_path: Path) -> None:
    doc = _doc(tmp_path, {"Audit Rights-Answer": "Yes", "Agreement Date-Answer": "[]/[]/[]"})

    issues = {(i.field, i.kind) for i in gold_record(doc).label_issues}

    assert issues == {
        ("renewal_term", "answer_without_span"),
        ("audit_rights", "answer_without_span"),
        ("agreement_date", "unparsed_answer"),
    }


def test_detects_text_mismatch(tmp_path: Path) -> None:
    doc = _doc(tmp_path)
    doc.txt_path.write_text(TEXT + " changed", encoding="utf-8")

    assert ("*", "text_mismatch") in {(i.field, i.kind) for i in gold_record(doc).label_issues}


def test_write_gold_round_trips_and_writes_parquet(tmp_path: Path) -> None:
    record = gold_record(_doc(tmp_path))
    out = tmp_path / "gold"
    (out / "stale.json").parent.mkdir(parents=True)
    (out / "stale.json").write_text("{}")

    write_gold([record], out)

    assert not (out / "stale.json").exists()
    loaded = GoldRecord.model_validate_json((out / "doc-1.json").read_text())
    assert loaded == record
    rows = duckdb.sql(f"select count(*) from '{out}/gold_fields.parquet'").fetchone()
    assert rows == (len(FIELDS),)


@pytest.mark.parametrize("field", ["effective_date", "expiration_date"])
def test_absent_typed_fields_are_empty(tmp_path: Path, field: str) -> None:
    value = getattr(gold_record(_doc(tmp_path)).fields, field)

    assert (value.values, value.evidence, value.raw_text) == ([], [], None)
