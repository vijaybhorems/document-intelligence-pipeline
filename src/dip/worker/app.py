"""The worker: receives one job at a time from the queue (SPEC §5).

Run: ``uvicorn dip.worker.app:create_app --factory --port 8081``. Only the queue
may call it (``/internal/*`` auth). A 5xx response makes the queue retry; a
finished or permanently failed job answers 200 so the queue stops.
"""

from collections.abc import AsyncIterator, MutableMapping
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request
from pydantic import BaseModel

from dip.config import Environment, get_settings
from dip.observability.logging import configure_logging
from dip.observability.tracing import shutdown_tracing, start_tracing
from dip.service import problems
from dip.service.auth import check_internal
from dip.service.backends import Services, build_services

PROBES = frozenset({"/health", "/ready"})


class ProcessRequest(BaseModel):
    job_id: str


def create_app(services: Services | None = None) -> FastAPI:
    settings = services.settings if services else get_settings()
    configure_logging(settings.log_level, json=settings.env is not Environment.LOCAL)
    svc = services or build_services(settings)

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        # The worker is the only process that calls OpenAI, so it is the one that traces.
        start_tracing(settings)
        yield
        shutdown_tracing()  # flush spans on SIGTERM; Cloud Run gives 10 s

    app = FastAPI(
        title="dip worker",
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
        lifespan=lifespan,
        # FastAPI's built-in spans: keep one request span per job as the trace root, but
        # not one per health probe (every few seconds) or per dependency/serialization step.
        telemetry={"operation_spans": False, "exclude": _is_probe},
    )
    problems.install(app)

    @app.get("/health", include_in_schema=False)
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/internal/process")
    def process(body: ProcessRequest, request: Request) -> dict[str, str]:
        # Sync endpoint: FastAPI runs it in a thread pool, so the pipeline's asyncio.run is safe.
        check_internal(request, svc.settings)
        svc.process(body.job_id)
        job = svc.jobs.get(body.job_id)
        return {"job_id": body.job_id, "status": job.status.value if job else "unknown"}

    app.state.services = svc
    return app


def _is_probe(scope: MutableMapping[str, Any]) -> bool:
    return scope.get("path") in PROBES
