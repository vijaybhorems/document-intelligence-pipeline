import hashlib
import zipfile
from pathlib import Path

import httpx
import pytest

from dip.ingest.cuad import (
    ChecksumError,
    UnsafeArchiveError,
    download,
    make_doc_id,
    match_key,
    md5_of,
    safe_extract,
)


@pytest.mark.parametrize(
    ("a", "b"),
    [
        ("MACY'S,INC_05_11_2020-EX-99.4", "MACY_S,INC_05_11_2020-EX-99.4"),
        ("MOELIS&CO_03_24_2014", "MOELIS_CO_03_24_2014"),
        ("Principal Life - Agreement ", "Principal Life - Agreement"),
        ("LECLANCHÉ S.A.", "LECLANCHÉ S.A."),  # NFD vs NFC accent
    ],
)
def test_match_key_ignores_cuads_spelling_differences(a: str, b: str) -> None:
    assert match_key(a) == match_key(b)


def test_make_doc_id_is_filesystem_safe() -> None:
    doc_id = make_doc_id("LECLANCHÉ S.A. - JOINT DEVELOPMENT & MARKETING AGREEMENT ")

    assert doc_id == "LECLANCHE_S.A._-_JOINT_DEVELOPMENT_MARKETING_AGREEMENT"


def _zip_with(tmp_path: Path, member: str) -> Path:
    archive = tmp_path / "a.zip"
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr(member, "x")
    return archive


def test_safe_extract_extracts_normal_members(tmp_path: Path) -> None:
    archive = _zip_with(tmp_path, "CUAD_v1/readme.txt")

    safe_extract(archive, tmp_path / "out")

    assert (tmp_path / "out" / "CUAD_v1" / "readme.txt").read_text() == "x"


@pytest.mark.parametrize("member", ["../escape.txt", "a/../../escape.txt", "/etc/escape.txt"])
def test_safe_extract_rejects_zip_slip(tmp_path: Path, member: str) -> None:
    archive = _zip_with(tmp_path, member)

    with pytest.raises(UnsafeArchiveError):
        safe_extract(archive, tmp_path / "out")
    assert not (tmp_path / "escape.txt").exists()


class _Server:
    """A fake HTTP server: records requests, always returns ``body``."""

    def __init__(self, body: bytes) -> None:
        self.body = body
        self.calls: list[str] = []

    def client(self) -> httpx.Client:
        def handler(request: httpx.Request) -> httpx.Response:
            self.calls.append(str(request.url))
            return httpx.Response(200, content=self.body)

        return httpx.Client(transport=httpx.MockTransport(handler))


def test_download_verifies_checksum(tmp_path: Path) -> None:
    server = _Server(b"cuad bytes")
    dest = tmp_path / "CUAD_v1.zip"
    expected = hashlib.md5(server.body).hexdigest()  # noqa: S324

    download("https://example.test/cuad.zip", dest, expected, client=server.client())

    assert dest.read_bytes() == server.body
    assert len(server.calls) == 1


def test_download_skips_when_valid_file_exists(tmp_path: Path) -> None:
    dest = tmp_path / "CUAD_v1.zip"
    dest.write_bytes(b"already here")
    server = _Server(b"new")

    download("https://example.test/cuad.zip", dest, md5_of(dest), client=server.client())

    assert server.calls == []


def test_download_rejects_wrong_checksum(tmp_path: Path) -> None:
    dest = tmp_path / "CUAD_v1.zip"

    with pytest.raises(ChecksumError):
        download("https://example.test/cuad.zip", dest, "0" * 32, client=_Server(b"x").client())
    assert not dest.exists()
    assert not dest.with_suffix(".zip.part").exists()
