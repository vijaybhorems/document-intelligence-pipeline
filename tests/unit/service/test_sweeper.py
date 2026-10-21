import datetime as dt

from fastapi.testclient import TestClient

from dip.api.app import create_app
from dip.service.backends import Services
from dip.service.jobs import Job, JobStatus, MemoryJobStore
from dip.service.sweeper import STALE_AFTER, sweep
from tests.unit.service.test_api import PDF_BYTES

T0 = dt.datetime(2026, 10, 21, 12, tzinfo=dt.UTC)


class Recorder:
    def __init__(self) -> None:
        self.sent: list[str] = []

    def enqueue(self, job_id: str) -> None:
        self.sent.append(job_id)


def _job(job_id: str, status: JobStatus, minutes_ago: int, sweeps: int = 0) -> Job:
    at = T0 - dt.timedelta(minutes=minutes_ago)
    return Job(
        job_id=job_id, status=status, created_at=at, updated_at=at, document_sha256="s",
        document_key="raw/s.pdf", mime="application/pdf", filename="c.pdf",
        pipeline_version="v", sweeps=sweeps,
    )  # fmt: skip


def _store(*jobs: Job) -> MemoryJobStore:
    store = MemoryJobStore()
    for job in jobs:
        store.create(job)
    return store


def test_sweeps_only_unfinished_jobs_idle_past_the_threshold() -> None:
    old = int(STALE_AFTER.total_seconds() // 60) + 5
    store = _store(
        _job("stuck-queued", JobStatus.QUEUED, old),
        _job("dead-worker", JobStatus.EXTRACTING, old),
        _job("recent", JobStatus.QUEUED, 5),  # Cloud Tasks may still be retrying it
        _job("finished", JobStatus.SUCCEEDED, old * 10),
    )
    queue = Recorder()

    report = sweep(store, queue, clock=lambda: T0)

    assert sorted(report.requeued) == ["dead-worker", "stuck-queued"]
    assert sorted(queue.sent) == ["dead-worker", "stuck-queued"]
    job = store.get("dead-worker")
    assert job is not None
    assert (job.status, job.sweeps) == (JobStatus.QUEUED, 1)


def test_gives_up_after_max_sweeps() -> None:
    store = _store(_job("hopeless", JobStatus.QUEUED, 120, sweeps=2))
    queue = Recorder()

    report = sweep(store, queue, clock=lambda: T0)

    job = store.get("hopeless")
    assert report.failed == ["hopeless"]
    assert queue.sent == []
    assert job is not None
    assert job.status is JobStatus.FAILED
    assert "stale" in (job.error or "")


def test_uploads_get_429_when_the_backlog_is_full(services: Services) -> None:
    services.settings = services.settings.model_copy(update={"max_queued_jobs": 1})
    services.jobs.create(_job("waiting", JobStatus.QUEUED, 1))
    client = TestClient(create_app(services))

    response = client.post(
        "/v1/extractions", files={"file": ("c.pdf", PDF_BYTES, "application/pdf")}
    )

    assert response.status_code == 429
    assert response.headers["retry-after"] == "60"
    assert response.headers["content-type"] == "application/problem+json"
