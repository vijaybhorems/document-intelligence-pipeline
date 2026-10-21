"""Synthetic scans: image-only copies of born-digital PDFs (SPEC §6.3).

All 510 CUAD PDFs have a text layer, so on CUAD alone an OCR or multimodal route
can't show what it's for. Each page is rendered to a grayscale image, slightly
rotated, given mild noise and JPEG compression, like a cheap office scan, and
the pages are rebuilt into a PDF with **no text layer**.

Everything is seeded by doc_id, so the scans regenerate identically.
"""

import hashlib
import io
import random
import time
from pathlib import Path

import numpy as np
import pypdfium2 as pdfium
from PIL import Image, ImageFilter

DPI = 150
MAX_ROTATION_DEG = 0.8
NOISE_STD = 6.0  # grey levels
JPEG_QUALITY = 60
_FIXED_DATE = time.gmtime(946_684_800)  # 2000-01-01; Pillow wants a struct_time


def _seed(doc_id: str) -> int:
    return int(hashlib.sha256(doc_id.encode()).hexdigest()[:8], 16)


def _degrade(page: Image.Image, rng: random.Random) -> Image.Image:
    page = page.convert("L").rotate(
        rng.uniform(-MAX_ROTATION_DEG, MAX_ROTATION_DEG),
        resample=Image.Resampling.BICUBIC,
        expand=False,
        fillcolor=255,
    )
    # Seeded sensor noise (PIL's effect_noise has its own unseeded RNG).
    pixels = np.asarray(page, dtype=np.float32)
    noise = np.random.default_rng(rng.getrandbits(32)).normal(0.0, NOISE_STD, pixels.shape)
    page = Image.fromarray(np.clip(pixels + noise, 0, 255).astype(np.uint8))
    page = page.filter(ImageFilter.GaussianBlur(radius=0.4))
    buffer = io.BytesIO()
    page.save(buffer, format="JPEG", quality=JPEG_QUALITY)  # compression artefacts
    return Image.open(io.BytesIO(buffer.getvalue()))


def make_scan(pdf_bytes: bytes, doc_id: str) -> bytes:
    rng = random.Random(_seed(doc_id))  # noqa: S311 (reproducible noise, not security)
    document = pdfium.PdfDocument(pdf_bytes)
    try:
        # pypdfium2 documents scale as a float; its type hint says int.
        pages = [
            _degrade(page.render(scale=DPI / 72).to_pil(), rng)  # pyright: ignore[reportArgumentType]
            for page in document
        ]
    finally:
        document.close()
    out = io.BytesIO()
    pages[0].save(
        out,
        format="PDF",
        save_all=True,
        append_images=pages[1:],
        resolution=DPI,
        # Pillow stamps the current time otherwise, so two runs straddling a second differ.
        creationDate=_FIXED_DATE,
        modDate=_FIXED_DATE,
    )
    return out.getvalue()


def scan_path(scans_dir: Path, doc_id: str) -> Path:
    return scans_dir / f"{doc_id}.pdf"


def write_scans(pdfs: dict[str, Path], scans_dir: Path) -> list[Path]:
    scans_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for doc_id, path in sorted(pdfs.items()):
        target = scan_path(scans_dir, doc_id)
        if not target.exists():
            target.write_bytes(make_scan(path.read_bytes(), doc_id))
        written.append(target)
    return written
