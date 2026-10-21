"""Load test: every contract in the manifest through the live service (SPEC §12.1, Phase 9).

    uv run python loadtest/prepare.py
    uv run locust -f loadtest/locustfile.py --headless -u 10 -r 1 \
        --host "$(terraform -chdir=infra/terraform output -raw api_url)" \
        --csv data/loadtest/locust --run-time 30m

Each simulated user takes the next contract, uploads it, polls its status every 2 s
until the job is done, then fetches the record. Ten users keep ten jobs in flight,
more than the queue dispatches at once (4), so jobs wait in Cloud Tasks: that's the
backpressure being measured. Results:

- Locust's own stats (``--csv``): latency of each endpoint (upload, status, record).
- ``data/loadtest/jobs.csv``: one row per contract, with end-to-end seconds (upload ->
  record available), time spent queued, route, pages and cost.

The run stops when the manifest is exhausted, or once recorded spend reaches
``DIP_LOADTEST_MAX_USD`` (default $1.50): no new uploads after that.
"""

import csv
import json
import os
import threading
import time
from pathlib import Path

from dotenv import dotenv_values
from locust import HttpUser, events, task
from locust.exception import StopUser

DATA = Path(os.environ.get("DIP_DATA_DIR", "data"))
MANIFEST = json.loads((DATA / "loadtest" / "manifest.json").read_text())
MAX_USD = float(os.environ.get("DIP_LOADTEST_MAX_USD", "1.50"))
API_KEY = os.environ.get("DIP_API_KEY") or dotenv_values(".env").get("DIP_API_KEY") or ""
POLL_S = 2.0
TIMEOUT_S = 1800.0

_lock = threading.Lock()
_next = iter(MANIFEST)
_spent = 0.0
_finished = 0
_results = DATA / "loadtest" / "jobs.csv"
_FIELDS = [
    "doc_id", "variant", "pages", "status", "route", "e2e_s", "queued_s",
    "worker_s", "cost_usd", "attempts", "http_errors",
]  # fmt: skip


@events.test_start.add_listener
def _start(**_: object) -> None:
    with _results.open("w", newline="") as f:
        csv.DictWriter(f, _FIELDS).writeheader()


def _take() -> dict | None:
    with _lock:
        if _spent >= MAX_USD:
            return None
        return next(_next, None)


def _record(row: dict, runner: object) -> None:
    global _spent, _finished
    with _lock:
        _spent += float(row.get("cost_usd") or 0)
        _finished += 1
        with _results.open("a", newline="") as f:
            csv.DictWriter(f, _FIELDS).writerow(row)
        done = _finished >= len(MANIFEST) or _spent >= MAX_USD
    if done and runner is not None:
        runner.quit()  # type: ignore[attr-defined]


class Uploader(HttpUser):
    def on_start(self) -> None:
        self.client.headers["X-API-Key"] = API_KEY

    @task
    def one_contract(self) -> None:
        doc = _take()
        if doc is None:
            raise StopUser()
        started = time.monotonic()
        data = Path(doc["path"]).read_bytes()
        with self.client.post(
            "/v1/extractions",
            files={"file": (f"{doc['doc_id'][:80]}.pdf", data, "application/pdf")},
            params={"force": "true"},  # measure extraction, not the dedupe cache
            name="POST /v1/extractions",
            catch_response=True,
        ) as response:
            if response.status_code != 202:
                response.failure(f"{response.status_code}: {response.text[:200]}")
                return
            accepted = response.json()

        job, errors, first_running = {}, 0, None
        while time.monotonic() - started < TIMEOUT_S:
            time.sleep(POLL_S)
            r = self.client.get(accepted["status_url"], name="GET /v1/extractions/{id}")
            if r.status_code != 200:
                errors += 1
                continue
            job = r.json()
            if first_running is None and job["status"] != "queued":
                first_running = time.monotonic()
            if job["status"] in ("succeeded", "partially_succeeded", "failed"):
                break
        e2e = time.monotonic() - started

        record = {}
        if job.get("status") in ("succeeded", "partially_succeeded"):
            r = self.client.get(accepted["record_url"], name="GET /v1/extractions/{id}/record")
            record = r.json() if r.status_code == 200 else {}
        provenance = record.get("provenance", {})
        events.request.fire(  # end-to-end time as its own row in Locust's stats
            request_type="E2E",
            name=f"upload -> record ({doc['variant']})",
            response_time=e2e * 1000,
            response_length=0,
            exception=None if record else RuntimeError(job.get("status", "timeout")),
            context={},
        )
        _record(
            {
                "doc_id": doc["doc_id"],
                "variant": doc["variant"],
                "pages": doc["pages"],
                "status": job.get("status", "timeout"),
                "route": provenance.get("route"),
                "e2e_s": round(e2e, 1),
                "queued_s": round((first_running or time.monotonic()) - started, 1),
                "worker_s": provenance.get("seconds"),
                "cost_usd": provenance.get("cost_usd", 0),
                "attempts": job.get("attempts"),
                "http_errors": errors,
            },
            self.environment.runner,
        )
