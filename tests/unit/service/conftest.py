"""A real service stack (API + worker logic + local stores) around a fake OpenAI client."""

from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from dip.config import Settings
from dip.extract.extractor import OpenAIExtractor, Strategy
from dip.pipeline import Pipeline
from dip.service.backends import Services, build_services
from dip.service.queue import InlineQueue
from tests.unit.extract.test_extractor import ANSWERS, FakeResponses

CONTRACT = (
    "Distributor shall not assign this Agreement. "
    "This Agreement is governed by the laws of the State of Texas."
)


def make_pipeline(responses: FakeResponses) -> Pipeline:
    client: Any = SimpleNamespace(responses=responses)
    return Pipeline(OpenAIExtractor("gpt-5.6-luna", Strategy.SINGLE, client=client), reask=True)


@pytest.fixture
def responses() -> FakeResponses:
    return FakeResponses(ANSWERS)


@pytest.fixture
def services(tmp_path: Path, responses: FakeResponses) -> Services:
    settings = Settings(backend="local", service_dir=tmp_path / "service", wait_max_seconds=10)
    svc = build_services(settings, pipeline=make_pipeline(responses))
    assert isinstance(svc.queue, InlineQueue)
    return svc
