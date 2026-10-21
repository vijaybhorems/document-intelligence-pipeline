"""Build the service's dependencies from settings (one place to swap local for GCP)."""

from collections.abc import Callable
from dataclasses import dataclass, field

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


def build_services(
    settings: Settings, pipeline: Pipeline | None = None, queue: TaskQueue | None = None
) -> Services:
    if settings.backend == "local":
        jobs: JobStore = MemoryJobStore()
        blobs: BlobStore = LocalBlobStore(settings.service_dir)
    elif settings.backend == "gcp":
        if not settings.gcs_bucket:
            raise ValueError("DIP_GCS_BUCKET is required for the gcp backend")
        jobs = FirestoreJobStore(settings.firestore_collection)
        blobs = GcsBlobStore(settings.gcs_bucket)
    else:
        raise ValueError(f"unknown backend {settings.backend!r}")
    services = Services(settings, jobs, blobs, pipeline or default_pipeline(settings))
    services.queue = queue or _queue(settings, services.process)
    return services


def _queue(settings: Settings, process: Callable[[str], None]) -> TaskQueue:
    kind = settings.queue_backend or ("inline" if settings.backend == "local" else "cloudtasks")
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
