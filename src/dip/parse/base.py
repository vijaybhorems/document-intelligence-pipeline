"""The parser interface and its output (SPEC §6.2)."""

from typing import Protocol

from pydantic import BaseModel


class PageSpan(BaseModel):
    page: int  # 1-based
    start: int  # char offsets into ParsedDocument.text
    end: int


class ParsedDocument(BaseModel):
    text: str
    pages: list[PageSpan] = []
    parser: str
    parser_version: str
    ocr_used: bool = False
    seconds: float = 0.0  # wall-clock parse time, the basis of compute cost
    warnings: list[str] = []

    def page_of(self, offset: int) -> int | None:
        """Which page a character offset falls on, for citing evidence by page."""
        for span in self.pages:
            if span.start <= offset < span.end:
                return span.page
        return None


class Parser(Protocol):
    @property
    def name(self) -> str: ...

    @property
    def version(self) -> str: ...

    def parse(self, data: bytes, filename: str) -> ParsedDocument: ...
