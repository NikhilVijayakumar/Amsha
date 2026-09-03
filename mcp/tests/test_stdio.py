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


async def _call_in(session, name: str, args: dict | None = None) -> dict:
    """Call a tool on an already-open session and parse the JSON response."""
    import json

    result = await session.call_tool(name, arguments=args or {})
    text = "".join(c.text for c in result.content if getattr(c, "type", None) == "text")
    return json.loads(text)


async def _with_server(handler):
    """Open one stdio server process, run handler(session) on it, tear down.
    Mirrors a real client holding one connection across a session so the server's
    in-memory Phase-2 session state persists across tool calls."""
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    params = StdioServerParameters(command=sys.executable, args=_server_cmd()[1:], env=None)
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            return await handler(session)


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


# ---------------------------------------------------------------------------
# Phase 2 — Architecture Guidance (proposal 02)
# ---------------------------------------------------------------------------

def test_phase2_tools_registered():
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    async def _go():
        params = StdioServerParameters(command=sys.executable, args=_server_cmd()[1:], env=None)
        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools = await session.list_tools()
                return {t.name for t in tools.tools}

    names = asyncio.run(_go())
    for tool in ("begin_architecture_session", "submit_stage_artifact",
                 "current_stage", "get_least_powerful_capability"):
        assert tool in names, f"missing Phase2 tool {tool}"


def test_phase2_full_sequence_over_stdio():
    """Walk a session through stages 00-06 within ONE server process, then capability opens."""
    async def handler(session):
        begin = await _call_in(session, "begin_architecture_session",
                               {"problem_statement": "Produce a validated chapter development package"})
        sid = begin["session_id"]
        assert begin["current_stage"] == "00"

        gate = await _call_in(session, "get_least_powerful_capability", {"session_id": sid})
        assert "error" in gate and "deferred" in gate["error"]
        assert "Deterministic Python" not in gate

        submit = {
            "00": {"problem", "start_condition", "desired_end_condition", "primary_objective", "constraints", "success_definition"},
            "01": {"start_boundary", "end_boundary", "scope", "completion_definition"},
            "02": {"start_state", "end_state", "processes", "relationships"},
            "03": {"contracts"},
            "04": {"validation"},
            "05": {"flow_order", "transitions", "state_requirements", "checkpoints"},
            "06": {"failures", "recovery", "unrecoverable_definition"},
        }
        for stage, fields in sorted(submit.items()):
            artifact = {f: "v" for f in fields}
            out = await _call_in(session, "submit_stage_artifact",
                                 {"session_id": sid, "stage": stage, "artifact": artifact, "checklist": ["ok"]})
            assert out["accepted"] is True, f"stage {stage} not accepted: {out}"

        cap = await _call_in(session, "get_least_powerful_capability", {"session_id": sid})
        assert "error" not in cap
        assert "Deterministic Python" in cap["capability_ladder"]

        cur = await _call_in(session, "current_stage", {"session_id": sid})
        assert cur["current_stage"] == "07"

    asyncio.run(_with_server(handler))


def test_phase2_out_of_order_is_blocked():
    async def handler(session):
        begin = await _call_in(session, "begin_architecture_session", {"problem_statement": "x"})
        sid = begin["session_id"]
        out = await _call_in(session, "submit_stage_artifact",
                             {"session_id": sid, "stage": "03", "artifact": {"contracts": "v"}})
        assert out["error"].startswith("Stage '03' blocked")
        assert "01" in out["error"] and "02" in out["error"]

    asyncio.run(_with_server(handler))


def test_phase2_missing_fields_reported():
    async def handler(session):
        begin = await _call_in(session, "begin_architecture_session", {"problem_statement": "x"})
        sid = begin["session_id"]
        out = await _call_in(session, "submit_stage_artifact",
                             {"session_id": sid, "stage": "00", "artifact": {"problem": "only"}})
        assert out["accepted"] is False
        assert "start_condition" in out["missing_fields"]

    asyncio.run(_with_server(handler))
FIXTURES = MCP_ROOT / "tests" / "fixtures"


def _verify_crew_engine(crew):
    from amsha_mcp.tools.verification import verify_crew_yaml
    return verify_crew_yaml(crew)


def test_phase3_valid_crew_passes_inprocess():
    res = _verify_crew_engine(FIXTURES / "valid_crew")
    assert res.passed is True
    assert not any(f.severity == "error" for f in res.findings)


def test_phase3_bad_crew_reports_god_agent_and_god_task():
    res = _verify_crew_engine(FIXTURES / "bad_crew")
    ids = {f.rule_id for f in res.findings}
    assert "agent.god_scope" in ids
    assert "task.god_lifecycle" in ids
    assert res.passed is False


def test_phase3_no_mutation():
    """A verify call must never modify the YAML it reports on."""
    target = FIXTURES / "bad_crew" / "agents" / "god_agent.yaml"
    before = target.read_text(encoding="utf-8")
    _verify_crew_engine(FIXTURES / "bad_crew")
    after = target.read_text(encoding="utf-8")
    assert before == after


def test_phase3_verify_component_over_stdio():
    async def handler(session):
        out = await _call_in(session, "verify_component", {
            "component_type": "agent",
            "definition": {"role": "Universal Master Genius AI",
                           "goal": "do research write publish manage database sql audio legal",
                           "backstory": "survived seven continents python sql api image deployment"},
        })
        assert out["passed"] is False
        ids = {f["rule_id"] for f in out["findings"]}
        assert "agent.god_scope" in ids

    asyncio.run(_with_server(handler))


def test_phase3_verify_prerequisite_artifacts_over_stdio():
    async def handler(session):
        out = await _call_in(session, "verify_prerequisite_artifacts", {
            "artifacts": {
                "00": {"problem": "p"},
                "03": {"contracts": [{"id": "c1", "name": "C1", "purpose": "x"}]},
                "02": {"processes": [{"id": "p1"}]},
            },
        })
        assert any(f["rule_id"] == "prereq.00_incomplete" for f in out["findings"])
        assert any(f["rule_id"] == "prereq.process_without_contract" for f in out["findings"])

    asyncio.run(_with_server(handler))
