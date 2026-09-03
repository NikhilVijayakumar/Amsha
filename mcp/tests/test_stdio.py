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


# ---------------------------------------------------------------------------
# Phase 4 — Improve / Test / Evaluate loop (proposal 04)
# ---------------------------------------------------------------------------

PHASE4_TOOLS = {"suggest_fixes", "apply_fixes", "dry_run_parse",
                "smoke_test", "score_crew", "evaluate_design"}


def test_phase4_tools_registered():
    assert PHASE4_TOOLS <= _list_tools(), f"missing {PHASE4_TOOLS - _list_tools()}"


def test_dry_run_parse_catches_broken_schema():
    from amsha_mcp.tools.smoke import dry_run_parse
    out = dry_run_parse(FIXTURES / "broken_schema")
    assert out["ok"] is False
    assert any("goal" in e["error"] for e in out["errors"])


def test_smoke_test_reads_build_not_design():
    """bad_crew is badly DESIGNED, not broken — it must parse AND build."""
    from amsha_mcp.tools.smoke import dry_run_parse, smoke_test
    assert dry_run_parse(FIXTURES / "bad_crew")["ok"] is True
    assert smoke_test(FIXTURES / "bad_crew")["ok"] is True


def test_smoke_test_surfaces_structural_break():
    """broken_build parses but cannot assemble a crew (agent with no task)."""
    from amsha_mcp.tools.smoke import dry_run_parse, smoke_test
    assert dry_run_parse(FIXTURES / "broken_build")["ok"] is True
    assert smoke_test(FIXTURES / "broken_build")["ok"] is False


def test_smoke_test_offline_stub_never_generates():
    """The stub LLM must never be reached — build is offline by construction."""
    from amsha_mcp.tools.smoke import smoke_test
    out = smoke_test(FIXTURES / "valid_crew")
    assert out["ok"] is True
    assert "stub" not in out.get("traceback", "")


def test_suggest_fixes_god_agent_draft():
    from amsha_mcp.tools.verification import verify_crew_yaml
    from amsha_mcp.tools.improve import suggest_fixes
    res = verify_crew_yaml(FIXTURES / "bad_crew")
    findings = [{"severity": f.severity, "rule_id": f.rule_id,
                 "rule_source": f.rule_source, "message": f.message,
                 "suggested_fix": f.suggested_fix} for f in res.findings]
    sug = suggest_fixes(findings, "crew")
    god = [s for s in sug["suggestions"] if s["rule_id"] == "agent.god_scope"]
    assert god, "god_scope finding should yield a suggestion"
    assert god[0]["draft"].strip()
    assert sug["count"] == len(findings)


def test_apply_fixes_unapproved_is_noop(tmp_path):
    """apply_fixes on a suggestion that is NOT approved must be a no-op."""
    from amsha_mcp.tools.improve import suggest_fixes, apply_fixes
    target = tmp_path / "agent.yaml"
    original = "agent:\n  role: Universal Master Genius\n  goal: do everything anywhere\n"
    target.write_text(original, encoding="utf-8")
    sug = suggest_fixes([{"rule_id": "agent.god_scope", "rule_source": "x",
                          "message": "m", "suggested_fix": "split it"}], "agent")
    sulist = [dict(s, target=str(target)) for s in sug["suggestions"]]
    out = apply_fixes(sulist, approved_indices=[], target_files=[])
    assert out["applied"] == []
    assert len(out["skipped"]) == 1
    assert target.read_text(encoding="utf-8") == original


def test_apply_fixes_approved_applies_and_diffs(tmp_path):
    from amsha_mcp.tools.improve import suggest_fixes, apply_fixes
    target = tmp_path / "agent.yaml"
    original = "agent:\n  role: Universal Master Genius\n  goal: do everything\n"
    target.write_text(original, encoding="utf-8")
    sug = suggest_fixes([{"rule_id": "agent.god_scope", "rule_source": "x",
                          "message": "m", "suggested_fix": "re-scope"}], "agent")
    sulist = [dict(s, target=str(target)) for s in sug["suggestions"]]
    out = apply_fixes(sulist, approved_indices=[0], target_files=[])
    assert len(out["applied"]) == 1
    assert out["applied"][0]["diff"]
    assert target.read_text(encoding="utf-8") != original


def test_score_crew_separates_runs_from_right():
    """bad_crew builds (smoke ok) yet scores worse than valid_crew (design)."""
    from amsha_mcp.tools.smoke import smoke_test
    from amsha_mcp.tools.evaluate import score_crew
    assert smoke_test(FIXTURES / "bad_crew")["ok"] is True
    bad = score_crew(FIXTURES / "bad_crew")["overall"]
    good = score_crew(FIXTURES / "valid_crew")["overall"]
    assert bad["score"] < good["score"]
    assert good["verdict"] == "pass"


def test_evaluate_design_over_stdio():
    async def handler(session):
        artifacts = {
            "00": {"problem": "p", "start_condition": "a", "desired_end_condition": "b",
                   "primary_objective": "c", "constraints": [], "success_definition": "d"},
            "02": {"processes": [{"id": "p1"}]},
            "03": {"contracts": [{"id": "c1", "name": "C1", "purpose": "x"}]},
        }
        out = await _call_in(session, "evaluate_design",
                             {"prerequisite_artifacts": artifacts,
                              "crew_dir": str(FIXTURES / "valid_crew")})
        assert "design" in out and "realization" in out
        assert "score" in out["design"] and "score" in out["realization"]

    asyncio.run(_with_server(handler))


def test_phase4_smoke_over_stdio():
    async def handler(session):
        out = await _call_in(session, "smoke_test", {"crew_dir": str(FIXTURES / "bad_crew")})
        assert out["ok"] is True
        assert out["agents"] == 1 and out["tasks"] == 1

    asyncio.run(_with_server(handler))


# ---------------------------------------------------------------------------
# Phase 5 — User plan verification & component discovery (proposal 05, addendum)
# ---------------------------------------------------------------------------

PHASE5_TOOLS = {"verify_user_plan", "recommend_components",
                "find_agent", "find_task", "find_flow"}


def test_phase5_tools_registered():
    assert PHASE5_TOOLS <= _list_tools(), f"missing {PHASE5_TOOLS - _list_tools()}"


def _plan_artifacts(obj, scope, processes, fails):
    """Structurally complete prerequisite artifacts (all required stage fields)."""
    ctr = [{"id": p["id"], "name": p["name"], "purpose": "purpose"} for p in processes]
    return {
        "00": {"problem": obj, "start_condition": "s", "desired_end_condition": "e",
               "primary_objective": obj, "constraints": [], "success_definition": "done"},
        "01": {"start_boundary": "", "end_boundary": "", "scope": scope,
               "completion_definition": "done"},
        "02": {"start_state": "s", "end_state": "e", "processes": processes, "relationships": []},
        "03": {"contracts": ctr},
        "04": {"validation": "ok"},
        "05": {"flow_order": [], "transitions": [], "state_requirements": {}},
        "06": {"failures": fails, "recovery": ["retry"], "unrecoverable_definition": "none"},
        "07": {"capabilities": []},
        "08": {"validation": "ok"},
        "09": {"checklist": []},
    }


def test_phase5_verify_user_plan_rejects_incoherent():
    """A goal that exceeds the boundary AND omits a step from the decomposition
    must be rejected with findings naming the mismatch (proposal 05 test bar)."""
    from amsha_mcp.tools.plan import verify_user_plan
    artifacts = _plan_artifacts(
        "Summarize finance reports", "summarize marketing documents",
        [{"id": "p1", "name": "analyze_marketing"}], "analyze_marketing recovery")
    out = verify_user_plan(artifacts, {
        "objective": "Summarize finance reports",
        "steps": ["Read the reports", "Produce a summary"],
    })
    assert out["passed"] is False
    ids = {f["rule_id"] for f in out["findings"]}
    assert "plan.goal_exceeds_boundary" in ids
    assert "plan.decomposition_gap" in ids
    bound = [f for f in out["findings"] if f["rule_id"] == "plan.goal_exceeds_boundary"]
    gap = [f for f in out["findings"] if f["rule_id"] == "plan.decomposition_gap"]
    assert "finance" in bound[0]["message"]
    assert any("Read the reports" in g["message"] for g in gap)


def test_phase5_verify_user_plan_passes_coherent():
    """A goal within the boundary, steps covered, failure plan covering every
    process yields a semantic pass (structural base stays clean)."""
    from amsha_mcp.tools.plan import verify_user_plan
    artifacts = _plan_artifacts(
        "Categorize marketing feedback", "marketing feedback analysis",
        [{"id": "p1", "name": "preprocess_feedback"},
         {"id": "p2", "name": "categorize_feedback"}],
        "preprocess_feedback categorize_feedback")
    out = verify_user_plan(artifacts, {
        "objective": "Categorize marketing feedback",
        "steps": ["Preprocess feedback", "Categorize feedback"],
    })
    assert out["passed"] is True, out["summary"]
    assert out["semantic"] == "pass"


def test_phase5_recommend_docling_least_powerful():
    """'summarize a directory of PDFs' must recommend the Task-with-Docling
    (least powerful) ahead of any Agent, citing the real docling source and a
    capability ladder ordering task < agent < crew."""
    from amsha_mcp.tools.plan import recommend_components
    out = recommend_components("summarize a directory of PDFs")
    assert out["matched"] >= 1
    first = out["recommendations"][0]
    assert first["rank"] == 1
    assert first["least_powerful"] is True
    assert first["kind"] == "task"
    assert "Docling" in first["mechanism"]
    assert "amsha_crew_docling_source.py" in first["reference"]
    assert not any(r["kind"] == "agent" and r["rank"] < first["rank"]
                   for r in out["recommendations"])

    # ladder: a query that genuinely needs an Agent AND a Crew still orders
    # task(Docling) < agent < crew
    lad = recommend_components(
        "write a professional analytical summary of a directory of documents")
    ranks = {r["kind"]: r["rank"] for r in lad["recommendations"]}
    assert ranks["task"] < ranks["agent"] < ranks["crew"]


def test_phase5_find_tools_grounded():
    """find_task surfaces real Amsha references, not invented capabilities."""
    from amsha_mcp.tools.plan import find_task
    out = find_task("summarize a directory of PDFs")
    assert out["matched"] >= 1
    assert any("amsha_crew_docling_source.py" in c["reference"] for c in out["components"])
    assert all(c["reference"] for c in out["components"])


def test_phase5_read_only():
    """verify_user_plan / recommend_components must never mutate their input."""
    from amsha_mcp.tools.plan import verify_user_plan, recommend_components
    artifacts = _plan_artifacts(
        "Categorize marketing feedback", "marketing feedback analysis",
        [{"id": "p1", "name": "preprocess_feedback"}],
        "preprocess_feedback")
    import copy
    snapshot = copy.deepcopy(artifacts)
    verify_user_plan(artifacts, {"objective": "Categorize marketing feedback",
                                 "steps": ["Preprocess feedback"]})
    assert artifacts == snapshot
    step = "summarize a directory of PDFs"
    recommend_components(step)
    assert isinstance(step, str)  # untouched


def test_phase5_verify_user_plan_over_stdio():
    async def handler(session):
        artifacts = _plan_artifacts(
            "Summarize finance reports", "summarize marketing documents",
            [{"id": "p1", "name": "analyze_marketing"}], "analyze_marketing recovery")
        out = await _call_in(session, "verify_user_plan", {
            "prerequisites": artifacts,
            "goal": {"objective": "Summarize finance reports",
                     "steps": ["Read the reports", "Produce a summary"]},
        })
        assert out["passed"] is False
        ids = {f["rule_id"] for f in out["findings"]}
        assert "plan.goal_exceeds_boundary" in ids
        assert "plan.decomposition_gap" in ids

        out2 = await _call_in(session, "recommend_components",
                              {"step": "summarize a directory of PDFs"})
        assert out2["recommendations"][0]["kind"] == "task"
        assert "Docling" in out2["recommendations"][0]["mechanism"]

    asyncio.run(_with_server(handler))
