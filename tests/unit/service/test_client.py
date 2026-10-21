from pathlib import Path
from typing import cast

import httpx
import pytest
from fastapi.testclient import TestClient

from dip.api.app import create_app
from dip.service import client as api_client
from dip.service.backends import Services
from tests.pdfs import text_pdf
from tests.unit.service.conftest import CONTRACT


def test_submit_uploads_polls_and_returns_a_valid_record(
    services: Services, tmp_path: Path
) -> None:
    pdf = tmp_path / "c.pdf"
    pdf.write_bytes(text_pdf([[CONTRACT] * 3]))

    job, record = api_client.submit(_client(services), pdf, poll_s=0.01)

    assert job["status"] == "succeeded"
    assert record.provenance.route == "text"
    assert record.fields.governing_law.values == ["Texas"]


def test_submit_raises_on_a_failed_job(services: Services, tmp_path: Path) -> None:
    services.pipeline.process = _boom  # type: ignore[method-assign]
    pdf = tmp_path / "c.pdf"
    pdf.write_bytes(text_pdf([[CONTRACT]]))

    with pytest.raises(api_client.ExtractionFailedError):
        api_client.submit(_client(services), pdf, poll_s=0.01, timeout_s=10)


def _boom(*_args: object, **_kwargs: object) -> None:
    raise RuntimeError("model unavailable")


def _client(services: Services) -> httpx.Client:
    # TestClient has httpx.Client's interface without subclassing it.
    return cast(httpx.Client, TestClient(create_app(services)))
