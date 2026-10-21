"""Task queue: how a job reaches the worker (SPEC §5, ADR I2).

- ``InlineQueue``: runs the job in a background thread in the same process, redelivering
  on failure like the others. Dev and tests.
- ``HttpQueue``: POSTs to the worker's ``/internal/process`` with retries. docker compose.
- ``CloudTasksQueue``: Cloud Tasks with an OIDC token for the worker. Production: retries,
  backoff and a dispatch rate cap that protects the OpenAI quota.
"""

import json
import threading
import time
from collections.abc import Callable
from typing import Protocol

import httpx
import structlog

log = structlog.get_logger()


class TaskQueue(Protocol):
    def enqueue(self, job_id: str) -> None: ...


class InlineQueue:
    def __init__(
        self, process: Callable[[str], None], attempts: int = 3, backoff_s: float = 0.5
    ) -> None:
        self._process = process
        self.attempts = attempts
        self.backoff_s = backoff_s
        self._threads: list[threading.Thread] = []

    def _deliver(self, job_id: str) -> None:
        # process_job raises to ask for a redelivery (a 5xx, to the real queues).
        for attempt in range(self.attempts):
            try:
                self._process(job_id)
                return
            except Exception:  # already logged and recorded on the job by process_job
                time.sleep(self.backoff_s * 2**attempt)

    def enqueue(self, job_id: str) -> None:
        thread = threading.Thread(target=self._deliver, args=(job_id,), daemon=True)
        self._threads.append(thread)
        thread.start()

    def drain(self, timeout: float = 30.0) -> None:
        """Wait for queued jobs (tests)."""
        for thread in self._threads:
            thread.join(timeout)


class HttpQueue:
    """Fire-and-forget delivery with retries, like Cloud Tasks, without the emulator."""

    def __init__(self, worker_url: str, token: str | None, attempts: int = 3) -> None:
        self.url = worker_url.rstrip("/") + "/internal/process"
        self.token = token
        self.attempts = attempts

    def _deliver(self, job_id: str) -> None:
        headers = {"X-Internal-Token": self.token} if self.token else {}
        for attempt in range(1, self.attempts + 1):
            try:
                response = httpx.post(
                    self.url, json={"job_id": job_id}, headers=headers, timeout=600
                )
                if response.status_code < 500:
                    return
                problem: str = f"HTTP {response.status_code}"
            except httpx.HTTPError as exc:
                problem = type(exc).__name__
            log.warning("queue.delivery_failed", job_id=job_id, attempt=attempt, error=problem)
            if attempt < self.attempts:
                time.sleep(2 ** (attempt - 1))
        # The job stays queued: nothing will pick it up again (see SPEC §20, stale jobs).
        log.error("queue.gave_up", job_id=job_id, attempts=self.attempts)

    def enqueue(self, job_id: str) -> None:
        threading.Thread(target=self._deliver, args=(job_id,), daemon=True).start()


class CloudTasksQueue:
    def __init__(
        self, queue: str, worker_url: str, invoker_email: str, deadline_s: int = 900
    ) -> None:
        from google.cloud import tasks_v2

        self._client = tasks_v2.CloudTasksClient()
        self._tasks_v2 = tasks_v2
        self.queue = queue
        self.url = worker_url.rstrip("/") + "/internal/process"
        self.invoker_email = invoker_email
        self.audience = worker_url.rstrip("/")
        # How long Cloud Tasks waits for the worker before calling it a failure and
        # redelivering. Default 10 min; match the worker's Cloud Run timeout (15 min) so a
        # long scan isn't retried while the first attempt is still running.
        self.deadline_s = deadline_s

    def enqueue(self, job_id: str) -> None:
        from google.protobuf import duration_pb2

        t = self._tasks_v2
        task = t.Task(
            http_request=t.HttpRequest(
                http_method=t.HttpMethod.POST,
                url=self.url,
                headers={"Content-Type": "application/json"},
                body=json.dumps({"job_id": job_id}).encode(),
                oidc_token=t.OidcToken(
                    service_account_email=self.invoker_email, audience=self.audience
                ),
            ),
            dispatch_deadline=duration_pb2.Duration(seconds=self.deadline_s),
        )
        self._client.create_task(parent=self.queue, task=task)
