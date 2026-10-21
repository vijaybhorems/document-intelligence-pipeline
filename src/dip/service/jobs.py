"""Jobs: the state of one extraction request (SPEC §5, ADR I4).

``queued -> routing -> extracting -> validating -> succeeded | partially_succeeded | failed``

``partially_succeeded`` means a record exists but some extraction call failed
(refusal, truncation): fields from that call are empty and listed as issues.
"""

import datetime as dt
import threading
from enum import StrEnum
from typing import Any, Protocol

from pydantic import BaseModel


class JobStatus(StrEnum):
    QUEUED = "queued"
    ROUTING = "routing"
    EXTRACTING = "extracting"
    VALIDATING = "validating"
    SUCCEEDED = "succeeded"
    PARTIALLY_SUCCEEDED = "partially_succeeded"
    FAILED = "failed"

    @property
    def done(self) -> bool:
        return self in (JobStatus.SUCCEEDED, JobStatus.PARTIALLY_SUCCEEDED, JobStatus.FAILED)


class Job(BaseModel):
    job_id: str
    status: JobStatus = JobStatus.QUEUED
    created_at: dt.datetime
    updated_at: dt.datetime
    document_sha256: str
    document_key: str
    mime: str
    filename: str
    pages: int | None = None
    pipeline_version: str
    idempotency_key: str | None = None
    attempts: int = 0
    sweeps: int = 0  # times the sweeper re-sent this job (dip.service.sweeper)
    record_key: str | None = None
    record_id: str | None = None
    cost_usd: float | None = None
    seconds: float | None = None
    error: str | None = None


def now() -> dt.datetime:
    return dt.datetime.now(dt.UTC)


class JobStore(Protocol):
    def create(self, job: Job) -> None: ...
    def get(self, job_id: str) -> Job | None: ...
    def update(self, job_id: str, **changes: Any) -> Job: ...
    def find_reusable(self, sha256: str, pipeline_version: str) -> Job | None:
        """A finished, successful job for the same bytes and pipeline: reuse it (idempotency)."""
        ...

    def find_by_idempotency_key(self, key: str) -> Job | None: ...

    def find_stale(self, before: dt.datetime, limit: int = 100) -> list[Job]:
        """Unfinished jobs not updated since ``before`` (oldest first)."""
        ...

    def count_queued(self) -> int: ...


ACTIVE = (JobStatus.QUEUED, JobStatus.ROUTING, JobStatus.EXTRACTING, JobStatus.VALIDATING)


class MemoryJobStore:
    """Process-local, thread-safe. For dev and tests; lost on restart."""

    def __init__(self) -> None:
        self._jobs: dict[str, Job] = {}
        self._lock = threading.Lock()

    def create(self, job: Job) -> None:
        with self._lock:
            self._jobs[job.job_id] = job

    def get(self, job_id: str) -> Job | None:
        with self._lock:
            return self._jobs.get(job_id)

    def update(self, job_id: str, **changes: Any) -> Job:
        with self._lock:
            job = self._jobs[job_id].model_copy(update={**changes, "updated_at": now()})
            self._jobs[job_id] = job
            return job

    def find_reusable(self, sha256: str, pipeline_version: str) -> Job | None:
        with self._lock:
            return next(
                (
                    j
                    for j in sorted(self._jobs.values(), key=lambda j: j.created_at, reverse=True)
                    if j.document_sha256 == sha256
                    and j.pipeline_version == pipeline_version
                    and j.status is JobStatus.SUCCEEDED
                ),
                None,
            )

    def find_by_idempotency_key(self, key: str) -> Job | None:
        with self._lock:
            return next((j for j in self._jobs.values() if j.idempotency_key == key), None)

    def find_stale(self, before: dt.datetime, limit: int = 100) -> list[Job]:
        with self._lock:
            stale = [j for j in self._jobs.values() if j.status in ACTIVE and j.updated_at < before]
        return sorted(stale, key=lambda j: j.updated_at)[:limit]

    def count_queued(self) -> int:
        with self._lock:
            return sum(j.status is JobStatus.QUEUED for j in self._jobs.values())


class FirestoreJobStore:
    """Honours ``FIRESTORE_EMULATOR_HOST`` for local runs."""

    def __init__(self, collection: str) -> None:
        from google.cloud import firestore

        self._collection = firestore.Client().collection(collection)

    def create(self, job: Job) -> None:
        self._collection.document(job.job_id).create(job.model_dump(mode="json"))

    def get(self, job_id: str) -> Job | None:
        snapshot = self._collection.document(job_id).get()
        return Job.model_validate(snapshot.to_dict()) if snapshot.exists else None

    def update(self, job_id: str, **changes: Any) -> Job:
        # Validate the merged job, but write only the changed fields: Firestore applies
        # field updates atomically, so a retried delivery can't clobber newer fields.
        job = Job.model_validate(
            {**self._require(job_id).model_dump(), **changes, "updated_at": now()}
        )
        data = job.model_dump(mode="json")
        self._collection.document(job_id).update({k: data[k] for k in [*changes, "updated_at"]})
        return job

    def _require(self, job_id: str) -> Job:
        job = self.get(job_id)
        if job is None:
            raise KeyError(job_id)
        return job

    def find_reusable(self, sha256: str, pipeline_version: str) -> Job | None:
        from google.cloud.firestore_v1.base_query import FieldFilter

        query = (
            self._collection.where(filter=FieldFilter("document_sha256", "==", sha256))
            .where(filter=FieldFilter("pipeline_version", "==", pipeline_version))
            .where(filter=FieldFilter("status", "==", JobStatus.SUCCEEDED.value))
            .limit(1)
        )
        docs = list(query.stream())
        return Job.model_validate(docs[0].to_dict()) if docs else None

    def find_by_idempotency_key(self, key: str) -> Job | None:
        from google.cloud.firestore_v1.base_query import FieldFilter

        docs = list(
            self._collection.where(filter=FieldFilter("idempotency_key", "==", key))
            .limit(1)
            .stream()
        )
        return Job.model_validate(docs[0].to_dict()) if docs else None

    def find_stale(self, before: dt.datetime, limit: int = 100) -> list[Job]:
        # status == X and updated_at < T: needs the composite index (status, updated_at)
        # in infra/terraform/storage.tf. Timestamps are stored as ISO-8601 UTC strings,
        # which sort like the instants they name (to the second).
        from google.cloud.firestore_v1.base_query import FieldFilter

        cutoff = before.astimezone(dt.UTC).isoformat().replace("+00:00", "Z")
        found: list[Job] = []
        for status in ACTIVE:
            query = (
                self._collection.where(filter=FieldFilter("status", "==", status.value))
                .where(filter=FieldFilter("updated_at", "<", cutoff))
                .order_by("updated_at")
                .limit(limit)
            )
            found += [Job.model_validate(d.to_dict()) for d in query.stream()]
        return sorted(found, key=lambda j: j.updated_at)[:limit]

    def count_queued(self) -> int:
        # An aggregation query: billed as one read per 1,000 index entries, not per job.
        from google.cloud.firestore_v1.base_query import FieldFilter

        query = self._collection.where(filter=FieldFilter("status", "==", JobStatus.QUEUED.value))
        (result,) = query.count().get()
        return int(result[0].value)
