"""Document and record storage (SPEC §9.1): a local folder, or a GCS bucket.

Layout (both backends)::

    raw/{sha256}.{ext}                      uploads, immutable, deduplicated by hash
    records/dt=YYYY-MM-DD/{record_id}.json  ContractRecords, the source of truth
    lake/{table}/…/part-0.parquet           compacted tables for DuckDB (dip.analytics.lake)
"""

import datetime as dt
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


@dataclass(frozen=True)
class BlobInfo:
    key: str
    updated: dt.datetime


class BlobStore(Protocol):
    def put(self, key: str, data: bytes, content_type: str) -> None: ...
    def get(self, key: str) -> bytes: ...
    def exists(self, key: str) -> bool: ...
    def list(self, prefix: str) -> list[BlobInfo]: ...


class LocalBlobStore:
    def __init__(self, root: Path) -> None:
        self.root = root

    def _path(self, key: str) -> Path:
        path = (self.root / key).resolve()
        if not path.is_relative_to(self.root.resolve()):
            raise ValueError(f"key escapes the store: {key!r}")
        return path

    def put(self, key: str, data: bytes, content_type: str) -> None:
        path = self._path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_bytes(data)
        tmp.replace(path)  # atomic: readers never see a half-written file

    def get(self, key: str) -> bytes:
        return self._path(key).read_bytes()

    def exists(self, key: str) -> bool:
        return self._path(key).exists()

    def list(self, prefix: str) -> list[BlobInfo]:
        root = self.root.resolve()
        if not root.exists():
            return []
        found = []
        for path in sorted(root.rglob("*")):
            key = path.relative_to(root).as_posix()
            if path.is_file() and key.startswith(prefix) and not key.endswith(".tmp"):
                mtime = dt.datetime.fromtimestamp(path.stat().st_mtime, dt.UTC)
                found.append(BlobInfo(key, mtime))
        return found


class GcsBlobStore:
    """Honours ``STORAGE_EMULATOR_HOST`` (fake-gcs-server) for local runs."""

    def __init__(self, bucket: str) -> None:
        from google.cloud import storage

        self._client = storage.Client()
        self._bucket = self._client.bucket(bucket)
        self.name = bucket

    def put(self, key: str, data: bytes, content_type: str) -> None:
        self._bucket.blob(key).upload_from_string(data, content_type=content_type)

    def get(self, key: str) -> bytes:
        return self._bucket.blob(key).download_as_bytes()

    def exists(self, key: str) -> bool:
        return self._bucket.blob(key).exists()

    def list(self, prefix: str) -> list[BlobInfo]:
        blobs = self._client.list_blobs(self._bucket, prefix=prefix)
        return [BlobInfo(b.name, b.updated) for b in blobs if b.updated is not None]
