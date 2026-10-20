"""Measure how much embedded text each PDF has (SPEC §2.1).

A born-digital PDF has a text layer on every page; a scanned one has little or
none. If CUAD is almost all born-digital, comparing OCR routes on it proves
little, which is why Phase 6 adds a synthetic-scan variant (SPEC §6.3).
"""

import logging
from concurrent.futures import ProcessPoolExecutor
from dataclasses import astuple, dataclass
from pathlib import Path
from statistics import median

import duckdb
from pypdf import PdfReader

# Below this many extracted characters a page is treated as image-only.
LOW_TEXT_CHARS = 100


@dataclass(frozen=True)
class TextLayerProfile:
    doc_id: str
    pages: int
    chars: int
    median_chars_per_page: float
    low_text_pages: int
    error: str | None = None

    @property
    def low_text_share(self) -> float:
        return self.low_text_pages / self.pages if self.pages else 1.0


def profile_pdf(doc_id: str, path: Path) -> TextLayerProfile:
    # pypdf logs warnings for the many slightly malformed EDGAR PDFs; they're noise here.
    logging.getLogger("pypdf").setLevel(logging.ERROR)
    try:
        reader = PdfReader(path)
        per_page = [len((page.extract_text() or "").strip()) for page in reader.pages]
    except Exception as exc:  # untrusted input: record the failure, keep going
        return TextLayerProfile(doc_id, 0, 0, 0.0, 0, error=f"{type(exc).__name__}: {exc}"[:300])
    return TextLayerProfile(
        doc_id=doc_id,
        pages=len(per_page),
        chars=sum(per_page),
        median_chars_per_page=float(median(per_page)) if per_page else 0.0,
        low_text_pages=sum(n < LOW_TEXT_CHARS for n in per_page),
    )


def profile_pdfs(pdfs: dict[str, Path], workers: int | None = None) -> list[TextLayerProfile]:
    ids = sorted(pdfs)
    with ProcessPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(profile_pdf, ids, [pdfs[i] for i in ids], chunksize=8))


def write_profiles(profiles: list[TextLayerProfile], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect()
    con.execute(
        """CREATE TABLE text_layer (doc_id VARCHAR, pages INTEGER, chars INTEGER,
            median_chars_per_page DOUBLE, low_text_pages INTEGER, error VARCHAR)"""
    )
    con.executemany("INSERT INTO text_layer VALUES (?, ?, ?, ?, ?, ?)", map(astuple, profiles))
    con.execute(f"COPY text_layer TO '{path.as_posix()}' (FORMAT parquet)")
