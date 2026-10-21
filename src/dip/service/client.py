"""A minimal client for the public API: upload, poll, fetch (used by ``dip submit``).

Takes an ``httpx.Client`` (or anything with its interface, like FastAPI's ``TestClient``),
so the same code drives a local stack, Cloud Run, or the app in-process in tests.
"""

import time
from pathlib import Path

import httpx

from dip.pipeline import PDF, TEXT
from dip.schema.domain import ContractRecord

DONE = {"succeeded", "partially_succeeded", "failed"}


class ExtractionFailedError(RuntimeError):
    pass


def submit(
    client: httpx.Client,
    path: Path,
    timeout_s: float = 300.0,
    poll_s: float = 1.0,
    force: bool = False,
) -> tuple[dict[str, object], ContractRecord]:
    """Upload one document and wait for its record. Returns (final job, record)."""
    mime = PDF if path.suffix.lower() == ".pdf" else TEXT
    response = client.post(
        "/v1/extractions",
        params={"force": force},
        files={"file": (path.name, path.read_bytes(), mime)},
    )
    response.raise_for_status()
    accepted = response.json()
    deadline = time.monotonic() + timeout_s
    while True:
        job = client.get(accepted["status_url"]).raise_for_status().json()
        if job["status"] in DONE:
            break
        if time.monotonic() > deadline:
            raise TimeoutError(f"job {accepted['job_id']} still {job['status']} after {timeout_s}s")
        time.sleep(poll_s)
    if job["status"] == "failed":
        raise ExtractionFailedError(f"job {job['job_id']} failed: {job.get('error')}")
    record = client.get(accepted["record_url"]).raise_for_status().json()
    return job, ContractRecord.model_validate(record)
