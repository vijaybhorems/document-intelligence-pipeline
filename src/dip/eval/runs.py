"""Eval runs: predict on a split, score against gold, keep everything reproducible (SPEC §10.5).

Each run is a directory, so runs never overwrite each other and DuckDB can query
all of them at once (``data/runs/*/field_results.parquet``)::

    data/runs/{run_id}/
      run.json                  who/what/when: system, split, git SHA, config
      predictions/{doc_id}.json one ContractFields per contract
      field_results.parquet     one row per (contract, field, metric)
      report.md                 rendered by `dip report`
"""

import datetime as dt
import json
import subprocess
from pathlib import Path
from typing import Any

import duckdb
from pydantic import BaseModel

from dip.eval.baselines import System
from dip.eval.matchers import Counts
from dip.eval.scorer import FieldResult, Metric, score
from dip.eval.slices import Slice
from dip.ingest.splits import load_splits
from dip.schema.domain import SCHEMA_VERSION, ContractFields, GoldRecord
from dip.schema.registry import FieldType


class RunMeta(BaseModel):
    run_id: str
    created_at: dt.datetime
    system: str
    split: str
    n_docs: int
    git_sha: str
    git_dirty: bool
    schema_version: str = SCHEMA_VERSION
    config: dict[str, Any] = {}


class Prediction(BaseModel):
    doc_id: str
    fields: ContractFields


def git_state() -> tuple[str, bool]:
    """(short SHA, uncommitted changes?). Recorded so every number traces back to code."""
    try:
        sha = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],  # noqa: S607
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        dirty = bool(
            subprocess.run(
                ["git", "status", "--porcelain", "--untracked-files=no"],  # noqa: S607
                capture_output=True,
                text=True,
                check=True,
            ).stdout.strip()
        )
    except (OSError, subprocess.CalledProcessError):
        return "unknown", True
    return sha, dirty


def load_gold(data_dir: Path, split: str) -> dict[str, GoldRecord]:
    ids = load_splits(data_dir / "splits.json")[split]
    gold_dir = data_dir / "gold"
    return {
        doc_id: GoldRecord.model_validate_json((gold_dir / f"{doc_id}.json").read_text("utf-8"))
        for doc_id in ids
    }


def contract_text(data_dir: Path, record: GoldRecord) -> str:
    return (data_dir / "raw" / "CUAD_v1" / "full_contract_txt" / record.txt_path).read_text("utf-8")


def predict(system: System, split: str, data_dir: Path, runs_dir: Path) -> Path:
    gold = load_gold(data_dir, split)
    now = dt.datetime.now(dt.UTC)
    run_id = f"{now:%Y%m%d-%H%M%S}-{system.name}-{split}"
    run_dir = runs_dir / run_id
    (run_dir / "predictions").mkdir(parents=True)
    for doc_id, record in gold.items():
        fields = system.predict(contract_text(data_dir, record))
        (run_dir / "predictions" / f"{doc_id}.json").write_text(
            Prediction(doc_id=doc_id, fields=fields).model_dump_json(indent=2), "utf-8"
        )
    sha, dirty = git_state()
    meta = RunMeta(
        run_id=run_id,
        created_at=now,
        system=system.name,
        split=split,
        n_docs=len(gold),
        git_sha=sha,
        git_dirty=dirty,
    )
    (run_dir / "run.json").write_text(meta.model_dump_json(indent=2), "utf-8")
    return run_dir


def load_meta(run_dir: Path) -> RunMeta:
    return RunMeta.model_validate_json((run_dir / "run.json").read_text("utf-8"))


def load_predictions(run_dir: Path) -> dict[str, ContractFields]:
    return {
        path.stem: Prediction.model_validate_json(path.read_text("utf-8")).fields
        for path in sorted((run_dir / "predictions").glob("*.json"))
    }


def score_run(run_dir: Path, data_dir: Path) -> list[FieldResult]:
    meta = load_meta(run_dir)
    gold = {doc_id: r.fields for doc_id, r in load_gold(data_dir, meta.split).items()}
    results = score(load_predictions(run_dir), gold)
    write_results(results, meta.run_id, run_dir / "field_results.parquet")
    return results


_COLUMNS = (
    "run_id VARCHAR, doc_id VARCHAR, field VARCHAR, field_type VARCHAR, field_group VARCHAR, "
    "metric VARCHAR, tp INTEGER, fp INTEGER, fn INTEGER, tn INTEGER, slice VARCHAR"
)


def write_results(results: list[FieldResult], run_id: str, path: Path) -> None:
    con = duckdb.connect()
    con.execute(f"CREATE TABLE field_results ({_COLUMNS})")
    con.executemany(
        "INSERT INTO field_results VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        [
            (
                run_id,
                r.doc_id,
                r.field,
                r.field_type.value,
                r.field_group,
                r.metric.value,
                r.counts.tp,
                r.counts.fp,
                r.counts.fn,
                r.counts.tn,
                r.slice.value if r.slice else None,
            )
            for r in results
        ],
    )
    con.execute(f"COPY field_results TO '{path.as_posix()}' (FORMAT parquet)")


def load_results(run_dir: Path) -> list[FieldResult]:
    rows = (
        duckdb.connect()
        .execute(
            "SELECT doc_id, field, field_type, field_group, metric, tp, fp, fn, tn, slice "
            "FROM read_parquet(?)",
            [(run_dir / "field_results.parquet").as_posix()],
        )
        .fetchall()
    )
    return [
        FieldResult(
            doc_id=doc_id,
            field=field,
            field_type=FieldType(field_type),
            field_group=group,
            metric=Metric(metric),
            counts=Counts(tp, fp, fn, tn),
            slice=Slice(slice_) if slice_ else None,
        )
        for doc_id, field, field_type, group, metric, tp, fp, fn, tn, slice_ in rows
    ]


def summary(results: list[FieldResult]) -> dict[str, float | None]:
    """Headline micro F1 per field type, for quick CLI output."""
    from dip.eval.scorer import aggregate, per_field
    from dip.schema.registry import FIELDS_BY_NAME

    by_type = aggregate(per_field(results, None), lambda f: FIELDS_BY_NAME[f].field_type.value)
    return {group: score.micro_f1 for group, score in sorted(by_type.items())}


def dump_summary(results: list[FieldResult]) -> str:
    return json.dumps(
        {k: None if v is None else round(v, 3) for k, v in summary(results).items()}, indent=2
    )
