"""The MCP server (SPEC §12.2): a thin adapter over the service layer, like the REST API.

``build_server(services, descriptions="v2", granularity="coarse")`` returns an
``MCPServer``. The variants exist for decision D8 (agent task eval):

- **coarse** (the spec's tool set): submit, status, get_record, search_records
  (all filters in one call), run_analytics.
- **fine**: search split into one tool per filter, and get_record into an
  overview plus one field at a time. More, smaller tools; the agent combines them.

Every tool goes through ``_tool``, which checks the caller's role (when OAuth is on),
runs the blocking work in a thread, turns service errors into actionable tool errors
(``isError``, with what to do next), and writes one audit log line per call.
"""

import contextvars
import datetime as dt
import functools
import hashlib
import json
import time
from collections.abc import Callable
from importlib.resources import files
from typing import Annotated, Any, Literal, cast

import anyio
import structlog
import yaml
from mcp.server.auth.middleware.auth_context import get_access_token
from mcp.server.auth.provider import AccessToken
from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ResourceNotFoundError, ToolError
from mcp_types import CallToolResult, TextContent, ToolAnnotations
from pydantic import BaseModel, Field, ValidationError

from dip.analytics.contract_types import contract_type
from dip.analytics.queries import QUERIES, QueryError
from dip.analytics.search import CLAUSES, ClauseName, SearchFilters, SearchPage, search
from dip.mcp_server.auth import Role
from dip.mcp_server.fetch import FetchError, fetch
from dip.mcp_server.models import (
    AnalyticsResult,
    ContractList,
    ContractRef,
    Overview,
    Quote,
    RecordView,
    StatusResult,
    SubmitResult,
    overview,
    record_view,
)
from dip.schema.domain import ContractRecord
from dip.schema.registry import FIELDS
from dip.service import extractions
from dip.service.backends import Services
from dip.service.jobs import Job
from dip.service.uploads import UploadError

log = structlog.get_logger()

FIELD_NAMES = [s.name for s in FIELDS]
_FIELD_ENUM: dict[str, Any] = {"enum": FIELD_NAMES}
FieldName = Annotated[str, Field(json_schema_extra=_FIELD_ENUM)]
QueryName = Literal[
    "clause_prevalence", "governing_law", "production_by_route", "eval_by_route_model",
    "field_regressions",
]  # fmt: skip
MAX_ROWS = 100
MAX_WAIT_S = 25
Granularity = Literal["coarse", "fine"]

_principal: contextvars.ContextVar[AccessToken | None] = contextvars.ContextVar(
    "dip_mcp_principal", default=None
)

READ_ONLY = ToolAnnotations(read_only_hint=True, open_world_hint=False)
# Not destructive; idempotent (deduplicated by document hash); open world (fetches URLs).
SUBMIT = ToolAnnotations(
    read_only_hint=False, destructive_hint=False, idempotent_hint=True, open_world_hint=True
)


def load_descriptions(version: str) -> dict[str, Any]:
    text = files("dip.mcp_server.descriptions").joinpath(f"{version}.yaml").read_text()
    return yaml.safe_load(text)


def _result(model: BaseModel, summary: str) -> CallToolResult:
    """Structured content, and the same data as text: a summary line, then compact JSON.

    The MCP spec asks tools that return structured content to also return it as text,
    for clients that pass only ``content`` to the model. A summary alone would leave
    those clients with nothing to answer from.
    """
    data = model.model_dump(mode="json")
    text = f"{summary}\n{json.dumps(data, separators=(',', ':'), ensure_ascii=False)}"
    return CallToolResult(content=[TextContent(type="text", text=text)], structured_content=data)


def _args_hash(kwargs: dict[str, Any]) -> str:
    blob = json.dumps(kwargs, sort_keys=True, default=str).encode()
    return hashlib.sha256(blob).hexdigest()[:16]


def _retry_after(job: Job) -> int | None:
    if job.status.done:
        return None
    return 20 if job.status.value == "queued" else 10


def _status(job: Job) -> StatusResult:
    return StatusResult(
        job_id=job.job_id,
        status=job.status.value,
        created_at=job.created_at,
        updated_at=job.updated_at,
        record_id=job.record_id,
        error=job.error,
        retry_after_s=_retry_after(job),
    )


def build_server(
    services: Services,
    descriptions: str = "v2",
    granularity: Granularity = "coarse",
    *,
    fetcher: Callable[[str, int], tuple[bytes, str]] = fetch,
    **server_kwargs: Any,
) -> MCPServer:
    text = load_descriptions(descriptions)
    desc: dict[str, str] = text["tools"]
    server = MCPServer(
        "dip",
        instructions=text["instructions"],
        version=f"descriptions-{descriptions}-{granularity}",
        **server_kwargs,
    )
    svc = services

    def _tool(name: str, role: Role, annotations: ToolAnnotations) -> Callable[..., Any]:
        def register(fn: Callable[..., CallToolResult]) -> Callable[..., Any]:
            @functools.wraps(fn)
            async def call(**kwargs: Any) -> CallToolResult:
                token = get_access_token()
                if token is not None and role not in (token.claims or {}).get("roles", []):
                    raise ToolError(f"your account lacks the '{role}' role needed for {name}")
                started, outcome, size = time.perf_counter(), "ok", 0
                ctx = contextvars.copy_context()
                ctx.run(_principal.set, token)
                try:
                    result = cast(
                        CallToolResult,
                        await anyio.to_thread.run_sync(functools.partial(ctx.run, fn, **kwargs)),
                    )
                    size = len(json.dumps(result.structured_content or {}))
                    return result
                except ToolError:
                    outcome = "tool_error"
                    raise
                except (extractions.ServiceError, UploadError, FetchError, QueryError) as exc:
                    outcome = "tool_error"
                    raise ToolError(_advice(exc)) from exc
                except ValidationError as exc:
                    outcome = "tool_error"
                    raise ToolError(f"invalid arguments: {exc.errors()[0]['msg']}") from exc
                except Exception:
                    # A bug, not the caller's fault: the SDK tells the client only "Error
                    # executing tool"; the audit line must not say "ok" (it did, in Phase 9.5).
                    outcome = "crash"
                    raise
                finally:
                    log.info(
                        "mcp.tool_call",
                        tool=name,
                        principal=token.subject if token else None,
                        email=(token.claims or {}).get("email") if token else None,
                        args_sha=_args_hash(kwargs),
                        outcome=outcome,
                        result_bytes=size,
                        ms=round(1000 * (time.perf_counter() - started)),
                    )

            server.add_tool(call, name=name, description=desc[name], annotations=annotations)
            return fn

        return register

    # ---------------------------------------------------------------- shared tools

    @_tool("submit_extraction", "extractions:write", SUBMIT)
    def submit_extraction(
        document_url: str | None = None,
        gcs_uri: str | None = None,
        idempotency_key: str | None = None,
        wait_seconds: Annotated[int, Field(ge=0, le=MAX_WAIT_S)] = 0,
    ) -> Annotated[CallToolResult, SubmitResult]:
        if bool(document_url) == bool(gcs_uri):
            raise ToolError("pass exactly one of document_url (https) or gcs_uri (gs://)")
        limit = svc.settings.max_upload_mb * 2**20
        if document_url:
            data, filename = fetcher(document_url, limit)
        else:
            data, filename = _read_inbox(svc, gcs_uri or "")
        token = _principal.get()
        submission = extractions.submit(
            svc,
            data,
            filename,
            idempotency_key=idempotency_key,
            principal=token.subject if token else None,
            daily_cap_usd=(token.claims or {}).get("daily_cap_usd") if token else None,
        )
        job = submission.job
        deadline = time.monotonic() + wait_seconds
        while not job.status.done and time.monotonic() < deadline:
            time.sleep(1.0)
            job = svc.jobs.get(job.job_id) or job
        out = SubmitResult(
            job_id=job.job_id,
            status=job.status.value,
            deduplicated=submission.deduplicated,
            record_id=job.record_id,
            retry_after_s=_retry_after(job),
        )
        return _result(out, f"job {job.job_id}: {job.status.value}")

    @_tool("get_extraction_status", "records:read", READ_ONLY)
    def get_extraction_status(job_id: str) -> Annotated[CallToolResult, StatusResult]:
        job = svc.jobs.get(job_id)
        if job is None:
            raise ToolError(f"no job {job_id}; job ids come from submit_extraction")
        out = _status(job)
        hint = f"; poll again in {out.retry_after_s}s" if out.retry_after_s else ""
        return _result(out, f"job {job_id}: {job.status.value}{hint}")

    @_tool("run_analytics", "analytics:read", READ_ONLY)
    def run_analytics(
        query_name: QueryName, params: dict[str, str] | None = None
    ) -> Annotated[CallToolResult, AnalyticsResult]:
        result = svc.lake.run(query_name, params or {})
        rows = [_jsonable(r) for r in result.rows[:MAX_ROWS]]
        out = AnalyticsResult(
            query=query_name,
            columns=result.columns,
            rows=rows,
            truncated=len(result.rows) > MAX_ROWS,
        )
        return _result(out, f"{query_name}: {len(result.rows)} rows")

    # ---------------------------------------------------------------- coarse tools

    if granularity == "coarse":

        @_tool("get_record", "records:read", READ_ONLY)
        def get_record(
            record_id: str | None = None,
            job_id: str | None = None,
            fields: Annotated[list[FieldName] | None, Field(max_length=41)] = None,
        ) -> Annotated[CallToolResult, RecordView]:
            record = _record(svc, record_id, job_id)
            unknown = sorted(set(fields or []) - set(FIELD_NAMES))
            if unknown:
                raise ToolError(f"unknown field(s) {unknown}; see dip://fields")
            out = record_view(record, contract_type(record.fields.document_name.value), fields)
            return _result(
                out,
                f"{record.record_id}: {len(out.fields)} fields present, {len(out.absent)} absent",
            )

        @_tool("search_records", "records:read", READ_ONLY)
        def search_records(
            contract_type: str | None = None,
            governing_law: str | None = None,
            clauses_present: list[ClauseName] | None = None,
            clauses_absent: list[ClauseName] | None = None,
            expires_before: dt.date | None = None,
            expires_after: dt.date | None = None,
            limit: Annotated[int, Field(ge=1, le=50)] = 10,
            cursor: str | None = None,
        ) -> Annotated[CallToolResult, SearchPage]:
            page = search(
                svc.lake,
                SearchFilters(
                    contract_type=contract_type,
                    governing_law=governing_law,
                    clauses_present=clauses_present or [],
                    clauses_absent=clauses_absent or [],
                    expires_before=expires_before,
                    expires_after=expires_after,
                    limit=limit,
                    cursor=cursor,
                ),
            )
            more = "; next_cursor for more" if page.next_cursor else ""
            return _result(
                page, f"{page.total} matching contracts, {len(page.results)} shown{more}"
            )

    # ---------------------------------------------------------------- fine tools

    else:

        @_tool("get_contract_overview", "records:read", READ_ONLY)
        def get_contract_overview(record_id: str) -> Annotated[CallToolResult, Overview]:
            record = _record(svc, record_id, None)
            out = overview(record, contract_type(record.fields.document_name.value))
            return _result(out, f"{record_id}: {out.document_name}")

        @_tool("get_field", "records:read", READ_ONLY)
        def get_field(record_id: str, field: FieldName) -> Annotated[CallToolResult, RecordView]:
            if field not in FIELD_NAMES:
                raise ToolError(f"unknown field {field!r}; see dip://fields")
            record = _record(svc, record_id, None)
            out = record_view(record, contract_type(record.fields.document_name.value), [field])
            found = "present" if out.fields else "absent"
            return _result(out, f"{record_id}.{field}: {found}")

        def _list(filters: SearchFilters, quote_field: str | None = None) -> CallToolResult:
            page = search(svc.lake, filters)
            refs = []
            for r in page.results:
                cite = next((c for c in r.matched if c.field == quote_field), None)
                refs.append(
                    ContractRef(
                        record_id=r.record_id,
                        document_name=r.document_name,
                        expiration_date=r.expiration_date,
                        quote=Quote(quote=cite.quote, page=cite.page)
                        if cite and cite.quote
                        else None,
                    )
                )
            out = ContractList(results=refs, total=page.total, next_cursor=page.next_cursor)
            return _result(out, f"{page.total} contracts, {len(refs)} shown")

        @_tool("find_contracts_with_clause", "records:read", READ_ONLY)
        def find_contracts_with_clause(
            clause: ClauseName,
            present: bool = True,
            limit: Annotated[int, Field(ge=1, le=50)] = 20,
            cursor: str | None = None,
        ) -> Annotated[CallToolResult, ContractList]:
            if present:
                filters = SearchFilters(clauses_present=[clause], limit=limit, cursor=cursor)
            else:
                filters = SearchFilters(clauses_absent=[clause], limit=limit, cursor=cursor)
            return _list(filters, clause if present else None)

        @_tool("find_contracts_by_governing_law", "records:read", READ_ONLY)
        def find_contracts_by_governing_law(
            law: str, limit: Annotated[int, Field(ge=1, le=50)] = 20, cursor: str | None = None
        ) -> Annotated[CallToolResult, ContractList]:
            return _list(SearchFilters(governing_law=law, limit=limit, cursor=cursor))

        @_tool("find_contracts_by_type", "records:read", READ_ONLY)
        def find_contracts_by_type(
            contract_type: str,
            limit: Annotated[int, Field(ge=1, le=50)] = 20,
            cursor: str | None = None,
        ) -> Annotated[CallToolResult, ContractList]:
            return _list(SearchFilters(contract_type=contract_type, limit=limit, cursor=cursor))

        @_tool("find_contracts_expiring", "records:read", READ_ONLY)
        def find_contracts_expiring(
            before: dt.date | None = None,
            after: dt.date | None = None,
            limit: Annotated[int, Field(ge=1, le=50)] = 20,
            cursor: str | None = None,
        ) -> Annotated[CallToolResult, ContractList]:
            filters = SearchFilters(
                expires_before=before, expires_after=after, limit=limit, cursor=cursor
            )
            return _list(filters)

    # ---------------------------------------------------------------- resources

    @server.resource("dip://schema/contract-record", mime_type="application/json")
    def contract_record_schema() -> str:
        """JSON Schema of a ContractRecord."""
        return json.dumps(ContractRecord.model_json_schema())

    @server.resource("dip://fields", mime_type="application/json")
    def field_registry() -> str:
        """Every field: name, type, family and what it means."""
        return json.dumps(
            [
                {
                    "name": s.name,
                    "type": s.field_type.value,
                    "family": s.group.value,
                    "definition": s.definition,
                }
                for s in FIELDS
            ]
        )

    @server.resource("dip://records/{record_id}", mime_type="application/json")
    def record_resource(record_id: str) -> str:
        """One contract record, every present field with its evidence."""
        record = extractions.find_record(svc, record_id)
        if record is None:
            raise ResourceNotFoundError(f"no record {record_id}")
        view = record_view(record, contract_type(record.fields.document_name.value))
        return view.model_dump_json()

    return server


def _jsonable(row: dict[str, Any]) -> dict[str, Any]:
    return json.loads(json.dumps(row, default=str))


def _record(svc: Services, record_id: str | None, job_id: str | None) -> ContractRecord:
    if bool(record_id) == bool(job_id):
        raise ToolError("pass exactly one of record_id or job_id")
    if job_id:
        job = svc.jobs.get(job_id)
        if job is None:
            raise ToolError(f"no job {job_id}")
        return extractions.record_for_job(svc, job)
    record = extractions.find_record(svc, record_id or "")
    if record is None:
        raise ToolError(f"no record {record_id}; find record ids with search_records")
    return record


def _read_inbox(svc: Services, uri: str) -> tuple[bytes, str]:
    """``gs://<this project's bucket>/inbox/...`` only (SPEC §12.2.5)."""
    bucket = svc.settings.gcs_bucket or "local"
    prefix = f"gs://{bucket}/inbox/"
    if not uri.startswith(prefix) or ".." in uri:
        raise ToolError(f"gcs_uri must be under {prefix}")
    key = uri.removeprefix(f"gs://{bucket}/")
    if not svc.blobs.exists(key):
        raise ToolError(f"{uri} does not exist")
    return svc.blobs.get(key), key.rsplit("/", 1)[-1]


def _advice(exc: Exception) -> str:
    """Service errors, rephrased as what the agent should do next."""
    if isinstance(exc, extractions.BusyError):
        return f"{exc} (retry in {exc.retry_after_s}s)"
    if isinstance(exc, extractions.NotReadyError):
        return f"{exc}: call get_extraction_status(job_id='{exc.job.job_id}') in ~15s"
    if isinstance(exc, UploadError):
        return f"{exc.title}: {exc.detail}"
    return str(exc)


__all__ = ["CLAUSES", "QUERIES", "build_server", "load_descriptions"]
