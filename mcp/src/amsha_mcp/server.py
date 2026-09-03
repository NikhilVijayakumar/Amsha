"""Amsha MCP stdio server — tool registration and entrypoint."""
from __future__ import annotations

import mcp.server.stdio
from mcp.server.fastmcp import FastMCP

from .tools import architecture, evaluate, improve, install, methodology, modules, plan, search, smoke, verification

# Import the heavy crew_forge domain models in the MAIN thread at startup.
# Lazily importing CrewAI's models (transitively CrewAI) from inside a FastMCP
# worker thread deadlocks this stdio server; importing once here, before the
# event loop runs, completes the CrewAI import so verify/smoke tools never hit
# the lazy-import-in-thread path.
import amsha.crew_forge.domain.models.agent_data  # noqa: E402,F401  (deadlock guard)
import amsha.crew_forge.domain.models.task_data  # noqa: E402,F401

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


def _result_dict(res):
    return {"passed": res.passed, "summary": res.summary,
            "findings": [{"severity": f.severity, "rule_id": f.rule_id,
                           "rule_source": f.rule_source, "message": f.message,
                           "suggested_fix": f.suggested_fix} for f in res.findings]}


@mcp.tool()
def verify_component(component_type: str, definition: dict) -> dict:
    """Verify a single component (agent/task/crew/flow/knowledge/skill/tool/mcp) against Amsha methodology rules. Returns a FindingsReport (severity/rule_id/rule_source/message/suggested_fix). Never rewrites — a judge, not a generator."""
    return _result_dict(verification.verify_component(component_type, definition))


@mcp.tool()
def verify_crew_yaml(crew_dir: str) -> dict:
    """Verify a full crew configuration directory (agents/*_agent.yaml, tasks/*_task.yaml) against the real crew_forge Pydantic schemas and methodology rules. Validates, never rewrites. Expects the standard Amsha crew_forge layout."""
    return _result_dict(verification.verify_crew_yaml(crew_dir))


@mcp.tool()
def verify_crew_def(crew_def: dict) -> dict:
    """Verify a single crew definition's lifecycle settings (memory/tracing/checkpoint) from a job_config.yaml crew block. Validates the field shapes against CrewData's rules and flags tracing-without-privacy-ack, memory-without-retention-need, and checkpoint-without-on_events. Validates, never rewrites."""
    return _result_dict(verification.verify_crew_def(crew_def))


@mcp.tool()
def verify_job_config(job_config_path: str) -> dict:
    """Verify every crew block (memory/tracing/checkpoint) in a job_config.yaml. Validates, never rewrites."""
    return _result_dict(verification.verify_job_config(job_config_path))


@mcp.tool()
def verify_prerequisite_artifacts(artifacts: dict) -> dict:
    """Verify filled prerequisite design artifacts (stage keys '00'-'09') for completeness and cross-stage consistency (process<->contract<->flow agreement)."""
    return _result_dict(verification.verify_prerequisite_artifacts(artifacts))


@mcp.tool()
def verify_prerequisite_files(doc_dir: str, pattern: str = "*.md") -> dict:
    """Verify a user's prerequisite documentation as markdown files: scans doc_dir, extracts the YAML blocks each .md embeds, attributes them to stages 00-09, and reports which stages are present, missing, or unattributable. Lets a user document in markdown (not JSON) and still get the same prerequisite verification. Validates, never rewrites."""
    return _result_dict(verification.verify_prerequisite_files(doc_dir, pattern))


@mcp.tool()
def verify_alignment(agents: list[dict], tasks: list[dict]) -> dict:
    """Verify agent-task alignment: unassigned tasks, unused agents, domain mismatch, capability gaps, overlap."""
    return _result_dict(verification.verify_alignment(agents, tasks))


@mcp.tool()
def suggest_fixes(findings: list[dict], component_type: str = "") -> dict:
    """Turn a Phase-3 FindingsReport into concrete, draft fix suggestions (one per finding). Drafts are proposed, never applied."""
    return improve.suggest_fixes(findings, component_type)


@mcp.tool()
def apply_fixes(suggestions: list[dict], approved_indices: list[int], target_files: list[str]) -> dict:
    """Apply ONLY the explicitly approved fix suggestions (by index). Produces a git-visible diff per applied fix. Unapproved indices are skipped, never applied."""
    return improve.apply_fixes(suggestions, approved_indices, target_files)


@mcp.tool()
def dry_run_parse(crew_dir: str) -> dict:
    """Fastest gate: parse every agent/task YAML against the real crew_forge Pydantic schemas with NO execution. Returns ok/parsed/errors."""
    return smoke.dry_run_parse(crew_dir)


@mcp.tool()
def smoke_test(crew_dir: str, module_name: str = "module", output_dir: str = ".Amsha/smoke") -> dict:
    """Bounded offline smoke test: parse AND assemble the crew graph through the real CrewParser + builder under a hard timeout (stub LLM, no network, no kickoff). Proves plumbing, not design."""
    return smoke.smoke_test(crew_dir, module_name, output_dir)


@mcp.tool()
def score_crew(crew_dir: str, smoke_output: dict | None = None) -> dict:
    """Score a crew against the methodology rubric (Phase 3 checks rolled into 0-100 component scores). Optionally blends in a smoke_test outcome."""
    return evaluate.score_crew(crew_dir, smoke_output)


@mcp.tool()
def evaluate_design(prerequisite_artifacts: dict, crew_dir: str) -> dict:
    """Score whether the assembled crew faithfully realizes the validated design: prerequisite completeness (design) + crew checks (realization)."""
    return evaluate.evaluate_design(prerequisite_artifacts, crew_dir)


@mcp.tool()
def verify_user_plan(prerequisites: dict, goal: dict) -> dict:
    """Semantically verify a user's prerequisite plan: the goal stays within the declared boundary, every stated goal step is covered by the decomposition, and the failure plan covers each process. Extends verify_prerequisite_artifacts; read-only."""
    return plan.verify_user_plan(prerequisites, goal)


@mcp.tool()
def recommend_components(step: str, capabilities: dict | None = None) -> dict:
    """Recommend the Amsha-native components that fit a validated step, least-powerful-first (deterministic -> Task -> Agent -> Crew -> Flow), each with purpose, config keys, and a real reference. Read-only, grounded in what Amsha ships."""
    return plan.recommend_components(step, capabilities)


@mcp.tool()
def find_agent(needs: str) -> dict:
    """Find existing Amsha Agent patterns (plus wiring) that embody a capability need. Read-only."""
    return plan.find_agent(needs)


@mcp.tool()
def find_task(needs: str) -> dict:
    """Find existing Amsha Task patterns (knowledge/tool wiring) for a capability need. Read-only."""
    return plan.find_task(needs)


@mcp.tool()
def find_flow(needs: str) -> dict:
    """Find existing Amsha Flow / orchestration patterns for a capability need. Read-only."""
    return plan.find_flow(needs)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()