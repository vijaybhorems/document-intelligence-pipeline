import pytest

from dip.ingest.synth_scans import make_scan
from dip.pipeline import PDF, TEXT, Stage
from dip.service.uploads import UploadError, check, sniff
from tests.pdfs import text_pdf
from tests.unit.extract.test_extractor import ANSWERS, FakeResponses
from tests.unit.service.conftest import CONTRACT, make_pipeline

PDF_BYTES = text_pdf([[CONTRACT] * 3])


@pytest.mark.parametrize(
    ("data", "mime"),
    [
        (PDF_BYTES, PDF),
        (b"Plain contract text.\n", TEXT),
        (b"PK\x03\x04docx", "application/zip"),
        (b"\xff\xfe\x00\x01", None),
    ],
)
def test_sniff_reads_bytes_not_names(data: bytes, mime: str | None) -> None:
    assert sniff(data) == mime


@pytest.mark.parametrize(
    ("data", "status"),
    [
        (b"", 422),
        (b"PK\x03\x04docx", 415),
        (b"%PDF-1.4 not really", 422),
        (b"x" * (2 * 1024 * 1024), 413),
    ],
)
def test_check_rejects_bad_uploads(data: bytes, status: int) -> None:
    with pytest.raises(UploadError) as err:
        check(data, max_mb=1, max_pages=300)
    assert err.value.status == status


def test_check_enforces_page_limit() -> None:
    with pytest.raises(UploadError) as err:
        check(text_pdf([["a"]] * 3), max_mb=25, max_pages=2)
    assert (err.value.status, err.value.title) == (413, "Too many pages")


def test_born_digital_pdf_takes_the_text_route_and_is_grounded() -> None:
    stages: list[Stage] = []
    record = make_pipeline(FakeResponses(ANSWERS)).process(PDF_BYTES, PDF, stages.append)

    assert stages == [Stage.ROUTING, Stage.EXTRACTING, Stage.VALIDATING]
    assert record.provenance.route == "text"
    assert record.provenance.grounding == "checked"
    assert record.provenance.pages == 1
    assert record.fields.governing_law.values == ["Texas"]
    assert record.fields.clauses.anti_assignment.evidence[0].grounded is True


def test_scan_goes_multimodal_and_grounding_is_unavailable() -> None:
    responses = FakeResponses(ANSWERS)
    record = make_pipeline(responses).process(make_scan(PDF_BYTES, "d"), PDF)

    assert record.provenance.route == "multimodal"
    assert record.provenance.grounding == "unavailable"
    assert record.fields.clauses.anti_assignment.evidence[0].grounded is None  # never "True"
    assert responses.calls[0]["input"][1]["content"][1]["type"] == "input_file"


def test_unsupported_value_triggers_one_reask() -> None:
    hallucinated = {
        **ANSWERS,
        "audit_rights": ANSWERS["anti_assignment"].model_copy(
            update={"quotes": ["Licensor may audit all books at any time."]}
        ),
    }
    responses = FakeResponses(hallucinated)
    record = make_pipeline(responses).process(CONTRACT.encode(), TEXT)

    assert len(responses.calls) == 2  # extraction + one re-ask
    assert "audit_rights" in responses.calls[1]["input"][-1]["content"]
    assert record.provenance.cost_usd > 0


def test_pipeline_version_changes_with_configuration() -> None:
    a = make_pipeline(FakeResponses({}))
    b = make_pipeline(FakeResponses({}))
    b.reask = False

    assert a.version != b.version
    assert "prompt-v4" in a.version
