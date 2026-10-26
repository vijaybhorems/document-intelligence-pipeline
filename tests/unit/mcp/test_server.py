"""The MCP server through a real in-process MCP client, over a local store and lake."""

import json

import pytest
from mcp import Client
from mcp.server.auth.middleware.auth_context import auth_context_var
from mcp.server.auth.middleware.bearer_auth import AuthenticatedUser
from mcp.server.auth.provider import AccessToken

from dip.analytics.lake import compact
from dip.analytics.queries import QUERIES
from dip.mcp_server.server import QueryName, build_server
from dip.service.backends import Services
from dip.service.blobs import LocalBlobStore
from tests.unit.mcp.helpers import resource_text, text
from tests.unit.service.conftest import responses, services  # noqa: F401 - fixtures
from tests.unit.service.test_analytics import _records, _store

pytestmark = pytest.mark.anyio


@pytest.fixture
def stocked(services: Services) -> Services:  # noqa: F811
    blobs = services.blobs
    assert isinstance(blobs, LocalBlobStore)
    for record in _records(services, 4):
        _store(blobs, record)
    compact(blobs)
    return services


def _data(result) -> dict:
    assert not result.is_error, text(result)
    return result.structured_content


async def test_coarse_tools_match_the_spec(stocked: Services) -> None:
    async with Client(build_server(stocked)) as client:
        tools = {t.name: t for t in (await client.list_tools()).tools}
    assert set(tools) == {
        "submit_extraction", "get_extraction_status", "get_record", "search_records",
        "run_analytics",
    }  # fmt: skip
    read, submit = tools["get_record"].annotations, tools["submit_extraction"].annotations
    assert read is not None
    assert read.read_only_hint
    assert submit is not None
    assert submit.destructive_hint is False
    assert all(t.output_schema for t in tools.values())  # structured results everywhere
    clauses = tools["search_records"].input_schema["properties"]["clauses_present"]
    assert "anti_assignment" in json.dumps(clauses)  # agents see the exact clause names


async def test_fine_tools_replace_search_and_get_record(stocked: Services) -> None:
    async with Client(build_server(stocked, granularity="fine")) as client:
        names = {t.name for t in (await client.list_tools()).tools}
    assert {"find_contracts_with_clause", "get_field", "get_contract_overview"} <= names
    assert "search_records" not in names


async def test_search_combines_filters_and_cites(stocked: Services) -> None:
    async with Client(build_server(stocked)) as client:
        result = await client.call_tool(
            "search_records",
            {"contract_type": "Distributor", "clauses_present": ["anti_assignment"]},
        )
    page = _data(result)
    assert page["total"] == 2  # r0, r2: Distributor with the clause
    cite = page["results"][0]["matched"][0]
    assert cite["field"] == "anti_assignment"
    assert cite["quote"]
    assert text(result).startswith("2 matching contracts")  # one line, not the JSON


async def test_get_record_projects_fields(stocked: Services) -> None:
    async with Client(build_server(stocked)) as client:
        result = await client.call_tool(
            "get_record", {"record_id": "r1", "fields": ["governing_law", "anti_assignment"]}
        )
    view = _data(result)
    assert [f["field"] for f in view["fields"]] == ["governing_law"]
    assert view["absent"] == ["anti_assignment"]
    assert view["fields"][0]["evidence"][0]["quote"]


async def test_errors_tell_the_agent_what_to_do(stocked: Services) -> None:
    async with Client(build_server(stocked)) as client:
        missing = await client.call_tool("get_record", {"record_id": "nope"})
        both = await client.call_tool("get_record", {"record_id": "r1", "job_id": "j"})
        bad_url = await client.call_tool("submit_extraction", {"document_url": "http://x/a.pdf"})
        bad_gcs = await client.call_tool("submit_extraction", {"gcs_uri": "gs://other/inbox/a.pdf"})
    assert missing.is_error
    assert "search_records" in text(missing)
    assert both.is_error
    assert "exactly one" in text(both)
    assert bad_url.is_error
    assert "https" in text(bad_url)
    assert bad_gcs.is_error
    assert "inbox" in text(bad_gcs)


async def test_analytics_and_resources(stocked: Services) -> None:
    async with Client(build_server(stocked)) as client:
        rows = _data(await client.call_tool("run_analytics", {"query_name": "governing_law"}))
        fields = json.loads(resource_text(await client.read_resource("dip://fields")))
        record = json.loads(resource_text(await client.read_resource("dip://records/r0")))
    assert rows["columns"] == ["governing_law", "contracts", "share"]
    assert len(fields) == 41
    assert record["record_id"] == "r0"


def test_query_enum_matches_the_whitelist() -> None:
    assert set(QueryName.__args__) == set(QUERIES)


async def test_roles_are_enforced_when_authenticated(stocked: Services) -> None:
    reader = AccessToken(
        token="t", client_id="c", scopes=[], subject="1001",
        claims={"email": "a@example.com", "roles": ["records:read"], "daily_cap_usd": 1.0},
    )  # fmt: skip
    reset = auth_context_var.set(AuthenticatedUser(reader))
    try:
        async with Client(build_server(stocked)) as client:
            ok = await client.call_tool("get_record", {"record_id": "r0", "fields": ["parties"]})
            denied = await client.call_tool("run_analytics", {"query_name": "governing_law"})
    finally:
        auth_context_var.reset(reset)
    assert not ok.is_error
    assert denied.is_error
    assert "analytics:read" in text(denied)


async def test_submit_from_the_inbox_waits_for_the_record(stocked: Services) -> None:
    from tests.unit.service.test_api import PDF_BYTES

    stocked.blobs.put("inbox/c.pdf", PDF_BYTES, "application/pdf")
    async with Client(build_server(stocked)) as client:
        sub = _data(
            await client.call_tool(
                "submit_extraction", {"gcs_uri": "gs://local/inbox/c.pdf", "wait_seconds": 10}
            )
        )
        again = _data(
            await client.call_tool("submit_extraction", {"gcs_uri": "gs://local/inbox/c.pdf"})
        )
        record = _data(await client.call_tool("get_record", {"job_id": sub["job_id"]}))
    assert sub["status"] == "succeeded"
    assert sub["record_id"]
    assert again["deduplicated"] is True  # same bytes: no second extraction, no cost
    assert record["record_id"] == sub["record_id"]


async def test_document_urls_go_through_the_guarded_fetcher(stocked: Services) -> None:
    from tests.unit.service.test_api import PDF_BYTES

    fetched: list[str] = []

    def fetcher(url: str, limit: int) -> tuple[bytes, str]:
        fetched.append(url)
        return PDF_BYTES, "c.pdf"

    async with Client(build_server(stocked, fetcher=fetcher)) as client:
        sub = _data(
            await client.call_tool(
                "submit_extraction", {"document_url": "https://example.com/c.pdf"}
            )
        )
    assert fetched == ["https://example.com/c.pdf"]
    assert sub["job_id"]


async def test_spend_cap_refuses_before_enqueueing(stocked: Services) -> None:
    from tests.unit.service.test_api import PDF_BYTES

    stocked.blobs.put("inbox/c.pdf", PDF_BYTES, "application/pdf")
    writer = AccessToken(
        token="t", client_id="c", scopes=[], subject="1001",
        claims={"email": "a@example.com", "roles": ["extractions:write"], "daily_cap_usd": 0.0001},
    )  # fmt: skip
    reset = auth_context_var.set(AuthenticatedUser(writer))
    try:
        async with Client(build_server(stocked)) as client:
            result = await client.call_tool(
                "submit_extraction", {"gcs_uri": "gs://local/inbox/c.pdf"}
            )
    finally:
        auth_context_var.reset(reset)
    assert result.is_error
    assert "daily spend cap" in text(result)
    assert stocked.jobs.count_queued() == 0  # nothing was enqueued


async def test_crashes_are_audited_as_crashes_and_hidden_from_the_client(
    stocked: Services, monkeypatch: pytest.MonkeyPatch
) -> None:
    from structlog.testing import capture_logs

    from dip.mcp_server import server as server_module

    def broken(*_: object, **__: object) -> None:
        raise RuntimeError("internal detail: SELECT secret_column")

    monkeypatch.setattr(server_module, "search", broken)
    with capture_logs() as logs:
        async with Client(build_server(stocked)) as client:
            result = await client.call_tool("search_records", {"governing_law": "Texas"})
    assert result.is_error
    assert "secret_column" not in text(result)  # no internals leak to the agent
    audit = [e for e in logs if e["event"] == "mcp.tool_call"]
    assert audit[-1]["outcome"] == "crash"
