import subprocess
import sys

import pytest

HEAVY = ("llama_index", "duckdb", "matplotlib", "docling", "tiktoken")


@pytest.mark.parametrize("role", ["api", "worker"])
def test_service_import_path_stays_lean(role: str) -> None:
    # Every module imported at startup is paid on each Cloud Run cold start.
    code = (
        f"import sys; import dip.{role}.app; "
        f"print(','.join(m for m in {HEAVY!r} if m in sys.modules))"
    )
    loaded = subprocess.run(  # noqa: S603 - our interpreter, a constant script
        [sys.executable, "-c", code], capture_output=True, text=True, check=True
    ).stdout.strip()
    assert loaded == "", f"dip.{role}.app imports {loaded}"
