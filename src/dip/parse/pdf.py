"""PDF facts that need no parser: how much embedded text each page has."""

import pypdfium2 as pdfium

MIN_LAYER_CHARS = 20  # below this a page has no usable text layer (scanned)


def text_layer_chars(data: bytes) -> list[int]:
    """Characters in each page's embedded text layer (0 for a scanned page)."""
    document = pdfium.PdfDocument(data)
    try:
        return [len(page.get_textpage().get_text_range().strip()) for page in document]
    finally:
        document.close()
