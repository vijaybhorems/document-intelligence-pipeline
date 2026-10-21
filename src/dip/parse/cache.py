"""Parse once, reuse forever (SPEC §6.5).

Parsed output is cached at ``data/parsed/{sha256}/{parser}-{version}.json``, so
re-running extraction experiments never re-parses, and a parser upgrade
naturally misses the cache.
"""

import hashlib
from pathlib import Path

from dip.parse.base import ParsedDocument, Parser


def content_hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def cache_path(cache_dir: Path, data: bytes, parser: Parser) -> Path:
    return cache_dir / content_hash(data) / f"{parser.name}-{parser.version}.json"


def parse_cached(parser: Parser, data: bytes, filename: str, cache_dir: Path) -> ParsedDocument:
    path = cache_path(cache_dir, data, parser)
    if path.exists():
        return ParsedDocument.model_validate_json(path.read_text("utf-8"))
    parsed = parser.parse(data, filename)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(parsed.model_dump_json(), "utf-8")
    return parsed
