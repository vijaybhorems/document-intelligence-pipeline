from typer.testing import CliRunner

from dip import __version__
from dip.cli import app

runner = CliRunner()


def test_version_prints_package_version() -> None:
    result = runner.invoke(app, ["version"])

    assert result.exit_code == 0
    assert result.stdout.strip() == __version__


def test_info_masks_secrets(monkeypatch) -> None:
    monkeypatch.setenv("DIP_OPENAI_API_KEY", "sk-test-not-a-real-key")
    from dip.config import get_settings

    get_settings.cache_clear()
    try:
        result = runner.invoke(app, ["info"])
    finally:
        get_settings.cache_clear()

    assert result.exit_code == 0
    assert "sk-test-not-a-real-key" not in result.stdout
    assert "openai_api_key: **********" in result.stdout


def test_jobs_log_json_outside_local(monkeypatch) -> None:
    # Cloud Run Jobs' alerts match jsonPayload.message; console logs would never fire them.
    from dip import cli
    from dip.config import get_settings

    calls: list[bool] = []
    monkeypatch.setattr(
        "dip.observability.logging.configure_logging", lambda level, json: calls.append(json)
    )
    for env in ("dev", "local"):
        monkeypatch.setenv("DIP_ENV", env)
        get_settings.cache_clear()
        try:
            assert runner.invoke(cli.app, ["version"]).exit_code == 0
        finally:
            get_settings.cache_clear()
    assert calls == [True, False]
