import httpx
import pytest
from structlog.testing import capture_logs

from dip.service import queue
from dip.service.queue import HttpQueue, InlineQueue


def _fake_post(statuses: list[int | Exception], seen: list[dict]):
    def post(url: str, **kwargs: object) -> httpx.Response:
        seen.append({"url": url, **kwargs})
        outcome = statuses[len(seen) - 1]
        if isinstance(outcome, Exception):
            raise outcome
        return httpx.Response(outcome)

    return post


@pytest.fixture(autouse=True)
def _no_sleep(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(queue.time, "sleep", lambda _s: None)


def test_http_queue_stops_on_the_first_non_5xx(monkeypatch: pytest.MonkeyPatch) -> None:
    seen: list[dict] = []
    monkeypatch.setattr(queue.httpx, "post", _fake_post([503, 200], seen))

    HttpQueue("http://worker:8080/", "tok")._deliver("j1")

    assert len(seen) == 2
    assert seen[0]["url"] == "http://worker:8080/internal/process"
    assert seen[0]["headers"] == {"X-Internal-Token": "tok"}
    assert seen[0]["json"] == {"job_id": "j1"}


def test_http_queue_logs_when_it_gives_up(monkeypatch: pytest.MonkeyPatch) -> None:
    seen: list[dict] = []
    down = httpx.ConnectError("refused")
    monkeypatch.setattr(queue.httpx, "post", _fake_post([down, 500, down], seen))

    with capture_logs() as logs:
        HttpQueue("http://worker:8080", None)._deliver("j1")

    assert len(seen) == 3
    assert [e["event"] for e in logs] == [*["queue.delivery_failed"] * 3, "queue.gave_up"]
    assert [e.get("error") for e in logs[:3]] == ["ConnectError", "HTTP 500", "ConnectError"]


def test_inline_queue_redelivers_until_success() -> None:
    calls: list[str] = []

    def flaky(job_id: str) -> None:
        calls.append(job_id)
        if len(calls) < 3:
            raise RuntimeError("try again")

    q = InlineQueue(flaky, backoff_s=0)
    q.enqueue("j1")
    q.drain()
    assert calls == ["j1"] * 3
