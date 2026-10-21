"""End to end, offline: upload -> poll -> record (the Phase 7 done criterion)."""

import time

import pytest
from fastapi.testclient import TestClient
from pydantic import SecretStr

from dip.api.app import create_app
from dip.service.backends import Services
from dip.service.jobs import Job, JobStatus
from dip.service.processing import MAX_ATTEMPTS, process_job
from dip.service.queue import InlineQueue
from tests.pdfs import text_pdf
from tests.unit.service.conftest import CONTRACT

PDF_BYTES = text_pdf([[CONTRACT] * 3])


def _upload(client: TestClient, data: bytes = PDF_BYTES, **params: bool) -> dict:
    response = client.post(
        "/v1/extractions", files={"file": ("c.pdf", data, "application/pdf")}, params=params
    )
    assert response.status_code in (200, 202), response.text
    return response.json()


def _job(services: Services, job_id: str) -> Job:
    job = services.jobs.get(job_id)
    assert job is not None
    return job


def _poll(client: TestClient, job_id: str) -> dict:
    for _ in range(100):
        job = client.get(f"/v1/extractions/{job_id}").json()
        if job["status"] in ("succeeded", "partially_succeeded", "failed"):
            return job
        time.sleep(0.05)
    raise AssertionError("job never finished")


def test_upload_poll_record(services: Services) -> None:
    client = TestClient(create_app(services))

    accepted = _upload(client)
    assert accepted["status"] == "queued"
    job = _poll(client, accepted["job_id"])
    record = client.get(accepted["record_url"]).json()

    assert job["status"] == "succeeded"
    assert job["cost_usd"] > 0
    assert record["fields"]["governing_law"]["values"] == ["Texas"]
    assert record["provenance"]["route"] == "text"
    assert record["document_sha256"] == job["document_sha256"]


def test_wait_returns_the_record_directly(services: Services) -> None:
    client = TestClient(create_app(services))

    response = client.post(
        "/v1/extractions", files={"file": ("c.pdf", PDF_BYTES)}, params={"wait": True}
    )

    assert response.status_code == 200
    assert response.json()["fields"]["clauses"]["anti_assignment"]["present"] is True


def test_same_document_is_reused_unless_forced(services: Services) -> None:
    client = TestClient(create_app(services))
    first = _upload(client)
    _poll(client, first["job_id"])

    again = _upload(client)
    forced = _upload(client, force=True)

    assert again["job_id"] == first["job_id"]
    assert again["deduplicated"] is True
    assert forced["job_id"] != first["job_id"]


def test_idempotency_key_conflict_is_409(services: Services) -> None:
    client = TestClient(create_app(services))
    headers = {"Idempotency-Key": "abc"}
    client.post("/v1/extractions", files={"file": ("a.pdf", PDF_BYTES)}, headers=headers)

    other = client.post(
        "/v1/extractions", files={"file": ("b.txt", b"another contract")}, headers=headers
    )

    assert other.status_code == 409
    assert other.headers["content-type"] == "application/problem+json"


def test_errors_are_problem_details(services: Services) -> None:
    client = TestClient(create_app(services))

    unsupported = client.post("/v1/extractions", files={"file": ("x.docx", b"PK\x03\x04zip")})
    missing = client.get("/v1/extractions/nope")

    assert unsupported.status_code == 415
    assert unsupported.json()["title"] == "Unsupported document type"
    assert missing.status_code == 404
    assert missing.headers["content-type"] == "application/problem+json"


def test_record_before_done_is_409(services: Services) -> None:
    services.queue = InlineQueue(lambda job_id: None)  # never processes
    client = TestClient(create_app(services))
    accepted = _upload(client)

    assert client.get(accepted["record_url"]).status_code == 409


def test_api_keys_are_enforced_when_set(services: Services) -> None:
    services.settings = services.settings.model_copy(update={"api_keys": SecretStr("k1, k2")})
    client = TestClient(create_app(services))

    assert client.get("/v1/schema").status_code == 401
    assert client.get("/v1/schema", headers={"X-API-Key": "wrong"}).status_code == 401
    assert client.get("/v1/schema", headers={"X-API-Key": "k2"}).status_code == 200
    assert client.get("/health").status_code == 200  # probes stay open


def test_transient_failure_is_retried_then_marked_failed(services: Services) -> None:
    services.queue = InlineQueue(lambda job_id: None)
    client = TestClient(create_app(services))
    job_id = _upload(client)["job_id"]

    def boom(*args: object, **kwargs: object) -> object:
        raise RuntimeError("OpenAI is down")

    services.pipeline.process = boom  # type: ignore[method-assign]
    for _ in range(1, MAX_ATTEMPTS):
        with pytest.raises(RuntimeError):
            process_job(job_id, services.jobs, services.blobs, services.pipeline)
        assert _job(services, job_id).status is JobStatus.QUEUED  # back for a retry
    process_job(job_id, services.jobs, services.blobs, services.pipeline)  # last attempt: no raise

    job = _job(services, job_id)
    assert job.status is JobStatus.FAILED
    assert job.attempts == MAX_ATTEMPTS
    assert "OpenAI is down" in (job.error or "")


def test_redelivered_finished_job_is_left_alone(services: Services) -> None:
    client = TestClient(create_app(services))
    job_id = _poll(client, _upload(client)["job_id"])["job_id"]
    before = services.jobs.get(job_id)

    process_job(job_id, services.jobs, services.blobs, services.pipeline)

    assert services.jobs.get(job_id) == before
