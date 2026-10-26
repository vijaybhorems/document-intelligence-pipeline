"""The lake end to end, offline: records -> compaction -> Parquet -> named queries."""

import datetime as dt
import json
import os
import time
from pathlib import Path

import duckdb
import pytest
from fastapi.testclient import TestClient

from dip.analytics.lake import compact, push_evals
from dip.analytics.queries import Lake, QueryError
from dip.api.app import create_app
from dip.pipeline import TEXT
from dip.schema.domain import ContractRecord
from dip.service.backends import Services
from dip.service.blobs import LocalBlobStore
from dip.service.processing import record_key
from tests.unit.service.conftest import CONTRACT


def _store(blobs: LocalBlobStore, record: ContractRecord) -> None:
    key = record_key(record.record_id, record.created_at.isoformat())
    blobs.put(key, record.model_dump_json().encode(), "application/json")


def _records(services: Services, n: int, day: str = "2026-10-21") -> list[ContractRecord]:
    base = services.pipeline.process(CONTRACT.encode(), TEXT, lambda _: None)
    out = []
    for i in range(n):
        fields = base.fields.model_copy(deep=True)
        fields.document_name.value = ["Distributor Agreement", "Hosting Agreement"][i % 2]
        fields.governing_law.values = [["Texas"], ["New York"], []][i % 3]
        if i % 2:  # absent: no flag and no quote (presence = is_present, as in the scorer)
            fields.clauses.anti_assignment.present = False
            fields.clauses.anti_assignment.evidence = []
        out.append(
            base.model_copy(
                update={
                    "record_id": f"r{i}",
                    "document_sha256": f"sha{i}",
                    "created_at": dt.datetime.fromisoformat(f"{day}T10:00:0{i}+00:00"),
                    "fields": fields,
                }
            )
        )
    return out


@pytest.fixture
def lake(services: Services) -> Lake:
    blobs = services.blobs
    assert isinstance(blobs, LocalBlobStore)
    for record in _records(services, 4):
        _store(blobs, record)
    compact(blobs)
    return Lake(str(blobs.root.resolve() / "lake"), blobs)


def test_compaction_is_incremental(services: Services) -> None:
    blobs = services.blobs
    assert isinstance(blobs, LocalBlobStore)
    for record in [*_records(services, 2, "2026-10-20"), *_records(services, 1, "2026-10-21")]:
        _store(blobs, record)

    first = compact(blobs)
    again = compact(blobs)
    assert first.partitions_rebuilt == ["2026-10-20", "2026-10-21"]
    assert (again.partitions_rebuilt, again.partitions_current) == ([], 2)

    newer = _records(services, 3, "2026-10-21")[2]  # a new record lands in one day
    _store(blobs, newer)
    later = time.time() + 5  # mtime resolution: make "newer" unambiguous
    path = blobs.root / record_key(newer.record_id, newer.created_at.isoformat())
    os.utime(path, (later, later))
    assert compact(blobs).partitions_rebuilt == ["2026-10-21"]


def test_clause_prevalence_by_contract_type(lake: Lake) -> None:
    rows = lake.run("clause_prevalence", {}).rows
    anti = {r["contract_type"]: r for r in rows if r["clause"] == "anti_assignment"}
    # r0, r2 are Distributor with the clause; r1, r3 are Hosting without it.
    assert anti["Distributor"]["prevalence"] == 1.0
    assert anti["Hosting"]["prevalence"] == 0.0
    assert anti["Distributor"]["contracts"] == 2


def test_governing_law_distribution_counts_contracts_without_one(lake: Lake) -> None:
    rows = {r["governing_law"]: r["contracts"] for r in lake.run("governing_law", {}).rows}
    assert rows == {"Texas": 2, "New York": 1, "(not found)": 1}


def test_production_by_route(lake: Lake) -> None:
    (row,) = lake.run("production_by_route", {"days": "3650"}).rows
    assert (row["route"], row["records"]) == ("text", 4)


def test_queries_reject_bad_parameters(lake: Lake) -> None:
    with pytest.raises(QueryError, match="unknown"):
        lake.run("governing_law", {"sql": "DROP TABLE records"})
    with pytest.raises(QueryError, match="must be int"):
        lake.run("clause_prevalence", {"min_contracts": "1; DROP TABLE x"})
    with pytest.raises(QueryError, match="format"):
        lake.run("field_regressions", {"run_a": "x' OR 1=1 --", "run_b": "y"})
    with pytest.raises(KeyError):
        lake.run("select_star", {})


def test_a_query_cannot_read_outside_the_lake(lake: Lake, tmp_path: Path) -> None:
    secret = tmp_path / "secret.csv"
    secret.write_text("a\n1\n")
    with lake.connect() as con:
        with pytest.raises(duckdb.PermissionException):
            con.execute(f"SELECT * FROM read_csv('{secret}')")
        with pytest.raises(duckdb.Error):  # and the lock can't be lifted
            con.execute("SET enable_external_access = true")


def test_empty_lake_still_answers(services: Services) -> None:
    blobs = services.blobs
    assert isinstance(blobs, LocalBlobStore)
    lake = Lake(str(blobs.root.resolve() / "lake"), blobs)
    assert lake.run("governing_law", {}).rows == []
    assert lake.run("eval_by_route_model", {}).rows == []


RESULT_COLUMNS = "run_id, doc_id, field, field_type, field_group, metric, tp, fp, fn, tn, slice"


def _write_run(runs: Path, run_id: str, tp: int, fp: int) -> None:
    run = runs / run_id
    run.mkdir(parents=True)
    meta = {
        "run_id": run_id,
        "created_at": "2026-10-21T00:00:00Z",
        "system": "llm",
        "split": "dev",
        "n_docs": 2,
        "n_predicted": 2,
        "git_sha": "abc",
        "config": {"model": "gpt-5.6-luna", "route": "pypdf", "variant": "clean"},
        "usage": {"cost_usd": 0.02, "compute_usd": 0.0},
        "latency_p50_s": 10.0,
        "latency_p95_s": 12.0,
    }
    (run / "run.json").write_text(json.dumps(meta))
    rows = [
        (run_id, "d1", "anti_assignment", "clause", "general", "presence", tp, fp, 0, 0, None),
        (run_id, "d1", "anti_assignment", "clause", "general", "span", 0, 9, 9, 0, None),
        (run_id, "d1", "governing_law", "jurisdiction", "general", "value", 2, 0, 0, 0, None),
    ]
    con = duckdb.connect()
    con.execute(
        "CREATE TABLE t (run_id VARCHAR, doc_id VARCHAR, field VARCHAR, field_type VARCHAR, "
        "field_group VARCHAR, metric VARCHAR, tp INT, fp INT, fn INT, tn INT, slice VARCHAR)"
    )
    con.executemany(f"INSERT INTO t ({RESULT_COLUMNS}) VALUES ({', '.join('?' * 11)})", rows)
    con.execute(f"COPY t TO '{run}/field_results.parquet' (FORMAT parquet)")


def test_eval_runs_feed_quality_and_regression_queries(services: Services, tmp_path: Path) -> None:
    blobs = services.blobs
    assert isinstance(blobs, LocalBlobStore)
    runs = tmp_path / "runs"
    _write_run(runs, "20261021-000001-a-dev", tp=4, fp=0)
    _write_run(runs, "20261021-000002-b-dev", tp=2, fp=2)
    assert push_evals(runs, blobs) == (2, 2)
    assert push_evals(runs, blobs) == (2, 0)  # immutable results aren't re-uploaded
    lake = Lake(str(blobs.root.resolve() / "lake"), blobs)

    (quality,) = lake.run("eval_by_route_model", {"split": "dev"}).rows
    assert quality["runs"] == 2
    assert quality["route"] == "pypdf"
    # span rows are not headline: run a = 6/6 -> 100, run b = 4 tp, 2 fp -> 80; mean 90.
    assert quality["micro_f1"] == 90.0

    params = {"run_a": "20261021-000001-a-dev", "run_b": "20261021-000002-b-dev"}
    (regressed,) = lake.run("field_regressions", params).rows
    assert regressed["field"] == "anti_assignment"
    assert regressed["delta"] == -33.3


def test_analytics_endpoint(services: Services, lake: Lake) -> None:
    client = TestClient(create_app(services))
    listing = client.get("/v1/analytics").json()
    assert "clause_prevalence" in {q["name"] for q in listing["queries"]}

    body = client.get("/v1/analytics/governing_law").json()
    assert body["query"] == "governing_law"
    assert len(body["rows"]) == 3

    bad = client.get("/v1/analytics/clause_prevalence", params={"min_contracts": "x"})
    assert bad.status_code == 422
    assert bad.headers["content-type"] == "application/problem+json"
    assert client.get("/v1/analytics/nope").status_code == 404


def test_a_layout_change_rebuilds_every_partition(
    services: Services, monkeypatch: pytest.MonkeyPatch
) -> None:
    from dip.analytics import lake

    blobs = services.blobs
    assert isinstance(blobs, LocalBlobStore)
    for record in _records(services, 2):
        _store(blobs, record)
    compact(blobs)
    assert compact(blobs).partitions_rebuilt == []  # current: nothing to do

    monkeypatch.setattr(lake, "LAKE_VERSION", "99")  # the code's columns changed
    assert compact(blobs).partitions_rebuilt == ["2026-10-21"]
    assert compact(blobs).partitions_rebuilt == []  # and recorded
