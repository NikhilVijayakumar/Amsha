"""Minimal local MCP stdio server for Amsha's tools/MCP example (proposal 12).

Spawned as a subprocess by CrewAI's MCPServerStdio at task-execution time --
see copywriter_agent.yaml's ``mcp_servers`` block and
``verify_capability_example.py``. Requires the venv's python (with the
``mcp`` package installed) on PATH, since ``command: python`` in the YAML
config resolves against the parent process's PATH.

Manual smoke test:
    python example/crew_forge/example_config/mcp_server/word_count_server.py
    (blocks, waiting on stdio -- Ctrl+C to stop)
"""
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("amsha-word-count")


@mcp.tool()
def count_words(text: str) -> int:
    """Count the words in a string of text."""
    return len(text.split())


if __name__ == "__main__":
    mcp.run(transport="stdio")
