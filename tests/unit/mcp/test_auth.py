import httpx
import pytest

from dip.mcp_server.auth import (
    GoogleTokenVerifier,
    MemoryPrincipalStore,
    Principal,
    TokenServiceUnavailableError,
)

pytestmark = pytest.mark.anyio

CLIENT = "dip-client.apps.googleusercontent.com"
NOW = 1_800_000_000.0


def _info(**over: object) -> dict:
    return {
        "aud": CLIENT,
        "azp": CLIENT,
        "sub": "1001",
        "email": "ana@example.com",
        "email_verified": "true",
        "exp": str(int(NOW) + 3600),
        "scope": "openid https://www.googleapis.com/auth/userinfo.email",
    } | over


def _verifier(handler, principals=None, clock=lambda: NOW) -> GoogleTokenVerifier:
    store = principals or MemoryPrincipalStore(
        [Principal(email="ana@example.com", roles=["records:read"], daily_cap_usd=2)]
    )
    http = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    return GoogleTokenVerifier(CLIENT, store, http, clock)


class _Tokeninfo:
    """Answers like Google's tokeninfo and records each request."""

    def __init__(self, status: int = 200, **over: object) -> None:
        self.status, self.over = status, over
        self.calls: list[httpx.Request] = []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.calls.append(request)
        return httpx.Response(self.status, json=_info(**self.over))


def _answer(status: int = 200, **over: object) -> _Tokeninfo:
    return _Tokeninfo(status, **over)


async def test_accepts_an_invited_user_and_binds_their_sub() -> None:
    store = MemoryPrincipalStore([Principal(email="ana@example.com", roles=["records:read"])])
    handler = _answer()
    token = await _verifier(handler, store).verify_token("s3cret-tkn")

    assert token is not None
    assert token.subject == "1001"
    assert token.claims == {
        "email": "ana@example.com",
        "roles": ["records:read"],
        "daily_cap_usd": 1.0,
    }
    assert store.by_sub("1001") is not None  # bound on first sign-in
    request = handler.calls[0]
    assert request.method == "POST"
    assert b"access_token=s3cret-tkn" in request.content
    assert "s3cret-tkn" not in str(request.url)  # not in the URL


@pytest.mark.parametrize(
    "over",
    [
        {"aud": "gcloud-cli.apps.googleusercontent.com", "azp": "other"},  # someone else's app
        {"email_verified": "false"},
        {"exp": str(int(NOW) - 1)},
        {"sub": "2002", "email": "eve@example.com"},  # not invited
    ],
)
async def test_rejects(over: dict) -> None:
    assert await _verifier(_answer(**over)).verify_token("tok") is None


async def test_an_email_bound_to_another_account_is_refused() -> None:
    store = MemoryPrincipalStore([Principal(email="ana@example.com", sub="1001")])
    # Same email, different Google account (e.g. the address was reassigned).
    assert await _verifier(_answer(sub="9999"), store).verify_token("tok") is None


async def test_disabled_principal_is_refused() -> None:
    store = MemoryPrincipalStore([Principal(email="ana@example.com", disabled=True)])
    assert await _verifier(_answer(), store).verify_token("tok") is None


async def test_invalid_token_is_rejected_but_an_outage_fails_closed() -> None:
    assert await _verifier(lambda r: httpx.Response(400, json={})).verify_token("t") is None
    with pytest.raises(TokenServiceUnavailableError):
        await _verifier(lambda r: httpx.Response(503)).verify_token("t")

    def down(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("no route")

    with pytest.raises(TokenServiceUnavailableError):
        await _verifier(down).verify_token("t")


async def test_results_are_cached_for_at_most_five_minutes() -> None:
    clock = [NOW]
    handler = _answer()
    verifier = _verifier(handler, clock=lambda: clock[0])
    await verifier.verify_token("tok")
    await verifier.verify_token("tok")
    assert len(handler.calls) == 1
    clock[0] += 301
    await verifier.verify_token("tok")
    assert len(handler.calls) == 2


def test_principal_defaults_are_least_privilege() -> None:
    p = Principal(email="x@example.com")
    assert p.roles == ["records:read"]
    assert p.daily_cap_usd == 1.0
