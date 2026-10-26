from typing import Any

from mcp_types import TextContent, TextResourceContents


def text(result: Any) -> str:
    """The text content of a tool result (narrows MCP's content union)."""
    block = result.content[0]
    assert isinstance(block, TextContent)
    return block.text


def resource_text(read: Any) -> str:
    block = read.contents[0]
    assert isinstance(block, TextResourceContents)
    return block.text
