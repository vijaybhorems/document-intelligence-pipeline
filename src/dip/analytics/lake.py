"""The lake: JSON records compacted into Parquet tables that DuckDB queries (SPEC §9, ADR I5).

Records (``records/dt=…/{id}.json``) stay the source of truth. Compaction derives:

    lake/records/dt=YYYY-MM-DD/part-0.parquet         one row per record
    lake/record_fields/dt=YYYY-MM-DD/part-0.parquet   one row per (record, field)
    lake/eval/runs.parquet                            one row per eval run (``dip lake push-evals``)
    lake/eval/field_results/{run_id}.parquet          the scorer's per-field counts

Compaction is incremental by day: a partition is rebuilt only when a record in it is
newer than its Parquet file, so an hourly job reads only what changed. Partition
columns (``dt``) live in the path, not the files (hive partitioning).
"""

import datetime as dt
import json
import tempfile
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import structlog

from dip.analytics.contract_types import contract_type
from dip.schema.domain import (
    ClauseField,
    ContractRecord,
    DateField,
    DurationField,
    FieldValue,
    JurisdictionField,
    PartyListField,
    TextField,
    field_of,
    has_value,
    is_present,
)
from dip.schema.registry import FIELDS
from dip.service.blobs import BlobInfo, BlobStore

log = structlog.get_logger()

PARQUET = "application/vnd.apache.parquet"

# Column order and types are the tables' contract with analytics/queries; both read from here.
RECORDS: dict[str, str] = {
    "record_id": "VARCHAR",
    "document_sha256": "VARCHAR",
    "created_at": "TIMESTAMPTZ",
    "schema_version": "VARCHAR",
    "pipeline_version": "VARCHAR",
    "route": "VARCHAR",
    "model": "VARCHAR",
    "prompt_version": "VARCHAR",
    "pages": "INTEGER",
    "grounding": "VARCHAR",
    "input_tokens": "BIGINT",
    "output_tokens": "BIGINT",
    "cost_usd": "DOUBLE",
    "seconds": "DOUBLE",
    "document_name": "VARCHAR",
    "contract_type": "VARCHAR",
    "parties": "VARCHAR[]",
    "governing_law": "VARCHAR[]",
    "fields_present": "INTEGER",
    "clauses_present": "INTEGER",
    "validation_errors": "INTEGER",
    "validation_warnings": "INTEGER",
    "extraction_issues": "INTEGER",
    "ungrounded_quotes": "INTEGER",
}
RECORD_FIELDS: dict[str, str] = {
    "record_id": "VARCHAR",
    "field": "VARCHAR",
    "field_type": "VARCHAR",
    "clause_family": "VARCHAR",
    "present": "BOOLEAN",
    "has_value": "BOOLEAN",
    "value_text": "VARCHAR",
    "value_date": "DATE",
    "grounded": "BOOLEAN",  # all quotes found in the text; NULL if unchecked or no quotes
    "evidence_count": "INTEGER",
}
EVAL_RUNS: dict[str, str] = {
    "run_id": "VARCHAR",
    "created_at": "TIMESTAMPTZ",
    "system": "VARCHAR",
    "split": "VARCHAR",
    "n_docs": "INTEGER",
    "n_predicted": "INTEGER",
    "git_sha": "VARCHAR",
    "model": "VARCHAR",
    "strategy": "VARCHAR",
    "route": "VARCHAR",
    "variant": "VARCHAR",
    "prompt_version": "VARCHAR",
    "context": "VARCHAR",
    "reasoning_effort": "VARCHAR",
    "derived_from": "VARCHAR",
    "cost_usd": "DOUBLE",
    "compute_usd": "DOUBLE",
    "input_tokens": "BIGINT",
    "output_tokens": "BIGINT",
    "latency_p50_s": "DOUBLE",
    "latency_p95_s": "DOUBLE",
}
EVAL_FIELD_RESULTS: dict[str, str] = {
    "run_id": "VARCHAR",
    "doc_id": "VARCHAR",
    "field": "VARCHAR",
    "field_type": "VARCHAR",
    "field_group": "VARCHAR",
    "metric": "VARCHAR",
    "tp": "INTEGER",
    "fp": "INTEGER",
    "fn": "INTEGER",
    "tn": "INTEGER",
    "slice": "VARCHAR",
}


# ---------------------------------------------------------------- rows


def _value_text(value: FieldValue) -> str | None:
    match value:
        case TextField():
            return value.value
        case PartyListField():
            return "; ".join(p.name for p in value.parties) or None
        case DateField():
            parts = ["-".join(str(c) for c in (d.year, d.month, d.day) if c) for d in value.values]
            return "; ".join(["perpetual"] * value.perpetual + parts) or None
        case DurationField():
            parts = [f"{d.value:g} {d.unit.value}" for d in value.values]
            return "; ".join(["perpetual"] * value.perpetual + parts) or None
        case JurisdictionField():
            return "; ".join(value.values) or None
        case ClauseField():
            return None


def _grounded(value: FieldValue) -> bool | None:
    checks = [e.grounded for e in value.evidence if e.grounded is not None]
    return all(checks) if checks else None


def record_row(record: ContractRecord) -> dict[str, Any]:
    p, f = record.provenance, record.fields
    values = [field_of(f, spec.name) for spec in FIELDS]
    return {
        "record_id": record.record_id,
        "document_sha256": record.document_sha256,
        "created_at": record.created_at,
        "schema_version": record.schema_version,
        "pipeline_version": p.pipeline_version,
        "route": p.route,
        "model": p.model,
        "prompt_version": p.prompt_version,
        "pages": p.pages,
        "grounding": p.grounding,
        "input_tokens": p.input_tokens,
        "output_tokens": p.output_tokens,
        "cost_usd": p.cost_usd,
        "seconds": p.seconds,
        "document_name": f.document_name.value,
        "contract_type": contract_type(f.document_name.value),
        "parties": [party.name for party in f.parties.parties],
        "governing_law": list(f.governing_law.values),
        "fields_present": sum(is_present(v) for v in values),
        "clauses_present": sum(c.present for _, c in f.clauses),
        "validation_errors": sum(i.severity == "error" for i in record.validation_issues),
        "validation_warnings": sum(i.severity == "warning" for i in record.validation_issues),
        "extraction_issues": len(record.extraction_issues),
        "ungrounded_quotes": sum(e.grounded is False for v in values for e in v.evidence),
    }


def field_rows(record: ContractRecord) -> list[dict[str, Any]]:
    rows = []
    for spec in FIELDS:
        value = field_of(record.fields, spec.name)
        first_date = (
            next((d.to_date() for d in value.values if d.is_complete), None)
            if isinstance(value, DateField)
            else None
        )
        rows.append(
            {
                "record_id": record.record_id,
                "field": spec.name,
                "field_type": spec.field_type.value,
                "clause_family": spec.group.value,
                "present": is_present(value),
                "has_value": has_value(value),
                "value_text": _value_text(value),
                "value_date": first_date,
                "grounded": _grounded(value),
                "evidence_count": len(value.evidence),
            }
        )
    return rows


# ---------------------------------------------------------------- parquet


def _ddl(table: str, schema: dict[str, str]) -> str:
    return f"CREATE TABLE {table} ({', '.join(f'{c} {t}' for c, t in schema.items())})"


def to_parquet(rows: list[dict[str, Any]], schema: dict[str, str]) -> bytes:
    """Rows -> Parquet bytes with exactly ``schema`` (even for zero rows)."""
    import duckdb  # not at module level: the API imports this module, and startup is billed

    with tempfile.TemporaryDirectory() as tmp, duckdb.connect() as con:
        con.execute(_ddl("t", schema))
        if rows:
            placeholders = ", ".join("?" * len(schema))
            con.executemany(
                f"INSERT INTO t VALUES ({placeholders})",  # noqa: S608 - only "?" placeholders
                [[row.get(c) for c in schema] for row in rows],
            )
        out = Path(tmp) / "part-0.parquet"
        con.execute(f"COPY t TO '{out}' (FORMAT parquet, COMPRESSION zstd)")
        return out.read_bytes()


# ---------------------------------------------------------------- compaction


@dataclass
class CompactionReport:
    partitions_rebuilt: list[str] = field(default_factory=list)
    partitions_current: int = 0
    records: int = 0


def _partition(key: str) -> str | None:
    # records/dt=2026-10-21/<id>.json -> "2026-10-21"
    parts = key.split("/")
    if len(parts) == 3 and parts[1].startswith("dt=") and parts[2].endswith(".json"):
        return parts[1][3:]
    return None


def compact(blobs: BlobStore, force: bool = False) -> CompactionReport:
    """Rebuild every day partition whose records changed since it was last compacted."""
    by_day: dict[str, list[BlobInfo]] = defaultdict(list)
    for info in blobs.list("records/"):
        if (day := _partition(info.key)) is not None:
            by_day[day].append(info)
    built = {b.key: b.updated for b in blobs.list("lake/records/")}

    report = CompactionReport()
    for day, sources in sorted(by_day.items()):
        target = f"lake/records/dt={day}/part-0.parquet"
        newest = max(s.updated for s in sources)
        if not force and target in built and built[target] >= newest:
            report.partitions_current += 1
            continue
        records = [ContractRecord.model_validate_json(blobs.get(s.key)) for s in sources]
        # record_fields first: a reader that sees the new records file sees its fields too.
        blobs.put(
            f"lake/record_fields/dt={day}/part-0.parquet",
            to_parquet([row for r in records for row in field_rows(r)], RECORD_FIELDS),
            PARQUET,
        )
        blobs.put(target, to_parquet([record_row(r) for r in records], RECORDS), PARQUET)
        report.partitions_rebuilt.append(day)
        report.records += len(records)
        log.info("lake.partition_rebuilt", dt=day, records=len(records))
    return report


# ---------------------------------------------------------------- eval runs


def eval_run_row(run: dict[str, Any]) -> dict[str, Any]:
    config, usage = run.get("config", {}), run.get("usage", {})
    return {
        **{k: run.get(k) for k in ("run_id", "system", "split", "n_docs", "git_sha")},
        "created_at": dt.datetime.fromisoformat(run["created_at"]),
        "n_predicted": run.get("n_predicted", run.get("n_docs")),
        "derived_from": run.get("derived_from"),
        **{
            k: config.get(k)
            for k in ("model", "strategy", "route", "variant", "prompt_version", "context")
        },
        "reasoning_effort": config.get("reasoning_effort"),
        **{
            k: usage.get(k, 0) for k in ("cost_usd", "compute_usd", "input_tokens", "output_tokens")
        },
        "latency_p50_s": run.get("latency_p50_s"),
        "latency_p95_s": run.get("latency_p95_s"),
    }


def push_evals(runs_dir: Path, blobs: BlobStore) -> tuple[int, int]:
    """Publish local eval runs to the lake. Returns (runs in the table, new result files)."""
    rows, uploaded = [], 0
    existing = {b.key for b in blobs.list("lake/eval/field_results/")}
    for run_dir in sorted(p for p in runs_dir.iterdir() if (p / "run.json").exists()):
        results = run_dir / "field_results.parquet"
        if not results.exists():
            continue  # never scored
        run = json.loads((run_dir / "run.json").read_text())
        rows.append(eval_run_row(run))
        key = f"lake/eval/field_results/{run['run_id']}.parquet"
        if key not in existing:  # runs are immutable once scored
            blobs.put(key, results.read_bytes(), PARQUET)
            uploaded += 1
    blobs.put("lake/eval/runs.parquet", to_parquet(rows, EVAL_RUNS), PARQUET)
    return len(rows), uploaded
