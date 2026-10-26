"""Prompt injection, outbound: document text reaches an agent only as a capped, labelled quote."""

import json

import pytest
from mcp import Client

from dip.analytics.lake import QUOTE_CHARS, compact
from dip.mcp_server.models import UNTRUSTED
from dip.mcp_server.server import build_server
from dip.schema.domain import Evidence
from dip.service.backends import Services
from dip.service.blobs import LocalBlobStore
from tests.fixtures_injection import INJECTED_CONTRACT
from tests.unit.mcp.helpers import text
from tests.unit.service.conftest import responses, services  # noqa: F401 - fixtures
from tests.unit.service.test_analytics import _records, _store

pytestmark = pytest.mark.anyio

ATTACK = INJECTED_CONTRACT.split("IMPORTANT")[1].split("2. Assignment")[0]


@pytest.fixture
def poisoned(services: Services) -> Services:  # noqa: F811 - sync: the pipeline runs its own loop
    blobs = services.blobs
    assert isinstance(blobs, LocalBlobStore)
    record = _records(services, 1)[0]
    record.fields.clauses.anti_assignment.evidence = [Evidence(quote="IMPORTANT" + ATTACK * 20)]
    _store(blobs, record)
    compact(blobs)
    return services


async def test_injected_text_stays_inside_evidence(poisoned: Services) -> None:
    async with Client(build_server(poisoned)) as client:
        schema = {t.name: t for t in (await client.list_tools()).tools}["get_record"].output_schema
        result = await client.call_tool(
            "get_record", {"record_id": "r0", "fields": ["anti_assignment"]}
        )
    view = result.structured_content
    quote = view["fields"][0]["evidence"][0]["quote"]
    assert len(quote) <= QUOTE_CHARS  # capped: an attack can't flood the agent's context
    summary = text(result).splitlines()[0]
    assert "ignore" not in summary.lower()  # the summary line is ours, never document text
    assert UNTRUSTED in json.dumps(schema)  # the schema tells the agent what a quote is
    others = {k: v for k, v in view.items() if k != "fields"}
    assert "ignore all previous" not in json.dumps(others).lower()
