"""dip-mcp's HTTP edges: health, 401 + discovery metadata, fail-closed 503."""

from pathlib import Path

import pytest
from starlette.testclient import TestClient

from dip.config import get_settings
from dip.mcp_server import app as mcp_app
from dip.mcp_server.auth import GoogleTokenVerifier, TokenServiceUnavailableError

PUBLIC = "https://dip-mcp-123.us-central1.run.app"


@pytest.fixture
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.chdir(tmp_path)  # no .env from the repo
    monkeypatch.setenv("DIP_BACKEND", "local")
    monkeypatch.setenv("DIP_SERVICE_DIR", str(tmp_path / "service"))
    monkeypatch.setenv("DIP_MCP_OAUTH_CLIENT_ID", "cid.apps.googleusercontent.com")
    monkeypatch.setenv("DIP_MCP_PUBLIC_URL", PUBLIC)
    get_settings.cache_clear()
    try:
        with TestClient(mcp_app.create_app(), base_url=PUBLIC) as c:
            yield c
    finally:
        get_settings.cache_clear()


def test_health(client: TestClient) -> None:
    assert client.get("/health").json() == {"status": "ok"}


def test_unauthenticated_calls_point_to_the_metadata(client: TestClient) -> None:
    response = client.post("/mcp", json={"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
    assert response.status_code == 401
    assert "resource_metadata=" in response.headers["www-authenticate"]

    meta = client.get("/.well-known/oauth-protected-resource/mcp").json()
    assert meta["resource"] == f"{PUBLIC}/mcp"
    assert meta["authorization_servers"] == ["https://accounts.google.com"]  # no trailing slash


def test_a_tokeninfo_outage_is_a_503_not_a_pass(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    async def down(self: GoogleTokenVerifier, token: str) -> None:
        raise TokenServiceUnavailableError("tokeninfo unreachable")

    monkeypatch.setattr(GoogleTokenVerifier, "verify_token", down)
    # Starlette re-raises after its error handler has answered; look at the answer.
    client = TestClient(client.app, base_url=PUBLIC, raise_server_exceptions=False)
    response = client.post(
        "/mcp",
        json={"jsonrpc": "2.0", "id": 1, "method": "tools/list"},
        headers={"Authorization": "Bearer anything"},
    )
    assert response.status_code == 503
    assert response.headers["retry-after"] == "5"


def test_other_hosts_are_refused(client: TestClient) -> None:
    response = client.post(
        "/mcp",
        json={"jsonrpc": "2.0", "id": 1, "method": "tools/list"},
        headers={"Host": "evil.example", "Authorization": "Bearer x"},
    )
    assert response.status_code in (401, 421)  # never served


def test_the_standalone_get_stream_is_refused_not_held_open(client: TestClient) -> None:
    # A held-open GET made MCP Inspector queue every tool call behind it (Phase 9.5).
    response = client.get("/mcp", headers={"Accept": "text/event-stream"})
    assert response.status_code == 405
    assert response.headers["allow"] == "POST, DELETE"
