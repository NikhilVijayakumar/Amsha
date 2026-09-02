"""Amsha MCP stdio server — tool registration and entrypoint."""
from __future__ import annotations

import mcp.server.stdio
from mcp.server.fastmcp import FastMCP

from .tools import architecture, install, methodology, modules, search

mcp = FastMCP(
    "amsha-mcp",
    instructions=(
        "Amsha is a lightweight library for CrewAI orchestration. Serve Amsha's "
        "modules, installation/quickstart, and the prerequisite (00-09) / "
        "implementation (00-23) crew-design methodology. Design a crew correctly "
        "before writing YAML."
    ),
)


@mcp.tool()
def list_amsha_modules() -> dict:
    """List every runtime module under src/nikhil/amsha with a one-line purpose. Returns a dict with a 'modules' key."""
    return modules.list_amsha_modules()


@mcp.tool()
def explain_module(module_name: str) -> dict:
    """Explain a specific Amsha module (e.g. 'crew_forge'): purpose, docs pointer, source files. Check list_amsha_modules() first."""
    return modules.explain_module(module_name)


@mcp.tool()
def get_install_instructions() -> dict:
    """Return how to install Amsha, including the optional docling extra and Python version constraint."""
    return install.get_install_instructions()


@mcp.tool()
def get_quickstart() -> dict:
    """Return the Quick Start code block from Amsha's README."""
    return install.get_quickstart()


@mcp.tool()
def get_prerequisite_stage(stage: str, summarize: bool = False) -> dict:
    """Return content of one prerequisite doc (stage '00'-'09', e.g. '03'). Optionally summarize."""
    return methodology.get_prerequisite_stage(stage, summarize)


@mcp.tool()
def get_implementation_guide(topic: str, summarize: bool = False) -> dict:
    """Return content of one implementation doc (topic '00'-'23', e.g. '05'). Optionally summarize."""
    return methodology.get_implementation_guide(topic, summarize)


@mcp.tool()
def search_amsha_docs(query: str) -> dict:
    """Keyword search across mcp/docs/ + docs/ + top-level markdown, with file and line references. Should not be used for Boolean/search-engine operators. Should not be used to fetch whole pages."""
    return search.search_amsha_docs(query)


@mcp.tool()
def begin_architecture_session(problem_statement: str) -> dict:
    """Start a Phase-2 architecture session with a problem statement. Returns a session_id and the first prerequisite stage (00) to fill. Phase 2 sequences the prerequisite methodology so the LLM designs before writing crew YAML."""
    return architecture.begin_architecture_session(problem_statement)


@mcp.tool()
def submit_stage_artifact(session_id: str, stage: str, artifact: dict, checklist: list[str] | None = None) -> dict:
    """Structurally validate a filled prerequisite artifact (stage 00-09) for a session; on success advance to the next stage. Gated: earlier stages must pass first; capability selection (07) is deferred. Structural-only — design quality is Phase 3."""
    return architecture.submit_stage_artifact(session_id, stage, artifact, checklist)


@mcp.tool()
def current_stage(session_id: str) -> dict:
    """Return where a Phase-2 architecture session is in the methodology (completed stages, current stage)."""
    return architecture.current_stage(session_id)


@mcp.tool()
def get_least_powerful_capability(session_id: str) -> dict:
    """After decomposition stages (00-06) pass for a session, present the least-powerful capability ladder as a decision, not a menu. Refuses until earlier stages are validated."""
    return architecture.get_least_powerful_capability(session_id)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()