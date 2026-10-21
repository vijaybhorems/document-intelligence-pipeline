from pathlib import Path

from dip.ingest.synth_scans import make_scan
from dip.parse.base import ParsedDocument
from dip.parse.cache import cache_path, parse_cached
from dip.parse.pypdf_parser import PypdfParser
from tests.pdfs import text_pdf

PAGE_1 = ["MASTER SERVICES AGREEMENT", "This Agreement is governed by the laws of Delaware."] * 4
PAGE_2 = ["Licensee shall not assign this Agreement without consent."] * 8
PDF = text_pdf([PAGE_1, PAGE_2])


def test_pypdf_reads_the_text_layer_with_page_spans() -> None:
    parsed = PypdfParser().parse(PDF, "x.pdf")

    assert "governed by the laws of Delaware" in parsed.text
    assert [p.page for p in parsed.pages] == [1, 2]
    assert parsed.page_of(parsed.text.index("Licensee shall not assign")) == 2
    assert parsed.page_of(0) == 1
    assert parsed.warnings == []


def test_scan_is_deterministic_and_has_no_text_layer() -> None:
    scan = make_scan(PDF, "doc-1")

    assert scan == make_scan(PDF, "doc-1")
    assert scan != make_scan(PDF, "doc-2")  # noise is seeded per contract
    parsed = PypdfParser().parse(scan, "scan.pdf")
    assert len(parsed.pages) == 2
    assert parsed.text.strip() == ""
    assert parsed.warnings == ["2/2 pages have almost no text layer"]


class CountingParser(PypdfParser):
    calls = 0

    def parse(self, data: bytes, filename: str) -> ParsedDocument:
        CountingParser.calls += 1
        return super().parse(data, filename)


def test_parse_cache_parses_once_per_content_and_version(tmp_path: Path) -> None:
    parser = CountingParser()

    first = parse_cached(parser, PDF, "a.pdf", tmp_path)
    second = parse_cached(parser, PDF, "renamed.pdf", tmp_path)  # same bytes, different name

    assert CountingParser.calls == 1
    assert first == second
    assert (
        cache_path(tmp_path, PDF, parser).parent.name
        == cache_path(tmp_path, PDF, parser).parent.name
    )
    assert parser.version in cache_path(tmp_path, PDF, parser).name
