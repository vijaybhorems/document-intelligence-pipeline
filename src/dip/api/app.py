"""The public API (SPEC §12). Run: ``uvicorn dip.api.app:create_app --factory``."""

import asyncio
import hashlib
import time
import uuid
from typing import Annotated

from fastapi import Depends, FastAPI, File, Form, Header, HTTPException, Query, Request, UploadFile
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from dip import __version__
from dip.analytics.queries import QUERIES, QueryError
from dip.config import Environment, get_settings
from dip.observability.logging import configure_logging
from dip.schema.domain import ContractRecord
from dip.service import problems
from dip.service.auth import check_api_key
from dip.service.backends import Services, build_services
from dip.service.jobs import Job, JobStatus, now
from dip.service.uploads import EXTENSIONS, UploadError, check


class Accepted(BaseModel):
    job_id: str
    status: JobStatus
    status_url: str
    record_url: str
    deduplicated: bool = False


def create_app(services: Services | None = None) -> FastAPI:
    settings = services.settings if services else get_settings()
    configure_logging(settings.log_level, json=settings.env is not Environment.LOCAL)
    svc = services or build_services(settings)
    app = FastAPI(
        title="Document Intelligence Pipeline",
        version=__version__,
        docs_url=None if settings.env is Environment.PROD else "/docs",
        redoc_url=None,
    )
    problems.install(app)

    def authorized(request: Request) -> None:
        check_api_key(request, svc.settings)

    auth = [Depends(authorized)]

    def accepted(job: Job, deduplicated: bool = False) -> Accepted:
        base = f"/v1/extractions/{job.job_id}"
        return Accepted(
            job_id=job.job_id,
            status=job.status,
            status_url=base,
            record_url=f"{base}/record",
            deduplicated=deduplicated,
        )

    def load_record(job: Job) -> ContractRecord:
        if job.status is JobStatus.FAILED:
            raise HTTPException(409, f"job failed: {job.error}")
        if not job.status.done or job.record_key is None:
            raise HTTPException(409, f"job is {job.status.value}; poll the status URL")
        return ContractRecord.model_validate_json(svc.blobs.get(job.record_key))

    @app.get("/health", include_in_schema=False)
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/ready", include_in_schema=False)
    def ready() -> dict[str, str]:
        svc.blobs.exists("ready-probe")  # touches storage; raises if unreachable
        return {"status": "ready", "backend": svc.settings.backend}

    @app.get("/v1/schema", dependencies=auth)
    def schema() -> dict[str, object]:
        return ContractRecord.model_json_schema()

    @app.post("/v1/extractions", status_code=202, response_model=None, dependencies=auth)
    async def create_extraction(
        request: Request,
        file: Annotated[UploadFile, File(description="PDF or UTF-8 text")],
        filename: Annotated[str | None, Form()] = None,
        wait: Annotated[bool, Query(description="Wait up to 60 s for the record")] = False,
        force: Annotated[bool, Query(description="Re-extract even if already done")] = False,
        idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
    ) -> Accepted | ContractRecord | JSONResponse:
        limit = svc.settings.max_upload_mb * 1024 * 1024
        if int(request.headers.get("content-length") or 0) > limit + 1024 * 64:
            raise UploadError(
                413, "Document too large", f"limit is {svc.settings.max_upload_mb} MB"
            )
        data = await file.read(limit + 1)  # never buffer more than the limit
        upload = check(data, svc.settings.max_upload_mb, svc.settings.max_pages)
        sha = hashlib.sha256(data).hexdigest()

        if idempotency_key and (
            prior := await run_in_threadpool(svc.jobs.find_by_idempotency_key, idempotency_key)
        ):
            if prior.document_sha256 != sha:
                raise HTTPException(
                    409, "Idempotency-Key was already used for a different document"
                )
            return accepted(prior, deduplicated=True)
        version = svc.pipeline.version
        if not force and (reuse := await run_in_threadpool(svc.jobs.find_reusable, sha, version)):
            return await _respond(reuse, wait=wait, deduplicated=True)

        # Backpressure: past the backlog cap, refuse new work instead of queueing it for
        # hours. Cheap to check (one aggregation query) and only on new jobs.
        cap = svc.settings.max_queued_jobs
        if cap and await run_in_threadpool(svc.jobs.count_queued) >= cap:
            raise HTTPException(
                429, f"{cap} jobs are already waiting; retry later", headers={"Retry-After": "60"}
            )
        key = f"raw/{sha}.{EXTENSIONS[upload.mime]}"
        if not await run_in_threadpool(svc.blobs.exists, key):
            await run_in_threadpool(svc.blobs.put, key, data, upload.mime)
        created = now()
        job = Job(
            job_id=str(uuid.uuid4()),
            created_at=created,
            updated_at=created,
            document_sha256=sha,
            document_key=key,
            mime=upload.mime,
            filename=(filename or file.filename or "document")[:200],
            pages=upload.pages,
            pipeline_version=version,
            idempotency_key=idempotency_key,
        )
        await run_in_threadpool(svc.jobs.create, job)
        await run_in_threadpool(svc.queue.enqueue, job.job_id)
        return await _respond(job, wait=wait)

    async def _respond(
        job: Job, wait: bool, deduplicated: bool = False
    ) -> Accepted | ContractRecord | JSONResponse:
        if wait:
            deadline = time.monotonic() + svc.settings.wait_max_seconds
            while time.monotonic() < deadline:
                current = await run_in_threadpool(svc.jobs.get, job.job_id)
                if current and current.status.done:
                    if current.status is JobStatus.FAILED:
                        return problems.problem(422, "Extraction failed", current.error or "")
                    record = await run_in_threadpool(load_record, current)
                    # Explicit 200: the route's default status is 202 (accepted, not done).
                    return JSONResponse(record.model_dump(mode="json"), status_code=200)
                await asyncio.sleep(0.5)
        body = accepted(job, deduplicated)
        status = 200 if job.status.done else 202
        return JSONResponse(body.model_dump(mode="json"), status_code=status)

    @app.get("/v1/analytics", dependencies=auth)
    def analytics_index() -> dict[str, object]:
        return {
            "queries": [
                {
                    "name": q.name,
                    "description": q.description,
                    "params": [
                        {
                            "name": p.name,
                            "type": p.kind.__name__,
                            "default": p.default,
                            "description": p.description,
                        }
                        for p in q.params
                    ],
                }
                for q in QUERIES.values()
            ]
        }

    @app.get("/v1/analytics/{name}", dependencies=auth)
    def analytics(name: str, request: Request) -> dict[str, object]:
        """A whitelisted query over the lake (SPEC §9.3). Never raw SQL."""
        if name not in QUERIES:
            raise HTTPException(404, f"no query named {name!r}; see GET /v1/analytics")
        try:
            result = svc.lake.run(name, dict(request.query_params))
        except QueryError as exc:
            raise HTTPException(422, str(exc)) from exc
        return {
            "query": name,
            "params": QUERIES[name].bind(dict(request.query_params)),
            "columns": result.columns,
            "rows": result.rows,
            "generated_at": now(),
        }

    @app.get("/v1/extractions/{job_id}", dependencies=auth)
    def get_job(job_id: str) -> Job:
        job = svc.jobs.get(job_id)
        if job is None:
            raise HTTPException(404, "no such job")
        return job

    @app.get("/v1/extractions/{job_id}/record", dependencies=auth)
    def get_record(job_id: str) -> ContractRecord:
        job = svc.jobs.get(job_id)
        if job is None:
            raise HTTPException(404, "no such job")
        return load_record(job)

    app.state.services = svc
    return app
