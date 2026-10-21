"""Upload checks before anything is stored or paid for (SPEC §6.5, §18).

The type is sniffed from the bytes, never trusted from the filename or the
Content-Type header. Limits: size (``max_upload_mb``) and page count (``max_pages``).
"""

from dataclasses import dataclass

import pypdfium2 as pdfium

from dip.pipeline import PDF, TEXT

EXTENSIONS = {PDF: "pdf", TEXT: "txt"}


class UploadError(ValueError):
    def __init__(self, status: int, title: str, detail: str) -> None:
        super().__init__(detail)
        self.status = status
        self.title = title
        self.detail = detail


@dataclass(frozen=True)
class CheckedUpload:
    mime: str
    pages: int | None


def sniff(data: bytes) -> str | None:
    if data.startswith(b"%PDF-"):
        return PDF
    if data.startswith(b"PK\x03\x04"):
        return "application/zip"  # DOCX is a zip; not supported in v1 (SPEC §20 Q5)
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return None
    printable = sum(c.isprintable() or c.isspace() for c in text[:4096])
    return TEXT if text and printable / min(len(text), 4096) > 0.95 else None


def check(data: bytes, max_mb: int, max_pages: int) -> CheckedUpload:
    if not data:
        raise UploadError(422, "Empty document", "the upload has no content")
    if len(data) > max_mb * 1024 * 1024:
        raise UploadError(413, "Document too large", f"limit is {max_mb} MB")
    mime = sniff(data)
    if mime not in EXTENSIONS:
        raise UploadError(
            415, "Unsupported document type", "send a PDF or UTF-8 text (DOCX isn't supported yet)"
        )
    pages = None
    if mime == PDF:
        try:
            document = pdfium.PdfDocument(data)
        except pdfium.PdfiumError as exc:
            raise UploadError(422, "Unreadable PDF", str(exc)) from exc
        pages = len(document)
        document.close()
        if pages > max_pages:
            raise UploadError(413, "Too many pages", f"{pages} pages; limit is {max_pages}")
    return CheckedUpload(mime=mime, pages=pages)
