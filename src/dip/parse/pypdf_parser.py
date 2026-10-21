"""The cheapest parser: read the PDF's embedded text layer (SPEC §6.2).

Fast and free, but blind to anything without a text layer: a scanned page
comes back empty. That failure is the point of comparing it with OCR.
"""

import io
import logging
import time
from importlib.metadata import version

from pypdf import PdfReader

from dip.parse.base import PageSpan, ParsedDocument

LOW_TEXT_CHARS = 100  # below this a page probably has no text layer


class PypdfParser:
    name = "pypdf"
    version = version("pypdf")

    def parse(self, data: bytes, filename: str) -> ParsedDocument:
        logging.getLogger("pypdf").setLevel(logging.ERROR)
        started = time.perf_counter()
        reader = PdfReader(io.BytesIO(data))
        parts: list[str] = []
        pages: list[PageSpan] = []
        offset = 0
        empty = 0
        for number, page in enumerate(reader.pages, start=1):
            text = (page.extract_text() or "").strip()
            empty += len(text) < LOW_TEXT_CHARS
            pages.append(PageSpan(page=number, start=offset, end=offset + len(text)))
            parts.append(text)
            offset += len(text) + 2  # "\n\n" between pages
        warnings = [f"{empty}/{len(pages)} pages have almost no text layer"] if empty else []
        return ParsedDocument(
            text="\n\n".join(parts),
            pages=pages,
            parser=self.name,
            parser_version=self.version,
            seconds=time.perf_counter() - started,
            warnings=warnings,
        )
