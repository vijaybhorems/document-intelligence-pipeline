"""The worker: receives one job at a time from the queue (SPEC §5).

Run: ``uvicorn dip.worker.app:create_app --factory --port 8081``. Only the queue
may call it (``/internal/*`` auth). A 5xx response makes the queue retry; a
finished or permanently failed job answers 200 so the queue stops.
"""

from fastapi import FastAPI, Request
from pydantic import BaseModel

from dip.config import Environment, get_settings
from dip.observability.logging import configure_logging
from dip.service import problems
from dip.service.auth import check_internal
from dip.service.backends import Services, build_services


class ProcessRequest(BaseModel):
    job_id: str


def create_app(services: Services | None = None) -> FastAPI:
    settings = services.settings if services else get_settings()
    configure_logging(settings.log_level, json=settings.env is not Environment.LOCAL)
    svc = services or build_services(settings)
    app = FastAPI(title="dip worker", docs_url=None, redoc_url=None, openapi_url=None)
    problems.install(app)

    @app.get("/healthz", include_in_schema=False)
    def healthz() -> dict[str, str]:
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
