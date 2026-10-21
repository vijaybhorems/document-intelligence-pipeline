"""Runtime configuration.

Every tunable lives here and is read from environment variables prefixed ``DIP_``
(or a local ``.env`` file). Code never reads ``os.environ`` directly.
Secrets are typed as ``SecretStr`` so they are masked in reprs and logs.
"""

from enum import StrEnum
from functools import lru_cache
from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(StrEnum):
    LOCAL = "local"
    DEV = "dev"
    PROD = "prod"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="DIP_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    env: Environment = Environment.LOCAL
    log_level: str = "INFO"
    data_dir: Path = Path("data")

    # Filled in later phases. Optional now so the app starts without them.
    openai_api_key: SecretStr | None = None
    gcp_project: str | None = None

    # Extraction (Phase 3). Model choice is decision D2; see docs/adr/.
    extraction_model: str = "gpt-5.6-luna"
    reasoning_effort: str = "low"
    max_concurrency: int = 8  # parallel API calls
    request_timeout_s: float = 180.0
    # Total spend allowed across all eval runs recorded in data/runs (SPEC §19).
    budget_usd: float = 10.0

    # Service (SPEC §12). "local": filesystem + in-memory jobs + in-process queue (dev, tests).
    # "gcp": GCS + Firestore + Cloud Tasks (also works against their local emulators).
    backend: str = "local"
    service_dir: Path = Path("data/service")  # local backend storage
    gcs_bucket: str | None = None
    firestore_collection: str = "jobs"
    tasks_queue: str | None = None  # projects/<p>/locations/<l>/queues/<q>
    queue_backend: str | None = (
        None  # inline | http | cloudtasks; default: inline locally, else cloudtasks
    )
    worker_url: str = "http://localhost:8081"  # where the queue delivers jobs
    tasks_invoker_email: str | None = None  # the service account Cloud Tasks signs as
    api_keys: SecretStr | None = None  # comma-separated; unset = auth off (local only)
    internal_token: SecretStr | None = None  # local shared secret for /internal/*
    max_upload_mb: int = 25
    max_pages: int = 300
    wait_max_seconds: float = 60.0

    # Tracing (SPEC §11). Unset = off. Local Phoenix: http://localhost:6006/v1/traces
    otel_endpoint: str | None = None
    trace_content: bool = True  # include prompt/response text in spans

    @property
    def queue_kind(self) -> str:
        """How jobs reach the worker; it also decides how the worker authenticates them."""
        return self.queue_backend or ("inline" if self.backend == "local" else "cloudtasks")


@lru_cache
def get_settings() -> Settings:
    return Settings()
