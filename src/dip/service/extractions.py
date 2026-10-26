"""The service operations both interfaces share (SPEC §5): REST (dip.api) and MCP (dip.mcp_server).

Neither interface holds business logic: they translate requests into these calls and
the typed errors below into their own error shapes (HTTP problem details, or MCP
tool results with ``isError``).
"""

import hashlib
import uuid
from dataclasses import dataclass

from dip.schema.domain import ContractRecord
from dip.service.backends import Services
from dip.service.jobs import Job, JobStatus, now
from dip.service.uploads import EXTENSIONS, check
from dip.service.usage import RESERVE_USD_PER_PAGE, LimitExceededError, admit


class ServiceError(Exception):
    status = 400


class ConflictError(ServiceError):
    status = 409


class BusyError(ServiceError):
    """Backpressure, a rate limit or a spend cap: try again later."""

    status = 429

    def __init__(self, message: str, retry_after_s: int = 60) -> None:
        super().__init__(message)
        self.retry_after_s = retry_after_s


class NotReadyError(ServiceError):
    status = 409

    def __init__(self, job: Job) -> None:
        super().__init__(f"job is {job.status.value}; poll its status")
        self.job = job


class JobFailedError(ServiceError):
    status = 409


@dataclass(frozen=True)
class Submission:
    job: Job
    deduplicated: bool


def submit(
    svc: Services,
    data: bytes,
    filename: str,
    *,
    idempotency_key: str | None = None,
    force: bool = False,
    principal: str | None = None,
    daily_cap_usd: float | None = None,
) -> Submission:
    """Validate, dedupe, store and enqueue one document. Raises UploadError or a ServiceError."""
    upload = check(data, svc.settings.max_upload_mb, svc.settings.max_pages)
    sha = hashlib.sha256(data).hexdigest()

    if idempotency_key and (prior := svc.jobs.find_by_idempotency_key(idempotency_key)):
        if prior.document_sha256 != sha:
            raise ConflictError("Idempotency-Key was already used for a different document")
        return Submission(prior, deduplicated=True)
    version = svc.pipeline.version
    if not force and (reuse := svc.jobs.find_reusable(sha, version)):
        return Submission(reuse, deduplicated=True)

    # Backpressure: past the backlog cap, refuse new work instead of queueing it for
    # hours. Cheap to check (one aggregation query) and only on new jobs.
    cap = svc.settings.max_queued_jobs
    if cap and svc.jobs.count_queued() >= cap:
        raise BusyError(f"{cap} jobs are already waiting; retry later")

    reserved = 0.0
    if principal is not None and daily_cap_usd is not None:
        reserved = RESERVE_USD_PER_PAGE * (upload.pages or 1)
        try:
            admit(
                svc.usage,
                principal,
                now(),
                per_minute=svc.settings.mcp_submissions_per_minute,
                daily_cap_usd=daily_cap_usd,
                reserve_usd=reserved,
            )
        except LimitExceededError as exc:
            raise BusyError(str(exc), retry_after_s=exc.retry_after_s) from exc

    key = f"raw/{sha}.{EXTENSIONS[upload.mime]}"
    if not svc.blobs.exists(key):
        svc.blobs.put(key, data, upload.mime)
    created = now()
    job = Job(
        job_id=str(uuid.uuid4()),
        created_at=created,
        updated_at=created,
        document_sha256=sha,
        document_key=key,
        mime=upload.mime,
        filename=filename[:200] or "document",
        pages=upload.pages,
        pipeline_version=version,
        idempotency_key=idempotency_key,
        principal=principal,
        reserved_usd=reserved,
    )
    svc.jobs.create(job)
    svc.queue.enqueue(job.job_id)
    return Submission(job, deduplicated=False)


def record_for_job(svc: Services, job: Job) -> ContractRecord:
    if job.status is JobStatus.FAILED:
        raise JobFailedError(f"job failed: {job.error}")
    if not job.status.done or job.record_key is None:
        raise NotReadyError(job)
    return ContractRecord.model_validate_json(svc.blobs.get(job.record_key))


def find_record(svc: Services, record_id: str) -> ContractRecord | None:
    """By record id. Records live under their creation date, which the id doesn't carry,
    so this lists ``records/``: fine at this scale; an index would replace it at more."""
    suffix = f"/{record_id}.json"
    for info in svc.blobs.list("records/"):
        if info.key.endswith(suffix):
            return ContractRecord.model_validate_json(svc.blobs.get(info.key))
    return None
