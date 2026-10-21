"""Who may call what (SPEC §12, §18).

- Public API: ``X-API-Key`` checked against ``DIP_API_KEYS`` (constant-time compare).
  Unset keys disable the check, which is allowed only with the local backend.
- ``/internal/*`` (the worker) depends on how jobs arrive. From Cloud Tasks: a
  Google-signed OIDC token whose audience is the worker URL and whose email is the
  tasks invoker service account. From the HTTP queue (docker compose): a shared
  ``X-Internal-Token``, required outside the local backend. Anything else is rejected.
"""

import hmac

from fastapi import HTTPException, Request

from dip.config import Settings


def allowed_api_keys(settings: Settings) -> list[str]:
    raw = settings.api_keys.get_secret_value() if settings.api_keys else ""
    return [k.strip() for k in raw.split(",") if k.strip()]


def check_api_key(request: Request, settings: Settings) -> None:
    keys = allowed_api_keys(settings)
    if not keys:
        if settings.backend != "local":
            raise HTTPException(500, "DIP_API_KEYS must be set outside the local backend")
        return
    given = request.headers.get("x-api-key", "")
    if not any(hmac.compare_digest(given, key) for key in keys):
        raise HTTPException(401, "missing or invalid X-API-Key")


def check_internal(request: Request, settings: Settings) -> None:
    if settings.queue_kind != "cloudtasks":
        expected = settings.internal_token.get_secret_value() if settings.internal_token else ""
        if not expected:
            if settings.backend != "local":
                raise HTTPException(500, "DIP_INTERNAL_TOKEN must be set outside the local backend")
            return
        given = request.headers.get("x-internal-token", "")
        if not hmac.compare_digest(given, expected):
            raise HTTPException(401, "invalid internal token")
        return
    header = request.headers.get("authorization", "")
    if not header.lower().startswith("bearer "):
        raise HTTPException(401, "missing OIDC token")
    claims = _verify_google_oidc(header[7:], settings.worker_url.rstrip("/"))
    if claims.get("email") != settings.tasks_invoker_email or not claims.get("email_verified"):
        raise HTTPException(403, "token is not from the tasks invoker service account")


def _verify_google_oidc(token: str, audience: str) -> dict[str, object]:
    from google.auth.transport import requests as google_requests
    from google.oauth2 import id_token

    try:
        return dict(id_token.verify_oauth2_token(token, google_requests.Request(), audience))
    except ValueError as exc:  # bad signature, wrong audience, expired
        raise HTTPException(401, "invalid OIDC token") from exc
