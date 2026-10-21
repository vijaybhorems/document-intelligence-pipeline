"""Docling: layout-aware parsing with OCR (SPEC §6.2, decision D1).

Docling reads the PDF's text layer where one exists and runs OCR on image
regions, so a scanned page still yields text. It also recovers reading order,
headings and tables, which a plain text-layer dump loses.

The OCR engine is pinned to RapidOCR (ONNX models, no system dependencies) so
macOS and Linux (Cloud Run) produce the same output; the engine is part of the
version string, so changing it misses the parse cache. The converter loads
several hundred MB of models, so build one parser and reuse it.
"""

import io
import logging
import time
from importlib.metadata import version

from dip.parse.base import PageSpan, ParsedDocument

OCR_ENGINE = "rapidocr"


class DoclingParser:
    name = "docling"
    version = f"{version('docling')}+{OCR_ENGINE}"

    def __init__(self) -> None:
        from docling.datamodel.base_models import InputFormat
        from docling.datamodel.pipeline_options import PdfPipelineOptions, RapidOcrOptions
        from docling.document_converter import DocumentConverter, PdfFormatOption

        for noisy in ("docling", "rapidocr", "RapidOCR"):
            logging.getLogger(noisy).setLevel(logging.ERROR)
        options = PdfPipelineOptions(do_ocr=True, ocr_options=RapidOcrOptions())
        self._converter = DocumentConverter(
            format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=options)}
        )

    def parse(self, data: bytes, filename: str) -> ParsedDocument:
        from docling.datamodel.base_models import DocumentStream

        started = time.perf_counter()
        result = self._converter.convert(DocumentStream(name=filename, stream=io.BytesIO(data)))
        document = result.document
        parts: list[str] = []
        pages: list[PageSpan] = []
        offset = 0
        for page_no in range(1, document.num_pages() + 1):
            text = document.export_to_markdown(page_no=page_no).strip()
            pages.append(PageSpan(page=page_no, start=offset, end=offset + len(text)))
            parts.append(text)
            offset += len(text) + 2
        ocr_used = any(
            getattr(cell, "from_ocr", False)
            for page in result.pages
            for cell in (page.cells if page.cells else [])
        )
        return ParsedDocument(
            text="\n\n".join(parts),
            pages=pages,
            parser=self.name,
            parser_version=self.version,
            ocr_used=ocr_used,
            seconds=time.perf_counter() - started,
            warnings=[str(e) for e in result.errors][:5],
        )
