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


@lru_cache
def get_settings() -> Settings:
    return Settings()
