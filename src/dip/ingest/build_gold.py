"""Convert CUAD's labels into gold ``GoldRecord``s in the domain schema (SPEC §10.10).

Sources, per field type:
- Evidence spans for every field come from ``CUAD_v1.json`` (exact char offsets).
- Typed values (dates, durations, jurisdictions, parties, document name) come
  from the normalized ``-Answer`` columns of ``master_clauses.csv``.
- Clause presence is "at least one labelled span"; the CSV's Yes/No is only
  used to detect disagreements, which are recorded as ``LabelIssue``s.

Nothing ambiguous is silently dropped: anything the normalizers can't parse
stays in ``raw_text`` and is listed in ``label_issues``.
"""

import hashlib
import json
from collections.abc import Iterable
from pathlib import Path

import duckdb

from dip.ingest.cuad import CuadDocument
from dip.schema.domain import (
    ClauseField,
    ClauseSet,
    ContractFields,
    DateField,
    DurationField,
    Evidence,
    GoldRecord,
    JurisdictionField,
    LabelIssue,
    PartyListField,
    TextField,
    field_of,
    is_present,
)
from dip.schema.registry import FIELDS, FieldSpec, FieldType
from dip.validate.normalize import (
    parse_cuad_dates,
    parse_cuad_parties,
    parse_durations,
    parse_jurisdictions,
)

TypedField = TextField | PartyListField | DateField | DurationField | JurisdictionField


def _evidence(answers: Iterable[dict[str, int | str]]) -> list[Evidence]:
    spans = {(int(a["answer_start"]), str(a["text"])) for a in answers}
    return [
        Evidence(
            quote=text,
            char_start=start,
            char_end=start + len(text),
            grounded=True,
            match_score=1.0,
        )
        for start, text in sorted(spans)
    ]


def _csv_answer(doc: CuadDocument, spec: FieldSpec) -> str | None:
    raw = (doc.csv_row.get(spec.csv_answer_column) or "").strip()
    return None if raw in ("", "None") else raw


def _typed_field(
    spec: FieldSpec, raw: str | None, evidence: list[Evidence], issues: list[LabelIssue]
) -> TypedField:
    unparsed: list[str] = []
    field: TypedField
    match spec.field_type:
        case FieldType.TEXT:
            field = TextField(value=raw, evidence=evidence)
        case FieldType.ENTITY_LIST:
            parties = parse_cuad_parties(raw)
            unparsed = parties.unparsed
            field = PartyListField(parties=parties.values, raw_text=raw, evidence=evidence)
        case FieldType.DATE:
            dates = parse_cuad_dates(raw)
            unparsed = dates.unparsed
            field = DateField(
                values=dates.values, perpetual=dates.perpetual, raw_text=raw, evidence=evidence
            )
        case FieldType.DURATION:
            durations = parse_durations(raw)
            unparsed = durations.unparsed
            field = DurationField(
                values=durations.values,
                perpetual=durations.perpetual,
                raw_text=raw,
                evidence=evidence,
            )
        case FieldType.JURISDICTION:
            laws = parse_jurisdictions(raw)
            unparsed = laws.unparsed
            field = JurisdictionField(values=laws.values, raw_text=raw, evidence=evidence)
        case FieldType.CLAUSE:
            raise ValueError(f"{spec.name} is a clause, not a typed field")

    if unparsed:
        issues.append(
            LabelIssue(field=spec.name, kind="unparsed_answer", detail="; ".join(unparsed))
        )
    if raw and not evidence:
        issues.append(LabelIssue(field=spec.name, kind="answer_without_span", detail=raw))
    if evidence and not raw:
        issues.append(
            LabelIssue(field=spec.name, kind="span_without_answer", detail=evidence[0].quote[:200])
        )
    return field


def _clause_field(
    spec: FieldSpec, raw: str | None, evidence: list[Evidence], issues: list[LabelIssue]
) -> ClauseField:
    csv_says_yes = raw is not None and raw.lower() == "yes"
    if csv_says_yes and not evidence:
        issues.append(LabelIssue(field=spec.name, kind="answer_without_span", detail="Yes"))
    if evidence and not csv_says_yes:
        issues.append(
            LabelIssue(field=spec.name, kind="span_without_answer", detail=evidence[0].quote[:200])
        )
    return ClauseField(present=bool(evidence), evidence=evidence)


def gold_record(doc: CuadDocument) -> GoldRecord:
    issues: list[LabelIssue] = []
    if doc.text != doc.txt_path.read_text(encoding="utf-8"):
        issues.append(LabelIssue(field="*", kind="text_mismatch", detail=str(doc.txt_path.name)))

    typed: dict[str, TypedField] = {}
    clauses: dict[str, ClauseField] = {}
    for spec in FIELDS:
        evidence = _evidence(doc.qas.get(spec.cuad_category, []))
        raw = _csv_answer(doc, spec)
        if spec.field_type is FieldType.CLAUSE:
            clauses[spec.name] = _clause_field(spec, raw, evidence, issues)
        else:
            typed[spec.name] = _typed_field(spec, raw, evidence, issues)

    return GoldRecord(
        doc_id=doc.doc_id,
        title=doc.title,
        contract_type=doc.contract_type,
        txt_path=doc.txt_path.name,
        pdf_path=str(
            Path(doc.pdf_path.parent.parent.name, doc.pdf_path.parent.name, doc.pdf_path.name)
        ),
        text_sha256=hashlib.sha256(doc.text.encode("utf-8")).hexdigest(),
        text_chars=len(doc.text),
        fields=ContractFields.model_validate({**typed, "clauses": ClauseSet(**clauses)}),
        label_issues=issues,
    )


# ── Output ───────────────────────────────────────────────────────────────────


def present_fields(record: GoldRecord) -> frozenset[str]:
    return frozenset(spec.name for spec in FIELDS if is_present(field_of(record.fields, spec.name)))


def _field_rows(record: GoldRecord) -> list[tuple[object, ...]]:
    """Long format: one row per (contract, field), for DuckDB analysis."""
    rows: list[tuple[object, ...]] = []
    for spec in FIELDS:
        value_json = raw = None
        if spec.field_type is FieldType.CLAUSE:
            field = getattr(record.fields.clauses, spec.name)
        else:
            field = getattr(record.fields, spec.name)
            value = field.model_dump(mode="json", exclude={"evidence", "raw_text"})
            value_json = json.dumps(value, sort_keys=True)
            raw = getattr(field, "raw_text", None) or getattr(field, "value", None)
        rows.append(
            (
                record.doc_id,
                record.contract_type,
                spec.name,
                spec.field_type.value,
                spec.group.value,
                is_present(field),
                len(field.evidence),
                sum(len(e.quote) for e in field.evidence),
                raw,
                value_json,
            )
        )
    return rows


def write_gold(records: list[GoldRecord], out_dir: Path) -> None:
    """Write ``{doc_id}.json`` per contract plus Parquet tables for analysis."""
    out_dir.mkdir(parents=True, exist_ok=True)
    keep = {f"{r.doc_id}.json" for r in records}
    for stale in out_dir.glob("*.json"):
        if stale.name not in keep:
            stale.unlink()
    for record in records:
        (out_dir / f"{record.doc_id}.json").write_text(
            record.model_dump_json(indent=2) + "\n", encoding="utf-8"
        )

    con = duckdb.connect()
    con.execute(
        """CREATE TABLE gold_fields (
            doc_id VARCHAR, contract_type VARCHAR, field VARCHAR, field_type VARCHAR,
            field_group VARCHAR, present BOOLEAN, n_spans INTEGER, span_chars INTEGER,
            raw_answer VARCHAR, value_json VARCHAR)"""
    )
    con.executemany(
        "INSERT INTO gold_fields VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        [row for r in records for row in _field_rows(r)],
    )
    con.execute(
        """CREATE TABLE documents (doc_id VARCHAR, title VARCHAR, contract_type VARCHAR,
            text_chars INTEGER, pdf_path VARCHAR, n_label_issues INTEGER)"""
    )
    con.executemany(
        "INSERT INTO documents VALUES (?, ?, ?, ?, ?, ?)",
        [
            (r.doc_id, r.title, r.contract_type, r.text_chars, r.pdf_path, len(r.label_issues))
            for r in records
        ],
    )
    con.execute(
        "CREATE TABLE label_issues (doc_id VARCHAR, field VARCHAR, kind VARCHAR, detail VARCHAR)"
    )
    con.executemany(
        "INSERT INTO label_issues VALUES (?, ?, ?, ?)",
        [(r.doc_id, i.field, i.kind, i.detail) for r in records for i in r.label_issues],
    )
    for table in ("gold_fields", "documents", "label_issues"):
        target = (out_dir / f"{table}.parquet").as_posix()
        con.execute(f"COPY {table} TO '{target}' (FORMAT parquet)")
