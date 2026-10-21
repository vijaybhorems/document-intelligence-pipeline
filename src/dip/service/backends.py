"""Build the service's dependencies from settings (one place to swap local for GCP)."""

from collections.abc import Callable
from dataclasses import dataclass, field

from dip.analytics.queries import GoogleToken, Lake
from dip.config import Settings
from dip.extract.extractor import OpenAIExtractor, Strategy
from dip.pipeline import Pipeline
from dip.service.blobs import BlobStore, GcsBlobStore, LocalBlobStore
from dip.service.jobs import FirestoreJobStore, JobStore, MemoryJobStore
from dip.service.processing import process_job
from dip.service.queue import CloudTasksQueue, HttpQueue, InlineQueue, TaskQueue


@dataclass
class Services:
    settings: Settings
    jobs: JobStore
    blobs: BlobStore
    pipeline: Pipeline
    lake: Lake
    queue: TaskQueue = field(init=False)

    def process(self, job_id: str) -> None:
        process_job(job_id, self.jobs, self.blobs, self.pipeline)


def default_pipeline(settings: Settings) -> Pipeline:
    """The decided configuration: D1 hybrid, D2 luna, D4 single call, D5 v4, D6 re-ask."""
    key = settings.openai_api_key.get_secret_value() if settings.openai_api_key else None
    extractor = OpenAIExtractor(
        model=settings.extraction_model,
        strategy=Strategy.SINGLE,
        reasoning_effort=settings.reasoning_effort,
        max_concurrency=settings.max_concurrency,
        timeout_s=settings.request_timeout_s,
        api_key=key,
    )
    return Pipeline(extractor, reask=True)


def build_blobs(settings: Settings) -> BlobStore:
    if settings.backend == "local":
        return LocalBlobStore(settings.service_dir)
    if settings.backend == "gcp":
        if not settings.gcs_bucket:
            raise ValueError("DIP_GCS_BUCKET is required for the gcp backend")
        return GcsBlobStore(settings.gcs_bucket)
    raise ValueError(f"unknown backend {settings.backend!r}")


def build_jobs(settings: Settings) -> JobStore:
    if settings.backend == "gcp":
        return FirestoreJobStore(settings.firestore_collection)
    return MemoryJobStore()


def build_lake(settings: Settings, blobs: BlobStore) -> Lake:
    if settings.backend == "gcp":
        return Lake(
            f"gs://{settings.gcs_bucket}/lake",
            blobs,
            token=GoogleToken(),
            extension_dir=settings.duckdb_extension_dir,
        )
    return Lake(str(settings.service_dir.resolve() / "lake"), blobs)


def build_queue(settings: Settings, jobs: JobStore, blobs: BlobStore) -> TaskQueue:
    """The queue alone (the sweeper): the inline queue gets a pipeline only if it runs jobs."""

    def process(job_id: str) -> None:
        process_job(job_id, jobs, blobs, default_pipeline(settings))

    return _queue(settings, process)


def build_services(
    settings: Settings, pipeline: Pipeline | None = None, queue: TaskQueue | None = None
) -> Services:
    blobs = build_blobs(settings)
    jobs = build_jobs(settings)
    lake = build_lake(settings, blobs)
    services = Services(settings, jobs, blobs, pipeline or default_pipeline(settings), lake)
    services.queue = queue or _queue(settings, services.process)
    return services


def _queue(settings: Settings, process: Callable[[str], None]) -> TaskQueue:
    kind = settings.queue_kind
    token = settings.internal_token.get_secret_value() if settings.internal_token else None
    if kind == "inline":
        return InlineQueue(process)
    if kind == "http":
        return HttpQueue(settings.worker_url, token)
    if kind == "cloudtasks":
        if not (settings.tasks_queue and settings.tasks_invoker_email):
            raise ValueError("DIP_TASKS_QUEUE and DIP_TASKS_INVOKER_EMAIL are required")
        return CloudTasksQueue(
            settings.tasks_queue, settings.worker_url, settings.tasks_invoker_email
        )
    raise ValueError(f"unknown queue backend {kind!r}")
