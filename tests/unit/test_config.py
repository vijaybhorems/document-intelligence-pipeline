from pathlib import Path

import pytest

from dip.config import Environment, Settings


@pytest.fixture(autouse=True)
def isolated_env(monkeypatch, tmp_path) -> None:
    """Run from an empty directory with no DIP_* variables, so a developer's .env can't leak in."""
    monkeypatch.chdir(tmp_path)
    for field in Settings.model_fields:
        monkeypatch.delenv(f"DIP_{field.upper()}", raising=False)


def test_defaults_need_no_environment() -> None:
    settings = Settings()

    assert settings.env is Environment.LOCAL
    assert settings.data_dir == Path("data")
    assert settings.openai_api_key is None


def test_reads_prefixed_environment_variables(monkeypatch) -> None:
    monkeypatch.setenv("DIP_ENV", "prod")
    monkeypatch.setenv("DIP_GCP_PROJECT", "dip-prod-123")

    settings = Settings()

    assert settings.env is Environment.PROD
    assert settings.gcp_project == "dip-prod-123"


def test_reads_dotenv_file(tmp_path) -> None:
    (tmp_path / ".env").write_text("DIP_LOG_LEVEL=DEBUG\n")

    assert Settings().log_level == "DEBUG"


def test_rejects_unknown_environment(monkeypatch) -> None:
    monkeypatch.setenv("DIP_ENV", "staging")

    with pytest.raises(ValueError, match="env"):
        Settings()
