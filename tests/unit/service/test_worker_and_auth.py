from pathlib import Path

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from pydantic import SecretStr

from dip.service import auth
from dip.service.backends import Services
from dip.service.blobs import LocalBlobStore
from dip.worker.app import create_app


def test_worker_requires_the_internal_token(services: Services) -> None:
    services.settings = services.settings.model_copy(update={"internal_token": SecretStr("s3cret")})
    client = TestClient(create_app(services))

    assert client.post("/internal/process", json={"job_id": "x"}).status_code == 401
    ok = client.post(
        "/internal/process", json={"job_id": "x"}, headers={"X-Internal-Token": "s3cret"}
    )
    assert ok.json() == {"job_id": "x", "status": "unknown"}


class _Req:
    def __init__(self, headers: dict[str, str]) -> None:
        self.headers = headers


@pytest.mark.parametrize(
    ("headers", "claims", "status"),
    [
        ({}, None, 401),
        ({"authorization": "Bearer t"}, {"email": "attacker@x.iam", "email_verified": True}, 403),
        ({"authorization": "Bearer t"}, {"email": "tasks@p.iam", "email_verified": False}, 403),
    ],
)
def test_gcp_internal_auth_rejects_anything_but_the_invoker(
    services: Services,
    monkeypatch: pytest.MonkeyPatch,
    headers: dict[str, str],
    claims: dict | None,
    status: int,
) -> None:
    settings = services.settings.model_copy(
        update={"backend": "gcp", "tasks_invoker_email": "tasks@p.iam"}
    )
    monkeypatch.setattr(auth, "_verify_google_oidc", lambda token, audience: claims)

    with pytest.raises(HTTPException) as err:
        auth.check_internal(_Req(headers), settings)  # type: ignore[arg-type]
    assert err.value.status_code == status


def test_gcp_internal_auth_accepts_the_invoker(
    services: Services, monkeypatch: pytest.MonkeyPatch
) -> None:
    settings = services.settings.model_copy(
        update={"backend": "gcp", "tasks_invoker_email": "tasks@p.iam"}
    )
    seen: dict[str, str] = {}
    monkeypatch.setattr(
        auth,
        "_verify_google_oidc",
        lambda token, audience: (
            seen.setdefault("aud", audience) and {"email": "tasks@p.iam", "email_verified": True}
        ),
    )

    auth.check_internal(_Req({"authorization": "Bearer t"}), settings)  # type: ignore[arg-type]
    assert seen["aud"] == settings.worker_url.rstrip("/")


@pytest.mark.parametrize(
    ("token", "headers", "status"),
    [
        (None, {"x-internal-token": "anything"}, 500),  # misconfigured: fail closed
        ("s3cret", {"x-internal-token": "wrong"}, 401),
        ("s3cret", {"authorization": "Bearer t"}, 401),  # OIDC is not accepted on this path
    ],
)
def test_http_queue_on_gcp_requires_the_shared_token(
    services: Services, token: str | None, headers: dict[str, str], status: int
) -> None:
    settings = services.settings.model_copy(
        update={
            "backend": "gcp",
            "queue_backend": "http",
            "internal_token": SecretStr(token) if token else None,
        }
    )
    with pytest.raises(HTTPException) as err:
        auth.check_internal(_Req(headers), settings)  # type: ignore[arg-type]
    assert err.value.status_code == status


def test_http_queue_on_gcp_accepts_the_shared_token(services: Services) -> None:
    settings = services.settings.model_copy(
        update={"backend": "gcp", "queue_backend": "http", "internal_token": SecretStr("s3cret")}
    )
    auth.check_internal(_Req({"x-internal-token": "s3cret"}), settings)  # type: ignore[arg-type]


def test_api_keys_required_outside_local(services: Services) -> None:
    settings = services.settings.model_copy(update={"backend": "gcp"})
    with pytest.raises(HTTPException) as err:
        auth.check_api_key(_Req({}), settings)  # type: ignore[arg-type]
    assert err.value.status_code == 500


def test_local_blob_store_refuses_keys_that_escape(tmp_path: Path) -> None:
    store = LocalBlobStore(tmp_path)
    with pytest.raises(ValueError, match="escapes"):
        store.put("../outside.txt", b"x", "text/plain")


def test_worker_traces_for_its_lifetime(
    services: Services, monkeypatch: pytest.MonkeyPatch
) -> None:
    from dip.worker import app as worker_app

    calls: list[str] = []
    monkeypatch.setattr(worker_app, "configure_tracing", lambda *a: calls.append("start"))
    monkeypatch.setattr(worker_app, "shutdown_tracing", lambda: calls.append("stop"))

    with TestClient(create_app(services)):
        assert calls == ["start"]
    assert calls == ["start", "stop"]
