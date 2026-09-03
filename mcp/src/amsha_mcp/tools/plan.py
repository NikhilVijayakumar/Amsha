"""Phase 5: user-plan verification (semantic) and component discovery.

Two read-only capabilities layered on the Phase 3 prerequisite artifacts:

1. ``verify_user_plan`` — extends ``verify_prerequisite_artifacts`` from
   *structural* to *semantic* coherence: the stated goal must stay inside the
   declared boundary, every step the user believes achieves the goal must be
   covered by the decomposition, and the failure plan must cover each process.

2. Discovery — ``recommend_components`` walks the capability ladder
   (deterministic -> Task -> Agent -> Crew -> Flow) least-powerful-first, and
   ``find_agent`` / ``find_task`` / ``find_flow`` search a catalog grounded in
   real Amsha sources (knowledge classes, tool_registry, McpServerConfig).

Nothing here writes a crew, edits a plan, or applies a fix.
"""

from __future__ import annotations

from .verification import (
    _extract_domains,
    verify_prerequisite_artifacts,
)


def _result(findings) -> dict:
    passed = not any(f.severity == "error" for f in findings)
    errs = sum(1 for f in findings if f.severity == "error")
    warns = sum(1 for f in findings if f.severity == "warning")
    advs = sum(1 for f in findings if f.severity == "advisory")
    return {
        "passed": passed,
        "summary": f"{errs} errors, {warns} warnings, {advs} advisories",
        "findings": [
            {"severity": f.severity, "rule_id": f.rule_id,
             "rule_source": f.rule_source, "message": f.message,
             "suggested_fix": f.suggested_fix}
            for f in findings
        ],
    }


# ── Capability 1: verify the user's prerequisite plan ────────────────────────

def _f(severity, rule_id, source, message, fix=""):
    from .verification import _finding
    return _finding(severity, rule_id, source, message, fix)


def _process_names(prerequisites: dict) -> list[str]:
    procs = (prerequisites.get("02") or {}).get("processes") or []
    names = []
    if isinstance(procs, list):
        for p in procs:
            if isinstance(p, dict):
                names.append(str(p.get("name") or p.get("id") or "").lower())
            else:
                names.append(str(p).lower())
    return [n for n in names if n]


def _boundary_text(prerequisites: dict) -> str:
    a = prerequisites.get("01") or {}
    return " ".join(str(a.get(k, "")) for k in ("scope", "start_boundary", "end_boundary"))


def _goal_domains_outside_boundary(objective: str, boundary: str) -> list[str]:
    goal_doms = _extract_domains(objective)
    bdry_doms = _extract_domains(boundary)
    return sorted(goal_doms - bdry_doms)


def _failure_text(prerequisites: dict) -> str:
    a = prerequisites.get("06") or {}
    parts = [str(a.get("failures", ""))]
    recovery = a.get("recovery")
    if isinstance(recovery, list):
        parts.append(" ".join(str(r) for r in recovery if r))
    elif recovery:
        parts.append(str(recovery))
    return " ".join(parts).lower()


def verify_user_plan(prerequisites: dict, goal: dict) -> dict:
    """Semantically verify a user's prerequisite plan for coherence.

    Structural completeness of the artifacts is checked by the Phase 3 engine;
    this adds the semantic checks: the goal stays within the declared boundary,
    every stated goal step is covered by the decomposition, and the failure
    plan covers each decomposed process.

    Args:
        prerequisites: stage-keyed ("00"-"09") prerequisite artifacts dict.
        goal: {"objective": str, "steps": [str, ...]} — the user's goal and the
            steps they believe achieve it.

    Returns:
        FindingsReport plus a top-level ``semantic`` verdict. Read-only.
    """
    base = verify_prerequisite_artifacts(prerequisites)
    findings = list(base.findings)

    objective = str((goal or {}).get("objective", "")).strip()
    steps = [(goal or {}).get("steps") or []]

    if objective:
        boundary = _boundary_text(prerequisites)
        if not boundary:
            findings.append(_f(
                "error", "plan.goal_vs_boundary_no_boundary",
                "prerequisite/01-goal-and-boundary-definition",
                "A goal is stated but no boundary (scope/start/end) is declared "
                "in prerequisite 01, so the plan's boundary cannot be checked.",
                "Declare the scoped boundary before verifying the goal."))
        else:
            stray = _goal_domains_outside_boundary(objective, boundary)
            if stray:
                findings.append(_f(
                    "error", "plan.goal_exceeds_boundary",
                    "prerequisite/01-goal-and-boundary-definition",
                    f"Goal '{objective}' introduces domain(s) {stray} that are "
                    f"not covered by the declared boundary '{boundary[:120]}'.",
                    "Either narrow the goal to the declared boundary or widen "
                    "the boundary to legitimately include these domains."))

    procs = _process_names(prerequisites)
    for step in steps[0] if steps and steps[0] else []:
        s = str(step).strip()
        if not s:
            continue
        step_tokens = [t for t in s.lower().split() if len(t) > 3]
        covered = any(
            (t in name or name in t) for name in procs for t in step_tokens
        ) or any(_extract_domains(s) & _extract_domains(name) for name in procs)
        if not covered:
            findings.append(_f(
                "error", "plan.decomposition_gap",
                "prerequisite/02-process-decomposition",
                f"Goal step '{s}' has no matching process in the "
                f"decomposition (processes: {procs or 'none'}).",
                "Add a process that realizes this step, or remove the "
                "step from the goal."))

    fail_text = _failure_text(prerequisites)
    for name in procs:
        if fail_text and name and name not in fail_text:
            findings.append(_f(
                "warning", "plan.failure_plan_coverage",
                "prerequisite/06-corner-cases-and-failure-planning",
                f"Process '{name}' has no matching entry in the failure plan "
                f"(failures/recovery of prerequisite 06).",
                "Add a failure entry and recovery path for this process."))

    if not findings:
        findings.append(_f(
            "advisory", "plan.coherent", "prerequisite",
            "The user plan is semantically coherent: goal within boundary, "
            "steps covered by the decomposition, failure plan present.", ""))

    out = _result(findings)
    out["semantic"] = "pass" if out["passed"] else "fail"
    return out


# ── Capability 2: grounded component discovery ───────────────────────────────

# Ladder level per prerequisite/07 §36 (capability escalation ladder).
_LADDER = {"python": 0, "task": 1, "agent": 2, "crew": 3, "flow": 4}

# Hand-curated catalog of capabilities Amsha actually ships. Every reference is
# a real source: knowledge classes under crew_forge/knowledge/, tool_registry.py,
# McpServerConfig (crew_forge/domain/models/mcp_data.py), and the implementation/
# docs. Catalog prose is ours; the grounded references are real.
_COMPONENT_CATALOG = [
    {
        "id": "python_deterministic",
        "kind": "python",
        "name": "Deterministic Python",
        "purpose": "Rules, validation, calculation, transformation, routing — work "
                   "expressible without LLM judgment.",
        "keywords": ["deterministic", "validate", "calculate", "transform", "parse",
                     "sort", "filter", "aggregate", "rule", "checksum", "score"],
        "config_keys": [],
        "ref": "prerequisite/07-capability-selection.md",
        "wire": "Plain Python module; no crewai construct. Prefer this before any Agent.",
    },
    {
        "id": "task_docling_summarize",
        "kind": "task",
        "name": "Task with Docling Knowledge Source",
        "purpose": "Summarize / extract / ingest a directory of documents (PDF, DOCX, "
                   "TXT, XLSX, images, HTML) by feeding them through the Docling "
                   "knowledge source inside a bounded Task.",
        "keywords": ["summarize", "document", "documents", "pdf", "pdfs", "directory",
                     "ingest", "extract", "conversion", "markdown", "docling"],
        "config_keys": ["knowledge_sources", "llm"],
        "ref": "crew_forge/knowledge/amsha_crew_docling_source.py",
        "wire": "Point the Task's knowledge_sources at AmshaCrewDoclingSource; the "
                "Task LLM does the summarizing. Least-powerful fit for doc summarization.",
    },
    {
        "id": "task_json_source",
        "kind": "task",
        "name": "Task with JSON Knowledge Source",
        "purpose": "Ground a Task in structured JSON reference data loaded locally "
                   "via the Amsha JSON knowledge source.",
        "keywords": ["json", "structured", "data", "records", "knowledge", "load",
                     "reference"],
        "config_keys": ["knowledge_sources", "llm"],
        "ref": "crew_forge/knowledge/amsha_json_knowledge_source.py",
        "wire": "Wire AmshaJsonKnowledgeSource into the Task's knowledge_sources.",
    },
    {
        "id": "task_tool_file_ops",
        "kind": "task",
        "name": "Tool-based File Operation Task",
        "purpose": "Read files / list a directory as tool calls inside a Task using "
                   "the registry's file_read / directory_read tools.",
        "keywords": ["file", "read", "directory", "list", "tool", "filesystem"],
        "config_keys": ["tools"],
        "ref": "crew_forge/service/tool_registry.py",
        "wire": "resolve_tools(['file_read', 'directory_read']) into the Task's tools.",
    },
    {
        "id": "agent_specialist",
        "kind": "agent",
        "name": "Specialist Agent + Task",
        "purpose": "A persistent professional capability needing judgment, "
                   "interpretation, generation, or domain reasoning — beyond a "
                   "bounded tool/Lookup Task.",
        "keywords": ["judgment", "interpret", "recommend", "analyze", "advise",
                     "draft", "write", "generate", "professional", "reason"],
        "config_keys": ["role", "goal", "backstory", "tools", "knowledge_sources"],
        "ref": "implementation/01-agent-engineering.md",
        "wire": "Define the agent in agents/*_agent.yaml, pair with a task in "
                "tasks/*_task.yaml. Prefer only when a bounded Task cannot.",
    },
    {
        "id": "crew_multi_specialist",
        "kind": "crew",
        "name": "Crew of Specialists",
        "purpose": "Multiple distinct professional perspectives collaborating, "
                   "cross-reviewing, or debating a single deliverable.",
        "keywords": ["collaborat", "cross-review", "debate", "specialist",
                     "multi-perspective", "independent analysis", "review board"],
        "config_keys": ["agents", "process"],
        "ref": "implementation/06-crew-engineering.md",
        "wire": "Compose several agents into a crew when genuine multi-specialist "
                "collaboration is required, not merely for a large task.",
    },
    {
        "id": "flow_orchestration",
        "kind": "flow",
        "name": "Flow Orchestration",
        "purpose": "Explicit multi-process orchestration: state, transitions, "
                   "conditionals, iteration, parallel branches, human gates, "
                   "checkpointing, recovery.",
        "keywords": ["orchestrate", "workflow", "state machine", "transition",
                     "conditional", "pipeline", "multi-step", "long-running",
                     "checkpoint", "recovery", "parallel"],
        "config_keys": ["flow_state", "transitions"],
        "ref": "implementation/09-flow-engineering.md",
        "wire": "Use when the sequence is known but needs explicit execution "
                "control; Flow ≠ Crew (collaboration).",
    },
    {
        "id": "mcp_external",
        "kind": "mcp",
        "name": "MCP Integration Boundary",
        "purpose": "Expose an external-system capability (ComfyUI, Unreal, shared "
                   "service) through a standardized MCP boundary.",
        "keywords": ["external system", "mcp", "comfyui", "unreal", "integration",
                     "remote service"],
        "config_keys": ["mcp_servers"],
        "ref": "crew_forge/domain/models/mcp_data.py",
        "wire": "Declare an McpServerConfig (stdio/http/sse) on the agent; MCP is an "
                "integration boundary, not a blanket replacement for local tools.",
    },
]


def _score_match(entry: dict, tokens: list[str]) -> int:
    text = (entry["name"] + " " + entry["purpose"] + " " + " ".join(entry["keywords"])).lower()
    return sum(1 for t in tokens if t in text)


def _matches(query: str, catalog: list[dict]) -> list[dict]:
    tokens = [t for t in query.lower().split() if len(t) > 2]
    if not tokens:
        return []
    scored = [(entry, _score_match(entry, tokens)) for entry in catalog]
    return [e for e, s in sorted(scored, key=lambda x: -x[1]) if s > 0]


def _recommendation(entry: dict, rank: int, count: int, reason: str) -> dict:
    return {
        "rank": rank,
        "least_powerful": rank == 1,
        "mechanism": entry["name"],
        "kind": entry["kind"],
        "purpose": entry["purpose"],
        "config_keys": entry["config_keys"],
        "reference": entry["ref"],
        "wire": entry["wire"],
        "reason": reason,
    }


def recommend_components(step: str, capabilities: dict | None = None) -> dict:
    """Recommend the Amsha-native components that fit a validated step.

    Walks the capability ladder (prerequisite/07) least-powerful-first:
    deterministic Python -> Task(-only) -> Agent -> Crew -> Flow. Recommendations
    reference real Amsha sources; nothing is invented or mutated.

    Args:
        step: the validated step / responsibility (natural language).
        capabilities: optional stage-07 capability_selection artifact to constrain
            the catalog (filtered to the capabilities it selects).

    Returns:
        Ordered recommendations (rank 1 = least powerful) plus a summary.
    """
    catalog = _COMPONENT_CATALOG
    if capabilities:
        selected = capabilities.get("capabilities") or []
        if isinstance(selected, list):
            selected_kinds = set()
            for c in selected:
                if isinstance(c, dict):
                    v = str(c.get("capability", "")).lower()
                    if v in _LADDER:
                        selected_kinds.add(v)
            if selected_kinds:
                catalog = [e for e in catalog if e["kind"] in selected_kinds]

    matched = _matches(step, catalog)
    if not matched:
        return {
            "matched": 0,
            "recommendations": [],
            "summary": f"No grounded Amsha component matched '{step}'. "
                       "Narrow the step or describe the required capability.",
        }

    matched.sort(key=lambda e: _LADDER[e["kind"]])
    recs = [_recommendation(e, i + 1, len(matched),
                            f"Matches '{step}' at capability level {_LADDER[e['kind']]}.")
            for i, e in enumerate(matched)]
    return {
        "matched": len(matched),
        "recommendations": recs,
        "summary": f"{len(recs)} candidate(s), least-powerful first: "
                   + " -> ".join(f"{r['kind']}" for r in recs),
    }


def find_agent(needs: str) -> dict:
    """Find existing Amsha Agent patterns (and wiring) that embody *needs*."""
    return _find_kind(needs, "agent")


def find_task(needs: str) -> dict:
    """Find existing Amsha Task patterns (and knowledge/tool wiring) for *needs*."""
    return _find_kind(needs, "task")


def find_flow(needs: str) -> dict:
    """Find existing Amsha Flow / orchestration patterns for *needs*."""
    return _find_kind(needs, "flow")


def _find_kind(needs: str, kind: str) -> dict:
    matches = [e for e in _matches(needs, _COMPONENT_CATALOG) if e["kind"] == kind]
    return {
        "kind": kind,
        "matched": len(matches),
        "components": [
            {"name": e["name"], "purpose": e["purpose"], "config_keys": e["config_keys"],
             "reference": e["ref"], "wire": e["wire"]}
            for e in matches
        ],
        "summary": f"{len(matches)} {kind} pattern(s) matched '{needs}'.",
    }
