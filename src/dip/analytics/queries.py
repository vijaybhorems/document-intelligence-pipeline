"""Named analytics queries over the lake (SPEC §9.3), served by ``GET /v1/analytics/{name}``.

The API never accepts SQL. A caller picks a query by name and passes parameters that
are type- and range-checked here, then bound by DuckDB (``$name``), never formatted
into the SQL text. The SQL lives in ``dip/analytics/sql/{name}.sql``.

DuckDB reads Parquet straight from GCS with a short-lived OAuth token from the
service account (no HMAC keys), and once the views exist, the connection is locked
so a query can't read anything outside ``lake/`` or change that setting.
"""

import re
import threading
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from importlib.resources import files
from typing import TYPE_CHECKING, Any

from dip.analytics.lake import EVAL_FIELD_RESULTS, EVAL_RUNS, RECORD_FIELDS, RECORDS
from dip.service.blobs import BlobStore

if TYPE_CHECKING:
    import duckdb


class QueryError(ValueError):
    """The caller's fault: unknown parameter, wrong type, out of range."""


@dataclass(frozen=True)
class Param:
    name: str
    kind: type[int] | type[float] | type[str]
    description: str
    default: int | float | str | None = None  # None: required
    minimum: float | None = None
    maximum: float | None = None
    pattern: str | None = None  # strings must fully match

    def parse(self, raw: str | None) -> int | float | str:
        if raw is None:
            if self.default is None:
                raise QueryError(f"missing parameter {self.name!r}")
            return self.default
        try:
            value = self.kind(raw)
        except ValueError:
            raise QueryError(f"{self.name} must be {self.kind.__name__}") from None
        if isinstance(value, int | float):
            if (self.minimum is not None and value < self.minimum) or (
                self.maximum is not None and value > self.maximum
            ):
                raise QueryError(f"{self.name} must be in [{self.minimum}, {self.maximum}]")
        elif self.pattern and not re.fullmatch(self.pattern, value):
            raise QueryError(f"{self.name} has an unexpected format")
        return value


@dataclass(frozen=True)
class Query:
    name: str
    description: str
    params: tuple[Param, ...] = ()

    @property
    def sql(self) -> str:
        return files("dip.analytics.sql").joinpath(f"{self.name}.sql").read_text()

    def bind(self, raw: Mapping[str, str]) -> dict[str, Any]:
        unknown = set(raw) - {p.name for p in self.params}
        if unknown:
            raise QueryError(f"unknown parameter(s): {', '.join(sorted(unknown))}")
        return {p.name: p.parse(raw.get(p.name)) for p in self.params}


_TOKEN = re.compile(r"[A-Za-z0-9._~+/=-]+")
RUN_ID = r"[0-9]{8}-[0-9]{6}-[A-Za-z0-9._-]{1,120}"
SPLIT = r"smoke|experiment|dev|train|test"

QUERIES: dict[str, Query] = {
    q.name: q
    for q in (
        Query(
            "clause_prevalence",
            "Share of contracts of each type that contain each clause.",
            (Param("min_contracts", int, "Hide types with fewer contracts", 1, 1, 10_000),),
        ),
        Query("governing_law", "Contracts per governing law."),
        Query(
            "production_by_route",
            "Cost, latency and validity of service extractions by route and model.",
            (Param("days", int, "Look-back window in days", 30, 1, 3650),),
        ),
        Query(
            "eval_by_route_model",
            "Eval-run F1, cost and latency by route, model and input variant (D1/D2).",
            (Param("split", str, "Eval split", "experiment", pattern=SPLIT),),
        ),
        Query(
            "field_regressions",
            "Fields whose headline F1 dropped from run_a to run_b.",
            (
                Param("run_a", str, "Baseline run_id", pattern=RUN_ID),
                Param("run_b", str, "Candidate run_id", pattern=RUN_ID),
                Param("min_drop", float, "Smallest drop to report, in F1 points", 2.0, 0, 100),
            ),
        ),
    )
}

# table -> (prefix under lake/, glob under it, schema for the empty case)
TABLES: dict[str, tuple[str, str, dict[str, str]]] = {
    "records": ("records/", "records/*/*.parquet", {**RECORDS, "dt": "DATE"}),
    "record_fields": (
        "record_fields/",
        "record_fields/*/*.parquet",
        {**RECORD_FIELDS, "dt": "DATE"},
    ),
    "eval_runs": ("eval/runs.parquet", "eval/runs.parquet", EVAL_RUNS),
    "eval_field_results": (
        "eval/field_results/",
        "eval/field_results/*.parquet",
        EVAL_FIELD_RESULTS,
    ),
}


@dataclass
class Result:
    columns: list[str]
    rows: list[dict[str, Any]]


class Lake:
    """Opens a DuckDB connection with the lake's tables as views."""

    def __init__(
        self,
        root: str,  # "gs://bucket/lake" or a local directory
        blobs: BlobStore,
        token: Callable[[], str] | None = None,  # OAuth access token, for gs://
        extension_dir: str | None = None,
    ) -> None:
        self.root = root.rstrip("/")
        self.blobs = blobs
        self.token = token
        self.extension_dir = extension_dir

    def connect(self) -> "duckdb.DuckDBPyConnection":
        import duckdb  # imported per query, not at startup: Cloud Run cold start (Phase 8)

        # Bounded: the API has 1 GiB and keeps serving uploads while a query runs.
        config: dict[str, Any] = {"threads": 2, "memory_limit": "384MB"}
        if self.extension_dir:  # baked into the image: never download at runtime
            config |= {
                "extension_directory": self.extension_dir,
                "autoinstall_known_extensions": False,
            }
        con = duckdb.connect(config=config)
        if self.root.startswith("gs://"):
            if self.token is None:
                raise RuntimeError("reading gs:// needs an access token")
            token = self.token()
            if not _TOKEN.fullmatch(token):  # it goes into SQL text: allow only token characters
                raise RuntimeError("unexpected access token format")
            con.execute("LOAD httpfs")
            con.execute(f"CREATE SECRET lake (TYPE gcs, BEARER_TOKEN '{token}')")
        for table, (prefix, glob, schema) in TABLES.items():
            if self.blobs.list(f"lake/{prefix}"):
                hive = "true" if "/*/" in glob else "false"
                # Table, root and glob are ours, never the caller's.
                con.execute(
                    f"CREATE VIEW {table} AS SELECT * FROM read_parquet("  # noqa: S608
                    f"'{self.root}/{glob}', hive_partitioning = {hive}, union_by_name = true)"
                )
            else:  # nothing compacted yet: an empty table with the right columns
                columns = ", ".join(f"{c} {t}" for c, t in schema.items())
                con.execute(f"CREATE TABLE {table} ({columns})")
        con.execute(
            "CREATE VIEW latest_records AS SELECT * FROM records QUALIFY row_number() "
            "OVER (PARTITION BY document_sha256 ORDER BY created_at DESC) = 1"
        )
        # Defense in depth: the SQL is ours, but nothing it runs may read beyond the lake.
        con.execute(f"SET allowed_directories = ['{self.root}/']")
        con.execute("SET enable_external_access = false")
        con.execute("SET lock_configuration = true")
        return con

    def run(self, name: str, raw_params: Mapping[str, str]) -> Result:
        query = QUERIES.get(name)
        if query is None:
            raise KeyError(name)
        params = query.bind(raw_params)
        with self.connect() as con:
            cursor = con.execute(query.sql, params)
            columns = [d[0] for d in cursor.description or []]
            return Result(
                columns, [dict(zip(columns, row, strict=True)) for row in cursor.fetchall()]
            )


class GoogleToken:
    """A cached, auto-refreshed access token from the service's own credentials."""

    SCOPE = "https://www.googleapis.com/auth/devstorage.read_only"

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._credentials: Any = None

    def __call__(self) -> str:
        import google.auth
        from google.auth.transport.requests import Request

        with self._lock:
            if self._credentials is None:
                self._credentials, _ = google.auth.default(scopes=[self.SCOPE])
            if not self._credentials.valid:
                self._credentials.refresh(Request())
            return self._credentials.token
