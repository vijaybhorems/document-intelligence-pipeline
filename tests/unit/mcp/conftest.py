import pytest


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"  # async tests run via the AnyIO plugin (installed with the MCP SDK)
