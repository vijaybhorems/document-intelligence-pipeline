"""Document and record storage (SPEC §9.1): a local folder, or a GCS bucket.

Layout (both backends)::

    raw/{sha256}.{ext}                      uploads, immutable, deduplicated by hash
    records/dt=YYYY-MM-DD/{record_id}.json  ContractRecords, the source of truth
"""

from pathlib import Path
from typing import Protocol


class BlobStore(Protocol):
    def put(self, key: str, data: bytes, content_type: str) -> None: ...
    def get(self, key: str) -> bytes: ...
    def exists(self, key: str) -> bool: ...


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


class GcsBlobStore:
    """Honours ``STORAGE_EMULATOR_HOST`` (fake-gcs-server) for local runs."""

    def __init__(self, bucket: str) -> None:
        from google.cloud import storage

        self._bucket = storage.Client().bucket(bucket)

    def put(self, key: str, data: bytes, content_type: str) -> None:
        self._bucket.blob(key).upload_from_string(data, content_type=content_type)

    def get(self, key: str) -> bytes:
        return self._bucket.blob(key).download_as_bytes()

    def exists(self, key: str) -> bool:
        return self._bucket.blob(key).exists()
