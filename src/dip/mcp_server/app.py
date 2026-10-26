"""dip-mcp on Cloud Run (SPEC §12.2.2): Streamable HTTP, stateless, Google OAuth.

Run: ``uvicorn dip.mcp_server.app:create_app --factory`` (the image does this with
``DIP_ROLE=mcp_server``). Stateless mode keeps no per-session state, so Cloud Run can
scale out and to zero. Locally, use stdio instead: ``dip mcp-stdio``.
"""

from urllib.parse import urlsplit

from mcp.server.auth.settings import AuthSettings
from mcp.server.transport_security import TransportSecuritySettings
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.types import ASGIApp, Receive, Scope, Send

from dip.config import Environment, get_settings
from dip.mcp_server.auth import (
    FirestorePrincipalStore,
    GoogleTokenVerifier,
    MemoryPrincipalStore,
    PrincipalStore,
    TokenServiceUnavailableError,
)
from dip.mcp_server.server import build_server
from dip.observability.logging import configure_logging
from dip.service.backends import build_services


async def _server_error(_: Request, exc: Exception) -> Response:
    """Tokeninfo unreachable -> 503, never a pass (SPEC §12.2.5, step 2). Anything else: 500.

    Registered for ``Exception``, so Starlette runs it in its outermost middleware,
    where errors raised by the auth middleware end up.
    """
    if isinstance(exc, TokenServiceUnavailableError):
        return JSONResponse(
            {"error": "temporarily_unavailable", "error_description": "token check failed"},
            status_code=503,
            headers={"Retry-After": "5"},
        )
    return JSONResponse({"error": "server_error"}, status_code=500)


class NoNotificationStream:
    """``GET /mcp`` -> 405: a stateless server has no server-to-client stream to offer.

    The Streamable HTTP spec lets a server answer the standalone GET with 405 instead of
    an SSE stream. Without it, the SDK held the GET open until Cloud Run's timeout
    (60 s), and MCP Inspector queued its tool calls behind it until they timed out.
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "http" and scope["method"] == "GET" and scope["path"] == "/mcp":
            response = Response(status_code=405, headers={"Allow": "POST, DELETE"})
            await response(scope, receive, send)
            return
        await self.app(scope, receive, send)


def create_app() -> Starlette:
    settings = get_settings()
    configure_logging(settings.log_level, json=settings.env is not Environment.LOCAL)
    if not (settings.mcp_oauth_client_id and settings.mcp_public_url):
        raise RuntimeError("DIP_MCP_OAUTH_CLIENT_ID and DIP_MCP_PUBLIC_URL are required")
    services = build_services(settings)
    principals: PrincipalStore = (
        FirestorePrincipalStore() if settings.backend == "gcp" else MemoryPrincipalStore()
    )
    public = settings.mcp_public_url.rstrip("/")
    server = build_server(
        services,
        descriptions=settings.mcp_descriptions,
        granularity="coarse",
        token_verifier=GoogleTokenVerifier(settings.mcp_oauth_client_id, principals),
        auth=AuthSettings(
            issuer_url="https://accounts.google.com",  # type: ignore[arg-type]
            resource_server_url=f"{public}/mcp",  # type: ignore[arg-type]
            validate_token_resource=False,  # Google has no resource indicators; we check aud
        ),
    )

    @server.custom_route("/health", methods=["GET"], include_in_schema=False)
    async def health(_: Request) -> Response:
        return JSONResponse({"status": "ok"})

    hosts = sorted({urlsplit(u).netloc for u in (public, *settings.mcp_extra_urls)})
    app: Starlette = server.streamable_http_app(
        stateless_http=True,
        json_response=True,  # one JSON response per request: nothing to keep open
        transport_security=TransportSecuritySettings(
            allowed_hosts=hosts, allowed_origins=list(settings.mcp_allowed_origins)
        ),
    )
    app.add_exception_handler(Exception, _server_error)
    app.add_middleware(NoNotificationStream)  # outermost of ours: before auth, nothing to leak
    return app
