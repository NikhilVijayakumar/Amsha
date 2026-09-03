from __future__ import annotations

import difflib
from dataclasses import dataclass, field
from pathlib import Path

import yaml

_RULE_FIX_TEMPLATES: dict[str, str] = {
    "agent.god_scope": (
        "# Split the multi-discipline agent into focused single-responsibility agents.\n"
        "# e.g. one per professional discipline, each with a bounded role/goal/backstory."
    ),
    "agent.role_vague": (
        "# Replace the generic role with a concrete professional title that bounds scope,\n"
        "# e.g. 'Narrative Continuity Editor' instead of 'AI Assistant'."
    ),
    "agent.role_professional_test": (
        "# Rename the role to a professional noun (Editor, Analyst, Researcher) rather than a\n"
        "# technical component (validator, processor, generator)."
    ),
    "agent.seniority_inflated": (
        "# Tone down the title; seniority must be earned by task complexity, not a grand title."
    ),
    "agent.backstory_capability_dump": (
        "# Trim the backstory to one professional identity; remove unrelated capability claims."
    ),
    "agent.backstory_dynamic_knowledge": (
        "# Move project-specific facts/versions/dates out of the backstory into a Knowledge source.\n"
        "# The persona must stay static."
    ),
    "agent.backstory_task_instructions": (
        "# Remove imperative workflow steps from backstory/goal; orchestration belongs in a Flow."
    ),
    "agent.backstory_biography_bloat": (
        "# Replace theatrical biography with concrete professional context and constraints."
    ),
    "agent.goal_is_task": (
        "# State an enduring responsibility in the goal, not a task spec with steps/outputs."
    ),
    "agent.scope_too_broad": (
        "# Bound the role to one professional responsibility."
    ),
    "agent.tools_justify_each": (
        "# Prune tools to those actually used by this agent's tasks."
    ),
    "agent.knowledge_justify_each": (
        "# Trim knowledge sources to what the assigned tasks reference."
    ),
    "agent.skill_justify_each": (
        "# Trim skills to those whose methodology the assigned tasks apply."
    ),
    "agent.reasoning_unjustified": (
        "# Set reasoning: false unless the tasks require genuine multi-factor judgment."
    ),
    "agent.prompt_footprint": (
        "# Cut duplication and keep role+goal+backstory minimal."
    ),
    "agent.backstory_contains_knowledge": (
        "# Move domain content to a Knowledge source; keep the persona as role only."
    ),
    "agent.knowledge_duplicated_in_backstory": (
        "# Keep facts in Knowledge only; strip them from the persona."
    ),
    "agent.delegation_enabled_no_crew": (
        "# Define the delegatees and termination criteria, or set allow_delegation: false."
    ),
    "task.god_lifecycle": (
        "# Split into atomic tasks, one transformation and one deliverable each."
    ),
    "task.multiple_outputs": (
        "# Split into separate tasks, one deliverable each."
    ),
    "task.multiple_validation_criteria": (
        "# Split validation domains into separate tasks."
    ),
    "task.multiple_human_decisions": (
        "# Move the human gate into the Flow as an explicit human_input step."
    ),
    "task.composite_output_contract": (
        "# Decompose into a chain of atomic contracts."
    ),
    "task.micro_fragmentation": (
        "# Merge into one meaningful transformation; avoid one task per mechanical step."
    ),
    "task.deterministic_work_assigned_agent": (
        "# Replace this agent task with a deterministic Python step (least-powerful tool)."
    ),
    "task.structural_validation_by_agent": (
        "# Move schema/required-field checks to deterministic Python code."
    ),
    "task.input_not_declared": (
        "# Declare each required input explicitly."
    ),
    "task.required_input_unavailable": (
        "# Ensure every required input has a producer (upstream task, flow input, or documented source)."
    ),
    "task.context_missing_link": (
        "# Point context at the exact upstream task output."
    ),
    "task.context_over_propagation": (
        "# Inject only the specific upstream outputs this task needs."
    ),
    "task.hidden_flow_decision": (
        "# Move control decisions to the Flow; the task should be one straight transformation."
    ),
    "task.state_versus_context_confusion": (
        "# Inject only task-relevant context, never wholesale flow state."
    ),
    "crew.single_agent_crew": (
        "# Use a single Agent+Task, or add real collaborators."
    ),
    "crew.god_crew": (
        "# Split into one crew per bounded process."
    ),
    "crew.decorative_no_value": (
        "# Give each agent genuine work that requires collaboration, or use a Flow."
    ),
    "crew.agent_collection": (
        "# Define a shared bounded outcome, or split into separate crews."
    ),
    "crew.sequential_flow_camouflage": (
        "# Use a Flow for linear sequencing; keep a crew only for genuine collaboration."
    ),
    "crew.agent_duplication": (
        "# Merge into one agent or define distinct specializations."
    ),
    "crew.coverage_gap": (
        "# Add an agent covering the missing responsibility."
    ),
    "crew.unbounded_collaboration": (
        "# Define a max-round limit or explicit success/termination criteria."
    ),
    "crew.process_param_mismatch": (
        "# Set process to match the dependency structure."
    ),
    "crew.process_hierarchical_no_manager": (
        "# Define a manager/lead agent, or switch to a bounded collaboration model."
    ),
    "flow.hidden_workflow_in_agent": (
        "# Promote control logic to explicit Flow transitions."
    ),
    "flow.implicit_transitions": (
        "# Declare explicit transitions (from/to/condition) for every step."
    ),
    "flow.unbounded_loop": (
        "# Add max_attempts/limit and an exhausted terminal outcome."
    ),
    "flow.state_dump": (
        "# Keep only state that needs cross-step retention; give each field an owner and lifetime."
    ),
    "flow.state_unowned": (
        "# Declare an owner and lifetime for each state field."
    ),
    "flow.deterministic_routing_by_llm": (
        "# Use deterministic Python for status/field-based routing."
    ),
    "flow.terminal_states_ambiguous": (
        "# Declare distinct terminal states and success criteria."
    ),
    "flow.human_gate_hidden": (
        "# Make the human gate an explicit human_input node with outcomes."
    ),
    "flow.god_flow": (
        "# Decompose the flow into focused steps, one responsibility each."
    ),
    "knowledge.skill_mislabel": (
        "# Move procedural instructions to a Skill; Knowledge holds reference facts."
    ),
    "skill.knowledge_mislabel": (
        "# Relabel as Knowledge, or add the actual methodology."
    ),
    "tool.giant_tool": (
        "# Expose a narrow capability instead of a universal tool."
    ),
    "tool.everywhere": (
        "# Attach the tool only to agents whose tasks need it."
    ),
    "tool.not_justified_by_task": (
        "# Document which task requires this tool."
    ),
    "tool.credentials_embedded": (
        "# Reference credentials via a secure source; never embed literals."
    ),
    "mcp.defined_but_unreachable": (
        "# Provide a valid endpoint and transport."
    ),
    "mcp.unrestricted_every_server": (
        "# Enumerate only the specific capabilities needed."
    ),
    "mcp.read_write_misgrant": (
        "# Grant read only."
    ),
    "mcp.transport_unsupported": (
        "# Use a supported transport (stdio, http, sse)."
    ),
    "mcp.everywhere": (
        "# Attach MCP only where an external capability is actually required."
    ),
    "mcp.credentials_in_context": (
        "# Inject credentials from a secure source at runtime."
    ),
}

_GENERIC_FIX = "# Review the reported rule and apply its stated suggested_fix."


@dataclass
class SuggestedFix:
    rule_id: str
    findings_index: int
    draft: str
    source: str


def suggest_fixes(findings: list[dict], component_type: str = "") -> dict:
    """Turn a Phase-3 FindingsReport into concrete, draft fix suggestions.

    Drafts are proposed, never applied.

    Args:
        findings: list of finding dicts ({severity, rule_id, rule_source, message, suggested_fix})
        component_type: optional component label for context.

    Returns:
        dict with {'suggestions': [{'rule_id', 'draft', 'source'}], 'count', 'component_type'}
    """
    suggestions: list[dict] = []
    for i, f in enumerate(findings):
        rule_id = f.get("rule_id", "")
        template = _RULE_FIX_TEMPLATES.get(rule_id, _GENERIC_FIX)
        draft = f.get("suggested_fix") or template
        suggestions.append({
            "rule_id": rule_id,
            "findings_index": i,
            "source": f.get("rule_source", ""),
            "draft": draft,
        })
    return {"suggestions": suggestions, "count": len(suggestions), "component_type": component_type}


@dataclass
class FixApplied:
    filename: str
    proposed: str
    applied: bool
    reason: str = ""


def _make_diff(original: str, updated: str, filename: str) -> str:
    lines = original.splitlines(keepends=True)
    newlines = updated.splitlines(keepends=True)
    diff = difflib.unified_diff(lines, newlines, fromfile=filename, tofile=f"{filename} (fixed)")
    return "".join(diff)


def apply_fixes(suggestions: list[dict], approved_indices: list[int],
                target_files: list[str]) -> dict:
    """Apply only the explicitly approved fix suggestions, producing a diff for each.

    Approval is explicit per suggestion by index; anything not approved is a no-op.

    Args:
        suggestions: the list returned by suggest_fixes.
        approved_indices: indices into suggestions the caller approves.
        target_files: one target file path per suggestion (parallel to suggestions),
            or read from each suggestion's 'target' key.

    Returns:
        dict with {'applied': [{'rule_id', 'filename', 'diff'}], 'skipped': [...], 'count'}
    """
    approved = set(approved_indices)
    applied: list[dict] = []
    skipped: list[dict] = []
    for i, s in enumerate(suggestions):
        rule_id = s.get("rule_id", "")
        draft = s.get("draft", "")
        target = s.get("target") or (target_files[i] if i < len(target_files) else None)
        if i not in approved:
            skipped.append({"rule_id": rule_id, "reason": "not approved"})
            continue
        if not target:
            skipped.append({"rule_id": rule_id, "reason": "no target file"})
            continue
        path = Path(target)
        if not path.exists() or not path.is_file():
            skipped.append({"rule_id": rule_id, "reason": f"target not found: {target}"})
            continue
        original = path.read_text(encoding="utf-8")
        if rule_id in {
            "agent.god_scope", "agent.role_vague", "agent.role_professional_test",
            "agent.scope_too_broad", "agent.seniority_inflated",
        }:
            updated = _re_scope_agent(original, draft)
        elif rule_id in {"task.god_lifecycle", "task.multiple_outputs", "task.composite_output_contract"}:
            updated = _append_draft(original, draft)
        else:
            updated = _append_draft(original, draft)
        if updated == original:
            skipped.append({"rule_id": rule_id, "reason": "no change"})
            continue
        path.write_text(updated, encoding="utf-8")
        applied.append({"rule_id": rule_id, "filename": str(path), "diff": _make_diff(original, updated, str(path))})
    return {"applied": applied, "skipped": skipped,
            "count": {"applied": len(applied), "skipped": len(skipped)}}


def _re_scope_agent(original: str, draft: str) -> str:
    try:
        data = yaml.safe_load(original)
    except yaml.YAMLError:
        return _append_draft(original, draft)
    agent = data.get("agent", data) if isinstance(data, dict) else data
    if isinstance(agent, dict):
        role = agent.get("role")
        if isinstance(role, str):
            if "universal" in role.lower() or "master" in role.lower() or role.lower() in _VAGUEROLES:
                agent["role"] = "Bounded Professional"
        if "role" not in agent:
            agent["role"] = "Bounded Professional"
        agent.pop("reasoning", None)
    updated = yaml.safe_dump(data, sort_keys=False, allow_unicode=True)
    return (draft + "\n\n" + updated)


_VAGUEROLES = {
    "ai assistant", "general ai", "ai expert", "assistant",
    "content specialist", "general assistant", "helper",
}


def _append_draft(original: str, draft: str) -> str:
    return original.rstrip("\n") + "\n\n" + draft + "\n"
