"""Extraction routes for decision D1 (SPEC §6.1).

- ``txt``         CUAD's own text files: a perfect-parser upper bound
- ``pypdf``       PDF text layer only: free and fast, blind to scans
- ``docling``     layout-aware parsing with OCR
- ``multimodal``  no parser: the model reads the PDF itself

Each route runs on the ``clean`` (original, born-digital) or ``scanned``
(synthetic image-only, SPEC §6.3) variant of every PDF. Parsing is cached and
its time is priced at Cloud Run rates as ``compute_usd``, so routes compare on
total cost, not just API spend.
"""

from collections.abc import Callable
from pathlib import Path
from typing import Any

from dip.extract.extractor import OpenAIExtractor
from dip.extract.pricing import compute_usd
from dip.extract.system import SystemOutput, Usage
from dip.parse.base import ParsedDocument, Parser
from dip.parse.cache import parse_cached

ROUTES = ("txt", "pypdf", "docling", "multimodal", "hybrid")
VARIANTS = ("clean", "scanned")


class ParsedTextRoute:
    """Parse each PDF (cached), then extract from the parsed text."""

    def __init__(
        self,
        parser: Parser,
        extractor: OpenAIExtractor,
        pdfs: dict[str, Path],
        variant: str,
        cache_dir: Path,
    ) -> None:
        self.parser = parser
        self.extractor = extractor
        self.pdfs = pdfs
        self.variant = variant
        self.cache_dir = cache_dir

    @property
    def name(self) -> str:
        return f"{self.extractor.name}-{self.parser.name}-{self.variant}"

    def config(self) -> dict[str, Any]:
        return {
            **self.extractor.config(),
            "route": self.parser.name,
            "variant": self.variant,
            "parser_version": self.parser.version,
        }

    def predict_all(
        self,
        texts: dict[str, str],
        max_cost_usd: float | None = None,
        on_usage: Callable[[Usage], None] | None = None,
    ) -> dict[str, SystemOutput]:
        parsed = {
            doc_id: parse_cached(
                self.parser, self.pdfs[doc_id].read_bytes(), f"{doc_id}.pdf", self.cache_dir
            )
            for doc_id in sorted(texts)
        }
        outputs = self.extractor.predict_all(
            {doc_id: p.text for doc_id, p in parsed.items()}, max_cost_usd, on_usage
        )
        for doc_id, out in outputs.items():
            seconds = parsed[doc_id].seconds
            parse_usage = Usage(compute_seconds=seconds, compute_usd=compute_usd(seconds))
            issues = [f"parse: {w}" for w in parsed[doc_id].warnings]
            outputs[doc_id] = out.model_copy(
                update={"usage": out.usage + parse_usage, "issues": out.issues + issues}
            )
        return outputs


class MultimodalRoute:
    """No parser: send each PDF to the model as a file input."""

    def __init__(self, extractor: OpenAIExtractor, pdfs: dict[str, Path], variant: str) -> None:
        self.extractor = extractor
        self.pdfs = pdfs
        self.variant = variant

    @property
    def name(self) -> str:
        return f"{self.extractor.name}-multimodal-{self.variant}"

    def config(self) -> dict[str, Any]:
        return {**self.extractor.config(), "route": "multimodal", "variant": self.variant}

    def predict_all(
        self,
        texts: dict[str, str],
        max_cost_usd: float | None = None,
        on_usage: Callable[[Usage], None] | None = None,
    ) -> dict[str, SystemOutput]:
        pdfs = {doc_id: self.pdfs[doc_id].read_bytes() for doc_id in sorted(texts)}
        return self.extractor.predict_pdfs(pdfs, max_cost_usd, on_usage)


SCANNED_PAGE_SHARE = 0.5  # route to multimodal when more than half the pages lack a text layer


def needs_vision(parsed_text_layer: ParsedDocument) -> bool:
    """A PDF is treated as scanned when most pages have (almost) no embedded text."""
    from dip.parse.pypdf_parser import LOW_TEXT_CHARS

    pages = parsed_text_layer.pages
    if not pages:
        return True
    low = sum((span.end - span.start) < LOW_TEXT_CHARS for span in pages)
    return low / len(pages) > SCANNED_PAGE_SHARE


class HybridRoute:
    """Decision D1: pypdf text for born-digital PDFs, multimodal for scanned ones.

    The text layer is read once (free, milliseconds); contracts whose pages mostly
    lack one go to the model as PDFs. Each prediction records the route it took.
    """

    def __init__(
        self, extractor: OpenAIExtractor, pdfs: dict[str, Path], variant: str, cache_dir: Path
    ) -> None:
        from dip.parse.pypdf_parser import PypdfParser

        self.extractor = extractor
        self.pdfs = pdfs
        self.variant = variant
        self.cache_dir = cache_dir
        self.text_layer = PypdfParser()

    @property
    def name(self) -> str:
        return f"{self.extractor.name}-hybrid-{self.variant}"

    def config(self) -> dict[str, Any]:
        return {
            **self.extractor.config(),
            "route": "hybrid",
            "variant": self.variant,
            "scanned_page_share": SCANNED_PAGE_SHARE,
        }

    def plan(self, doc_ids: list[str]) -> dict[str, str]:
        """doc_id -> "pypdf" or "multimodal"."""
        routes = {}
        for doc_id in sorted(doc_ids):
            data = self.pdfs[doc_id].read_bytes()
            layer = parse_cached(self.text_layer, data, f"{doc_id}.pdf", self.cache_dir)
            routes[doc_id] = "multimodal" if needs_vision(layer) else "pypdf"
        return routes

    def predict_all(
        self,
        texts: dict[str, str],
        max_cost_usd: float | None = None,
        on_usage: Callable[[Usage], None] | None = None,
    ) -> dict[str, SystemOutput]:
        routes = self.plan(list(texts))
        text_ids = [d for d, r in routes.items() if r == "pypdf"]
        vision_ids = [d for d, r in routes.items() if r == "multimodal"]
        outputs: dict[str, SystemOutput] = {}
        if text_ids:
            text_route = ParsedTextRoute(
                self.text_layer, self.extractor, self.pdfs, self.variant, self.cache_dir
            )
            outputs |= text_route.predict_all(dict.fromkeys(text_ids, ""), max_cost_usd, on_usage)
        if vision_ids:
            spent = sum(o.usage.cost_usd for o in outputs.values())
            remaining = None if max_cost_usd is None else max(0.0, max_cost_usd - spent)
            vision = MultimodalRoute(self.extractor, self.pdfs, self.variant)
            outputs |= vision.predict_all(dict.fromkeys(vision_ids, ""), remaining, on_usage)
        return {
            d: o.model_copy(update={"issues": [*o.issues, f"route: {routes[d]}"]})
            for d, o in outputs.items()
        }
