"""What the worker does with one job: load, run the pipeline, store, update (SPEC §5)."""

import structlog

from dip.pipeline import Pipeline, Stage
from dip.service.blobs import BlobStore
from dip.service.jobs import Job, JobStatus, JobStore
from dip.service.usage import UsageStore

log = structlog.get_logger()
MAX_ATTEMPTS = 3  # then the job is marked failed and the queue stops retrying


def record_key(record_id: str, created: str) -> str:
    return f"records/dt={created[:10]}/{record_id}.json"


def _settle(usage: UsageStore | None, job: Job, actual_usd: float) -> None:
    """Replace the spend reserved at submission with what the job actually cost."""
    if usage is not None and job.principal and job.reserved_usd:
        usage.add_spend(job.principal, job.created_at.date(), actual_usd - job.reserved_usd)


def process_job(
    job_id: str,
    jobs: JobStore,
    blobs: BlobStore,
    pipeline: Pipeline,
    usage: UsageStore | None = None,
) -> None:
    """Idempotent: a finished job is left alone, so a redelivered task is harmless.

    Raises (so the worker answers 5xx and the queue retries) on a failure before the
    last attempt; on the last attempt the job is marked ``failed`` and this returns.
    """
    job = jobs.get(job_id)
    if job is None:
        log.warning("job.unknown", job_id=job_id)
        return
    if job.status.done:
        log.info("job.already_done", job_id=job_id, status=job.status)
        return
    bound = log.bind(job_id=job_id, doc_sha256=job.document_sha256[:12])
    jobs.update(job_id, attempts=job.attempts + 1)
    try:
        data = blobs.get(job.document_key)

        def on_stage(stage: Stage) -> None:
            jobs.update(job_id, status=JobStatus(stage.value))
            bound.info("job.stage", stage=stage.value)

        record = pipeline.process(data, job.mime, on_stage)
        key = record_key(record.record_id, record.created_at.isoformat())
        blobs.put(key, record.model_dump_json(indent=2).encode(), "application/json")
        failed_calls = [i for i in record.extraction_issues if i.split(":")[0] in ("all", "reask")]
        status = JobStatus.PARTIALLY_SUCCEEDED if failed_calls else JobStatus.SUCCEEDED
        jobs.update(
            job_id,
            status=status,
            record_key=key,
            record_id=record.record_id,
            cost_usd=record.provenance.cost_usd,
            seconds=record.provenance.seconds,
            error=None,
        )
        _settle(usage, job, record.provenance.cost_usd)
        bound.info(
            "job.done",
            status=status.value,
            route=record.provenance.route,
            cost_usd=round(record.provenance.cost_usd, 5),
            seconds=round(record.provenance.seconds, 2),
            issues=len(record.validation_issues),
        )
    except Exception as exc:
        # Never log document text; the type and message are enough to debug.
        error = f"{type(exc).__name__}: {exc}"[:500]
        if job.attempts + 1 < MAX_ATTEMPTS:
            # Back to the queue: re-raising makes the worker answer 5xx, so the queue retries.
            bound.warning("job.retrying", error=type(exc).__name__, attempt=job.attempts + 1)
            jobs.update(job_id, status=JobStatus.QUEUED, error=error)
            raise
        bound.exception("job.failed", error=type(exc).__name__, attempts=job.attempts + 1)
        jobs.update(job_id, status=JobStatus.FAILED, error=error)
        _settle(usage, job, 0.0)  # a failed job costs what its calls cost; none are billed back
        # Returning normally (2xx) tells the queue to stop retrying.
