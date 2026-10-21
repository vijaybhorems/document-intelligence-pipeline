"""D1 routes with fake parsers and the fake OpenAI client: no network, no Docling."""

import base64
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from dip.extract.estimate import INPUT_TOKENS_PER_PDF_PAGE, estimate
from dip.extract.extractor import OpenAIExtractor, Strategy
from dip.extract.pricing import WORKER_USD_PER_SECOND, compute_usd
from dip.extract.routes import MultimodalRoute, ParsedTextRoute
from dip.parse.base import PageSpan, ParsedDocument
from tests.pdfs import text_pdf
from tests.unit.extract.test_extractor import ANSWERS, TEXT, FakeResponses


class FakeParser:
    name = "fake"
    version = "1"

    def parse(self, data: bytes, filename: str) -> ParsedDocument:
        return ParsedDocument(
            text=TEXT,
            pages=[PageSpan(page=1, start=0, end=len(TEXT))],
            parser=self.name,
            parser_version=self.version,
            seconds=2.0,
            warnings=["1/1 pages have almost no text layer"],
        )


def _extractor(responses: FakeResponses) -> OpenAIExtractor:
    client: Any = SimpleNamespace(responses=responses)
    return OpenAIExtractor("gpt-5.6-luna", Strategy.SINGLE, client=client)


@pytest.fixture
def pdf(tmp_path: Path) -> Path:
    path = tmp_path / "d1.pdf"
    path.write_bytes(text_pdf([["Distributor shall not assign this Agreement."]]))
    return path


def test_parsed_text_route_extracts_from_parsed_text_and_prices_compute(
    pdf: Path, tmp_path: Path
) -> None:
    responses = FakeResponses(ANSWERS)
    route = ParsedTextRoute(
        FakeParser(), _extractor(responses), {"d1": pdf}, "scanned", tmp_path / "parsed"
    )

    out = route.predict_all({"d1": "ignored: routes read the PDF"})["d1"]

    assert TEXT in responses.calls[0]["input"][1]["content"]
    assert out.usage.compute_seconds == 2.0
    assert out.usage.compute_usd == pytest.approx(2.0 * WORKER_USD_PER_SECOND)
    assert "parse: 1/1 pages have almost no text layer" in out.issues
    assert route.config()["route"] == "fake"
    assert route.config()["variant"] == "scanned"


def test_multimodal_route_sends_the_pdf_as_a_file(pdf: Path) -> None:
    responses = FakeResponses(ANSWERS)
    route = MultimodalRoute(_extractor(responses), {"d1": pdf}, "clean")

    out = route.predict_all({"d1": ""})["d1"]

    (call,) = responses.calls
    file_part = call["input"][1]["content"][1]
    assert file_part["type"] == "input_file"
    assert base64.b64decode(file_part["file_data"].split(",", 1)[1]) == pdf.read_bytes()
    assert out.fields.clauses.anti_assignment.present
    assert route.name.endswith("-multimodal-clean")


def test_multimodal_estimate_counts_page_images() -> None:
    ex = _extractor(FakeResponses({}))
    text_only = estimate(ex, {"d1": TEXT})
    with_pages = estimate(ex, {"d1": TEXT}, pdf_pages={"d1": 3})

    assert with_pages.input_tokens > text_only.input_tokens
    assert with_pages.input_tokens >= 3 * INPUT_TOKENS_PER_PDF_PAGE


def test_compute_cost_is_priced_at_cloud_run_worker_rates() -> None:
    assert compute_usd(10.0) == pytest.approx(10 * (4 * 0.000024 + 8 * 0.0000025))


def test_hybrid_routes_scans_to_vision_and_text_pdfs_to_text(tmp_path: Path) -> None:
    from dip.extract.routes import HybridRoute
    from dip.ingest.synth_scans import make_scan

    text = text_pdf([["Distributor shall not assign this Agreement without prior consent."] * 6])
    (tmp_path / "born.pdf").write_bytes(text)
    (tmp_path / "scan.pdf").write_bytes(make_scan(text, "scan"))
    pdfs = {"born": tmp_path / "born.pdf", "scan": tmp_path / "scan.pdf"}
    responses = FakeResponses(ANSWERS)
    route = HybridRoute(_extractor(responses), pdfs, "mixed", tmp_path / "parsed")

    assert route.plan(["born", "scan"]) == {"born": "pypdf", "scan": "multimodal"}
    out = route.predict_all({"born": "", "scan": ""})

    assert "route: pypdf" in out["born"].issues
    assert "route: multimodal" in out["scan"].issues
    kinds = [type(c["input"][1]["content"]).__name__ for c in responses.calls]
    assert sorted(kinds) == ["list", "str"]  # one PDF file input, one text input
