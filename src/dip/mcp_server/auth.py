"""Google OAuth for the remote MCP server (SPEC §12.2.5, ADR I8): dip-mcp is a resource server.

Google issues the tokens; this module decides whether one is good for *this* server,
in order, failing closed at every step:

1. A bearer token is present (the SDK's middleware: else 401 + WWW-Authenticate).
2. Google's tokeninfo accepts it and it hasn't expired. Tokeninfo unreachable ->
   ``TokenServiceUnavailableError`` (503), never a pass.
3. ``aud`` or ``azp`` is our OAuth client ID. A valid Google token issued to any
   other app (gcloud, another site) is rejected.
4. ``email_verified``.
5. A principal exists for the Google ``sub`` (stable; emails can be reassigned) and
   isn't disabled. On first sign-in the principal added by email is bound to the sub.
6. Per-tool roles are checked by the server, from ``AccessToken.claims["roles"]``.

Google access tokens are opaque, so they can't be verified locally; results are
cached by token hash for at most ``CACHE_S`` (or until expiry, if sooner).
"""

import hashlib
import threading
import time
from collections.abc import Callable
from typing import Literal, Protocol

import anyio
import httpx
import structlog
from mcp.server.auth.provider import AccessToken
from pydantic import BaseModel, Field

log = structlog.get_logger()

TOKENINFO = "https://oauth2.googleapis.com/tokeninfo"
CACHE_S = 300
Role = Literal["records:read", "analytics:read", "extractions:write"]
ROLES: tuple[Role, ...] = ("records:read", "analytics:read", "extractions:write")


class TokenServiceUnavailableError(RuntimeError):
    """Google's tokeninfo couldn't be reached: refuse (503) rather than guess."""


class Principal(BaseModel):
    email: str
    sub: str | None = None  # bound on first sign-in
    roles: list[Role] = Field(default_factory=lambda: ["records:read"])
    daily_cap_usd: float = 1.0
    disabled: bool = False


class PrincipalStore(Protocol):
    def get(self, email: str) -> Principal | None: ...
    def put(self, principal: Principal) -> None: ...
    def by_sub(self, sub: str) -> Principal | None: ...
    def all(self) -> list[Principal]: ...


class MemoryPrincipalStore:
    def __init__(self, principals: list[Principal] | None = None) -> None:
        self._lock = threading.Lock()
        self._by_email = {p.email.lower(): p for p in principals or []}

    def get(self, email: str) -> Principal | None:
        with self._lock:
            return self._by_email.get(email.lower())

    def put(self, principal: Principal) -> None:
        with self._lock:
            self._by_email[principal.email.lower()] = principal

    def by_sub(self, sub: str) -> Principal | None:
        with self._lock:
            return next((p for p in self._by_email.values() if p.sub == sub), None)

    def all(self) -> list[Principal]:
        with self._lock:
            return sorted(self._by_email.values(), key=lambda p: p.email)


class FirestorePrincipalStore:
    """``principals/{email}``. Looked up by ``sub`` once bound."""

    def __init__(self, collection: str = "principals") -> None:
        from google.cloud import firestore

        self._collection = firestore.Client().collection(collection)

    def get(self, email: str) -> Principal | None:
        snap = self._collection.document(email.lower()).get()
        return Principal.model_validate(snap.to_dict()) if snap.exists else None

    def put(self, principal: Principal) -> None:
        self._collection.document(principal.email.lower()).set(principal.model_dump())

    def by_sub(self, sub: str) -> Principal | None:
        from google.cloud.firestore_v1.base_query import FieldFilter

        docs = list(self._collection.where(filter=FieldFilter("sub", "==", sub)).limit(1).stream())
        return Principal.model_validate(docs[0].to_dict()) if docs else None

    def all(self) -> list[Principal]:
        return sorted(
            (Principal.model_validate(d.to_dict()) for d in self._collection.stream()),
            key=lambda p: p.email,
        )


def resolve_principal(store: PrincipalStore, sub: str, email: str) -> Principal | None:
    """The principal for a verified Google identity, binding ``sub`` on first sign-in."""
    if (known := store.by_sub(sub)) is not None:
        return known
    invited = store.get(email)
    if invited is None or invited.sub is not None:
        return None  # not invited, or the email now belongs to a different Google account
    bound = invited.model_copy(update={"sub": sub})
    store.put(bound)
    log.info("mcp.principal_bound", email=email)
    return bound


class GoogleTokenVerifier:
    def __init__(
        self,
        client_id: str,
        principals: PrincipalStore,
        http: httpx.AsyncClient | None = None,
        clock: Callable[[], float] = time.time,
    ) -> None:
        self.client_id = client_id
        self.principals = principals
        self._http = http or httpx.AsyncClient(timeout=5.0)
        self._clock = clock
        self._cache: dict[str, tuple[float, AccessToken]] = {}

    async def verify_token(self, token: str) -> AccessToken | None:
        key = hashlib.sha256(token.encode()).hexdigest()
        now = self._clock()
        if (hit := self._cache.get(key)) and hit[0] > now:
            return hit[1]

        try:  # POST keeps the token out of URLs and access logs
            response = await self._http.post(TOKENINFO, data={"access_token": token})
        except httpx.HTTPError as exc:
            raise TokenServiceUnavailableError("tokeninfo unreachable") from exc
        if response.status_code == 400:
            return self._reject("invalid_or_expired")
        if response.status_code != 200:
            raise TokenServiceUnavailableError(f"tokeninfo answered {response.status_code}")
        info = response.json()

        expires = int(info.get("exp", 0))
        if expires <= now:
            return self._reject("expired")
        if self.client_id not in (info.get("aud"), info.get("azp")):
            return self._reject("wrong_audience")
        if str(info.get("email_verified")).lower() != "true":
            return self._reject("email_unverified")
        sub, email = str(info.get("sub", "")), str(info.get("email", ""))
        principal = await anyio.to_thread.run_sync(resolve_principal, self.principals, sub, email)
        if principal is None or principal.disabled:
            return self._reject("not_a_principal" if principal is None else "disabled")

        access = AccessToken(
            token=token,
            client_id=self.client_id,
            scopes=str(info.get("scope", "")).split(),
            expires_at=expires,
            subject=sub,
            claims={
                "email": email,
                "roles": list(principal.roles),
                "daily_cap_usd": principal.daily_cap_usd,
            },
        )
        self._cache[key] = (min(float(expires), now + CACHE_S), access)
        return access

    @staticmethod
    def _reject(reason: str) -> None:
        log.warning("mcp.auth_rejected", reason=reason)  # never the token or the email
        return None
