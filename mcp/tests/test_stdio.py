"""Integration test: exercise the Amsha MCP server over a REAL stdio transport.

Matches the proposal's testing bar: a tool that returns correct data when
called in-process but breaks over stdio (framing, subprocess, encoding) is not
done. We spawn the actual server as a subprocess and talk to it via the MCP
SDK's stdio client.

Run with the repo's venv:  .venv\\Scripts\\python.exe -m pytest mcp/tests/
"""
from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

import pytest

MCP_ROOT = Path(__file__).resolve().parent.parent  # mcp/
SRC = MCP_ROOT / "src"


def _server_cmd() -> list[str]:
    # PYTHONIOENCODING avoids cp1252 encode errors on non-ASCII doc content.
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    code = (f"import sys; sys.path.insert(0, r'{SRC}'); "
            f"from amsha_mcp.server import main; main()")
    return [sys.executable, "-c", code]


def _invoke(name: str, args: dict | None = None) -> str:
    """Open a stdio session, call one tool, tear down. Returns concatenated text."""
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    async def _go():
        params = StdioServerParameters(command=sys.executable, args=_server_cmd()[1:], env=None)
        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(name, arguments=args or {})
                return "".join(
                    c.text for c in result.content if getattr(c, "type", None) == "text"
                )

    return asyncio.run(_go())


def _list_tools() -> set[str]:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    async def _go():
        params = StdioServerParameters(command=sys.executable, args=_server_cmd()[1:], env=None)
        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools = await session.list_tools()
                return {t.name for t in tools.tools}

    return asyncio.run(_go())


EXPECTED_TOOLS = {
    "list_amsha_modules", "explain_module", "get_install_instructions",
    "get_quickstart", "get_prerequisite_stage", "get_implementation_guide",
    "search_amsha_docs",
}


def test_lists_all_tools_over_stdio():
    names = _list_tools()
    assert EXPECTED_TOOLS <= names, f"missing {EXPECTED_TOOLS - names}; got {names}"


def test_list_and_explain_module_over_stdio():
    out = _invoke("list_amsha_modules")
    assert "crew_forge" in out and "crew_monitor" in out

    out = _invoke("explain_module", {"module_name": "crew_forge"})
    assert "Parse YAML" in out and "source_files" in out


def test_install_and_quickstart_over_stdio():
    assert "pip install amsha" in _invoke("get_install_instructions")
    assert "AmshaCrewFileApplication" in _invoke("get_quickstart")


def test_prerequisite_and_implementation_over_stdio():
    out = _invoke("get_prerequisite_stage", {"stage": "03", "summarize": True})
    assert "process-contracts-and-atomicity" in out
    assert "agent-task-validation" in _invoke("get_implementation_guide", {"topic": "05"})


def test_unknown_stage_returns_helpful_error():
    assert "Unknown prerequisite" in _invoke("get_prerequisite_stage", {"stage": "99"})


def test_search_over_stdio():
    out = _invoke("search_amsha_docs", {"query": "Docling"})
    assert "count" in out