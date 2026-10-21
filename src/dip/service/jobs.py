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
