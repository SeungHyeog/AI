from __future__ import annotations

from pathlib import Path

import anyio

from safe_eks_mcp.server import create_mcp


def test_fastmcp_call_tool_returns_payload_without_optional_fields(fake_cli: Path) -> None:
    _ = fake_cli

    async def call_tool() -> None:
        payload = await create_mcp().call_tool("aws_eks_list_clusters", {"region": "us-east-1"})
        assert payload is not None

    anyio.run(call_tool)
