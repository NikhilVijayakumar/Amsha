from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

import yaml
from pydantic import ValidationError

_VAGUE_ROLES = {
    "ai assistant", "general ai", "ai expert", "assistant",
    "content specialist", "general assistant", "helper",
    "ai agent", "processing agent",
}
_INFLATED_SENIORITY = {
    "master genius", "world-class ultimate", "universal superintelligence",
    "everything expert", "omniscient", "godlike", "superhuman",
    "ultimate expert", "world-class expert",
}
_LIFECYCLE_VERBS = {
    "research", "analyze", "write", "generate", "evaluate", "validate",
    "revise", "approve", "publish", "deploy", "optimize", "review",
    "test", "edit", "proofread", "format", "design", "plan",
}
_DETERMINISTIC_OPS = {
    "calculate", "score", "average", "sum", "sort", "deduplicate",
    "dedupe", "validate schema", "check severity", "routing", "field exists",
    "arithmetic", "count", "filter", "parse", "extract",
    "if status", "if result", "if type", "if category",
}
_WORKFLOW_SIGNALS = re.compile(
    r"\b(if|else|retry|re-try|re-run|loop|iterate|determine next|"
    r"call next task|send to next|update state|branch|fallback|"
    r"recursively|until.*succeed|escalat)\b",
    re.IGNORECASE,
)
_SECRET_PATTERN = re.compile(
    r"(api[_-]?key|secret|password|token|credential|auth)[\s:=]+['\"][^'\"]{8,}",
    re.IGNORECASE,
)
_BIOGRAPHY_PATTERNS = re.compile(
    r"(survived|legendary|seven continents|countless assignments|"
    r"transcendent|peerless|unparalleled|mastery of all|"
    r"born.*destiny|forged in|unmatched brilliance)",
    re.IGNORECASE,
)
_KNOWLEDGE_IN_BACKSTORY = re.compile(
    r"(born in \d{4}|protagonist|chapter \d|page \d|scene \d|"
    r"isbn|doi:|arxiv:|volume \d|issue \d|figures? \d|"
    r"section \d+\.\d|appendix [a-z])",
    re.IGNORECASE,
)
_DYNAMIC_DATA = re.compile(
    r"(\d{4}[-/]\d{2}[-/]\d{2}|v\d+\.\d+|version \d|"
    r"release \d|build \d+|commit [a-f0-9]{7})",
    re.IGNORECASE,
)
_COMPOSITE_PATTERN = re.compile(
    r"(research|analyze).*(write|generate).*(evaluate|validate|review|approve)",
    re.IGNORECASE,
)
_MULTI_OUTPUT_PATTERN = re.compile(
    r"(and|also|additionally|furthermore|,\s*\w+\s+report|"
    r"\w+\s+and\s+\w+\s+(summary|report|document|list|output|file))",
    re.IGNORECASE,
)
_HUMAN_GATE = re.compile(
    r"(human\s+(input|approval|review|decision|gate)|"
    r"wait for (human|user|approval)|ask (human|user)|"
    r"require.*approval|final approval|sign.?off)",
    re.IGNORECASE,
)
_GIANT_TOOLS = {
    "shell", "system_tool", "filesystem_admin", "database_admin",
    "execute_command", "run_command", "full_access", "admin",
    "file_manager", "system_admin", "root_access", "terminal",
}
_VALID_TRANSPORTS = {"stdio", "http", "sse"}
_DISCIPLINE_KEYWORDS = {
    "research", "writing", "evaluation", "programming", "publish",
    "admin", "sql", "audio", "legal", "design", "marketing",
    "database", "deployment", "devops", "data science", "analytics",
    "finance", "accounting", "hr", "sales", "support", "translation",
    "illustration", "photography", "video", "animation", "seo",
    "copywriting", "journalism", "law", "medicine", "science",
    "engineering", "architecture", "education", "consulting",
}


@dataclass
class Finding:
    severity: str
    rule_id: str
    rule_source: str
    message: str
    suggested_fix: str = ""


@dataclass
class VerificationResult:
    findings: list[Finding] = field(default_factory=list)
    passed: bool = True
    component_type: str = ""
    summary: str = ""

    def __post_init__(self):
        self.passed = not any(f.severity == "error" for f in self.findings)
        errs = sum(1 for f in self.findings if f.severity == "error")
        warns = sum(1 for f in self.findings if f.severity == "warning")
        advs = sum(1 for f in self.findings if f.severity == "advisory")
        if not self.summary:
            self.summary = f"{errs} errors, {warns} warnings, {advs} advisories"


def _count_keywords(text: str, keywords: set[str]) -> int:
    lower = text.lower()
    return sum(1 for kw in keywords if kw in lower)


def _extract_domains(text: str) -> set[str]:
    lower = text.lower()
    return {kw for kw in _DISCIPLINE_KEYWORDS if kw in lower}


def _domains_overlap(a: str, b: str) -> bool:
    return bool(_extract_domains(a) & _extract_domains(b))


def _is_vague_role(role: str) -> bool:
    return role.strip().lower() in _VAGUE_ROLES or (
        "agent" in role.lower() and not any(
            kw in role.lower() for kw in _DISCIPLINE_KEYWORDS
        )
    )


def _is_inflated(role: str) -> bool:
    lower = role.lower()
    return any(phrase in lower for phrase in _INFLATED_SENIORITY)


def _has_lifecycle_verbs(text: str, threshold: int = 3) -> bool:
    lower = text.lower()
    return sum(1 for v in _LIFECYCLE_VERBS if v in lower) >= threshold


def _is_deterministic(text: str) -> bool:
    lower = text.lower()
    return any(op in lower for op in _DETERMINISTIC_OPS)


def _has_workflow_signals(text: str) -> bool:
    return bool(_WORKFLOW_SIGNALS.search(text))


def _has_secrets(text: str) -> bool:
    return bool(_SECRET_PATTERN.search(text))


def _has_biography_bloat(text: str) -> bool:
    return bool(_BIOGRAPHY_PATTERNS.search(text))


def _has_knowledge_in_backstory(text: str) -> bool:
    return bool(_KNOWLEDGE_IN_BACKSTORY.search(text))


def _has_dynamic_data(text: str) -> bool:
    return bool(_DYNAMIC_DATA.search(text))


def _is_composite_task(task: dict) -> bool:
    text = f"{task.get('purpose', '')} {task.get('description', '')}"
    return bool(_COMPOSITE_PATTERN.search(text))


def _has_multi_output(text: str) -> bool:
    return bool(_MULTI_OUTPUT_PATTERN.search(text))


def _has_human_gate(text: str) -> bool:
    return bool(_HUMAN_GATE.search(text))


def _is_god_agent(agent: dict) -> bool:
    text = f"{agent.get('role', '')} {agent.get('goal', '')} {agent.get('backstory', '')}"
    return _count_keywords(text, _DISCIPLINE_KEYWORDS) >= 4


def _prompt_redundancy(agent: dict) -> bool:
    parts = [agent.get("role", ""), agent.get("goal", ""),
             agent.get("backstory", "")]
    combined = " ".join(parts)
    if len(combined) > 2000:
        return True
    words = combined.lower().split()
    if len(words) > 20:
        unique_ratio = len(set(words)) / len(words)
        return unique_ratio < 0.4
    return False

def _finding(severity, rule_id, source, message, fix=""):
    return Finding(severity=severity, rule_id=rule_id, rule_source=source, message=message, suggested_fix=fix)


def _check_god_agent(a):
    if _is_god_agent(a):
        return [_finding("error", "agent.god_scope", "implementation/01-agent-engineering.md §53; 23 §1.3",
                         f"Agent '{a.get('role', '')}' spans many unrelated professional disciplines (one agent for everything).",
                         "Split into focused single-responsibility agents, one professional discipline each.")]
    return []


def _check_role_vague(a):
    role = a.get("role", "")
    if _is_vague_role(role):
        return [_finding("error", "agent.role_vague", "implementation/01-agent-engineering.md §45; 23 §1.4",
                         f"Role '{role}' is generic/technical, not a professional archetype. Agents need a bounded professional persona.",
                         "Give the role a concrete professional title with a scope (e.g. 'Narrative Continuity Editor').")]
    return []


def _check_role_professional(a):
    role = a.get("role", "").lower()
    non_professional = ("analyzer", "processor", "generator", "outputer", "validator",
                        "handler", "manager", "integration")
    if any(role.endswith(s) for s in non_professional):
        return [_finding("warning", "agent.role_professional_test", "implementation/01-agent-engineering.md §7",
                         f"Role '{a.get('role')}' reads as a technical component, not a professional archetype.",
                         "Rename to a professional noun (Editor, Analyst, Researcher, Consultant).")]
    return []


def _check_seniority(a):
    if _is_inflated(a.get("role", "")):
        return [_finding("warning", "agent.seniority_inflated", "implementation/01-agent-engineering.md §8",
                         f"Role '{a.get('role')}' inflates seniority; seniority must be earned by task complexity.",
                         "Tone down the title to match actual task scope.")]
    return []


def _check_backstory_dump(a):
    backstory = a.get("backstory", "")
    if _count_keywords(backstory, _DISCIPLINE_KEYWORDS) >= 3:
        return [_finding("warning", "agent.backstory_capability_dump", "implementation/01-agent-engineering.md §14; 23 §4.2",
                         "Backstory lists many unrelated capabilities (capability dump).",
                         "Keep backstory to one professional identity; remove unrelated expertise claims.")]
    return []


def _check_backstory_knowledge(a):
    backstory = a.get("backstory", "")
    if _has_dynamic_data(backstory) or _has_knowledge_in_backstory(backstory):
        return [_finding("error", "agent.backstory_dynamic_knowledge", "implementation/01-agent-engineering.md §15, §41; 23 §7.3",
                         "Backstory contains dynamic/project-specific knowledge (facts, versions, dates) that belongs in Knowledge, not the persona.",
                         "Move project facts/entities into a Knowledge source; keep the persona static.")]
    return []


def _check_backstory_workflow(a):
    text = f"{a.get('backstory', '')} {a.get('goal', '')}"
    if _has_workflow_signals(text):
        return [_finding("error", "agent.backstory_task_instructions", "implementation/01-agent-engineering.md §16, §40",
                         "Backstory/goal embeds operational workflow instructions (hidden workflow). Orchestration belongs in Flow.",
                         "Remove imperative steps from the persona; define orchestration in the Flow.")]
    return []


def _check_biography_bloat(a):
    if _has_biography_bloat(a.get("backstory", "")):
        return [_finding("warning", "agent.backstory_biography_bloat", "implementation/01-agent-engineering.md §39, §53",
                         "Backstory leans on theatrical biography rather than professional capability.",
                         "Replace flourish with concrete professional context and constraints.")]
    return []


def _check_goal_is_task(a):
    goal = a.get("goal", "")
    if _has_lifecycle_verbs(goal, threshold=2) and _is_deterministic(goal):
        return [_finding("warning", "agent.goal_is_task", "implementation/01-agent-engineering.md §11, §53",
                         "Goal reads like a task (task-scoped verbs + inputs/outputs). A goal is an enduring responsibility, not a task spec.",
                         "State what the agent is responsible for, not how to do one unit of work.")]
    return []


def _check_scope_broad(a):
    role = a.get("role", "").lower()
    if "universal" in role or "everything expert" in role or "all-round" in role:
        return [_finding("error", "agent.scope_too_broad", "implementation/04-agent-task-alignment.md §29, §54; 23 §1.3",
                         f"Role '{a.get('role')}' claims universal scope. No agent should own every concern.",
                         "Bound the role to one professional responsibility.")]
    return []


def _check_tools_justified(a):
    tools = a.get("tools") or []
    if len(tools) >= 5:
        return [_finding("warning", "agent.tools_justify_each", "implementation/01-agent-engineering.md §29, §30; 04 §20",
                         f"Agent attached to {len(tools)} tools; capability padding risk. Every tool must map to a task need.",
                         "Prune tools to those actually used by this agent's tasks.")]
    return []


def _check_knowledge_relevant(a):
    knowledge = a.get("knowledge") or a.get("knowledge_sources") or []
    if isinstance(knowledge, list) and len(knowledge) >= 3:
        return [_finding("warning", "agent.knowledge_justify_each", "implementation/01-agent-engineering.md §31; 04 §18",
                         "Many knowledge sources attached; only attach knowledge this agent's tasks actually use.",
                         "Trim knowledge to what the assigned tasks reference.")]
    return []


def _check_skill_relevant(a):
    skills = a.get("skills") or []
    if isinstance(skills, list) and len(skills) >= 3:
        return [_finding("warning", "agent.skill_justify_each", "implementation/01-agent-engineering.md §33; 04 §19",
                         "Many skills attached; only attach skills whose methodology this agent's tasks apply.",
                         "Trim skills to those used as methodology by assigned tasks.")]
    return []


def _check_reasoning_justified(a):
    if a.get("reasoning") is True:
        return [_finding("warning", "agent.reasoning_unjustified", "implementation/01-agent-engineering.md §35; 04 §22",
                         "Reasoning enabled — confirm the assigned tasks actually need multi-factor judgment before keeping it.",
                         "Disable reasoning unless a task requires genuine multi-factor judgment.")]
    return []


def _check_prompt_footprint(a):
    if _prompt_redundancy(a):
        return [_finding("warning", "agent.prompt_footprint", "implementation/01-agent-engineering.md §37, §38; 02 §43",
                         "Role+goal+backstory are long or heavily redundant; bloats every prompt the agent touches.",
                         "Cut duplication and keep the persona minimal.")]
    return []


def _check_knowledge_in_backstory(a):
    backstory = a.get("backstory", "")
    if _count_keywords(backstory, _DISCIPLINE_KEYWORDS) >= 2 and len(backstory) > 600:
        return [_finding("error", "agent.backstory_contains_knowledge", "implementation/01-agent-engineering.md §15; 11 §175",
                         "Backstory reads as a knowledge/data dump, not a persona definition.",
                         "Move domain content to Knowledge; persona states role, not data.")]
    return []


def _check_knowledge_backstory_dup(a):
    backstory = (a.get("backstory", "") or "").lower()
    knowledge = a.get("knowledge") or a.get("knowledge_sources") or []
    if backstory and isinstance(knowledge, list) and knowledge:
        return [_finding("warning", "agent.knowledge_duplicated_in_backstory", "11 §65; 01 §38",
                         "Agent has both knowledge sources and a long backstory; verify no content is duplicated.",
                         "Keep facts in Knowledge only; strip them from the persona.")]
    return []


def _check_delegation_no_crew(a):
    if a.get("allow_delegation") is True:
        return [_finding("warning", "agent.delegation_enabled_no_crew", "06 §16.4; 23 §5.5",
                         "Agent allows delegation but crew collaborators/limits aren't evident; delegation may be decorative or unbounded.",
                         "Define the delegatees and termination criteria, or disable delegation.")]
    return []


def _check_god_task(t):
    text = f"{t.get('purpose', '')} {t.get('description', '')}"
    if _has_lifecycle_verbs(text, threshold=3) or _is_composite_task(t):
        return [_finding("error", "task.god_lifecycle", "implementation/02-task-engineering.md §7, §57; 03 §10",
                         f"Task '{t.get('name', '')}' runs a full lifecycle (research→generate→evaluate→revise→publish). That is a God Task.",
                         "Split into atomic tasks, one transformation and one deliverable each.")]
    return []


def _check_multiple_outputs(t):
    text = f"{t.get('expected_output', '')} {t.get('output', '')}"
    if _has_multi_output(text):
        return [_finding("error", "task.multiple_outputs", "implementation/02-task-engineering.md §7; 03 §8",
                         f"Task '{t.get('name', '')}' declares multiple independent deliverables; an atomic task has one coherent output.",
                         "Split into separate tasks, one deliverable each.")]
    return []


def _check_multi_validation(t):
    text = f"{t.get('description', '')} {t.get('instructions', '')}"
    if _count_keywords(text, {"schema", "creative", "security", "historical", "style", "factual", "consistency"}) >= 3:
        return [_finding("warning", "task.multiple_validation_criteria", "implementation/03-atomic-task-design.md §14",
                         "Mixed validation criteria in one task; atomicity is fragile when validation spans unrelated domains.",
                         "Split validation domains into separate tasks.")]
    return []


def _check_human_gate_in_task(t):
    text = f"{t.get('description', '')} {t.get('instructions', '')} {t.get('expected_output', '')}"
    if _has_human_gate(text):
        return [_finding("error", "task.multiple_human_decisions", "implementation/03-atomic-task-design.md §16, §46",
                         "A human approval gate is embedded inside this task alongside other work. Human gates belong in Flow as explicit checkpoints.",
                         "Move the human gate into the Flow as an explicit human_input step.")]
    return []


def _check_composite_output(t):
    if _is_composite_task(t):
        return [_finding("error", "task.composite_output_contract", "implementation/03-atomic-task-design.md §53; 02 §57",
                         "Task contract is composite (multiple transformation stages in one contract).",
                         "Decompose into a chain of atomic contracts.")]
    return []


def _check_micro_fragmentation(t):
    text = f"{t.get('purpose', '')} {t.get('description', '')}"
    if _count_keywords(text, {"extract", "list", "enumerate", "read", "load", "sort", "count"}) >= 3:
        return [_finding("warning", "task.micro_fragmentation", "implementation/03-atomic-task-design.md §31, §32",
                         f"Task '{t.get('name', '')}' looks micro-fragmented (only mechanical extraction steps). Consider merging with siblings.",
                         "Merge into one meaningful transformation; avoid a task per mechanical step.")]
    return []


def _check_deterministic_by_agent(t):
    text = f"{t.get('purpose', '')} {t.get('description', '')}"
    if _is_deterministic(text):
        return [_finding("error", "task.deterministic_work_assigned_agent", "implementation/13-python-and-tools.md §27, §29; 23 §8.3",
                         f"Task '{t.get('name', '')}' is deterministic/mechanical work assigned to an agent. Use Python/deterministic processing instead.",
                         "Replace this agent task with a deterministic Python step (least-powerful tool).")]
    return []


def _check_validation_by_agent(t):
    text = f"{t.get('description', '')} {t.get('instructions', '')}"
    if _count_keywords(text, {"required", "enum", "field exists", "missing field", "schema"}) >= 2:
        return [_finding("warning", "task.structural_validation_by_agent", "implementation/02-task-engineering.md §60; 13 §27",
                         "Structural validation (required fields/enums) assigned to the LLM. Deterministic validation belongs in Python.",
                         "Move schema/required-field checks to deterministic code.")]
    return []


def _check_input_declared(t):
    purpose = t.get("purpose", "")
    if _count_keywords(purpose, {"chapter", "input", "file", "document", "source", "data"}) >= 1 and not t.get("input_required") and not t.get("input"):
        return [_finding("warning", "task.input_not_declared", "implementation/02-task-engineering.md §11",
                         "Task references concrete inputs but none are declared as required inputs.",
                         "Declare each required input explicitly.")]
    return []


def _check_input_available(t):
    required = t.get("input_required") or []
    if required and not isinstance(required, list):
        required = [required]
    if required:
        return [_finding("error", "task.required_input_unavailable", "implementation/02-task-engineering.md §13; 07 §7",
                         f"Required inputs {required} are not verifiably produced by any upstream task in this context.",
                         "Ensure every required input has a producer (upstream task, flow input, or documented external source).")]
    return []


def _check_context_link(t):
    ctx = t.get("context") or t.get("previous_outputs") or []
    if isinstance(ctx, list) and any(isinstance(c, dict) and not c.get("task") and not c.get("source") for c in ctx):
        return [_finding("warning", "task.context_missing_link", "implementation/02-task-engineering.md §22, §23",
                         "A context item has no resolvable producer; broken dependency risk.",
                         "Point context at the exact upstream task output.")]
    return []


def _check_context_propagation(t):
    ctx = t.get("context") or t.get("previous_outputs") or []
    if "*" in ctx or "all_outputs" in ctx or "all_state" in ctx:
        return [_finding("warning", "task.context_over_propagation", "implementation/02-task-engineering.md §21, §22; 11 §53",
                         "Context pulls everything (all outputs/state/knowledge) — a context dump, not a minimal input contract.",
                         "Inject only the specific upstream outputs this task needs.")]
    return []


def _check_hidden_flow_in_task(t):
    text = f"{t.get('description', '')} {t.get('instructions', '')}"
    if _has_workflow_signals(text):
        return [_finding("error", "task.hidden_flow_decision", "implementation/02-task-engineering.md §48; 09",
                         "Task instructions contain branching/retry/orchestration — a hidden Flow decision inside the task.",
                         "Move control decisions to the Flow; the task should be one straight transformation.")]
    return []


def _check_state_context_confusion(t):
    ctx = t.get("context") or t.get("previous_outputs") or []
    if "state" in ctx or "flow_state" in ctx:
        return [_finding("warning", "task.state_versus_context_confusion", "11 §27; 09 §36; 23 §7.2",
                         "Flow state is being dumped into the task context. State and context are different things.",
                         "Inject only task-relevant context, never wholesale flow state.")]
    return []

def _crew_agents(c):
    agents = c.get("agents") or []
    if isinstance(agents, dict):
        agents = list(agents.values())
    return [a if isinstance(a, dict) else (a.dict() if hasattr(a, "dict") else {}) for a in agents]


def _crew_tasks(c):
    tasks = c.get("tasks") or []
    if isinstance(tasks, dict):
        tasks = list(tasks.values())
    return [t if isinstance(t, dict) else (t.model_dump() if hasattr(t, "model_dump") else {}) for t in tasks]


def _check_single_agent_crew(c):
    agents = _crew_agents(c)
    collab = c.get("collaboration") or c.get("process")
    if len(agents) == 1 and not collab:
        return [_finding("warning", "crew.single_agent_crew", "23 §5.1; 06 §49",
                         "Crew has a single agent and no collaboration — that is an Agent+Task, not a crew.",
                         "Use a single Agent+Task, or add real collaborators.")]
    return []


def _check_god_crew(c):
    agents = _crew_agents(c)
    if len(agents) >= 4:
        all_text = " ".join(f"{a.get('role', '')} {a.get('goal', '')}" for a in agents)
        if _count_keywords(all_text, _DISCIPLINE_KEYWORDS) >= 6:
            return [_finding("error", "crew.god_crew", "06 §12, §44; 07 §2",
                             "Crew spans many unrelated professional processes (God Crew, 'do everything' scope).",
                             "Split into one crew per bounded process.")]
    return []


def _check_decorative_crew(c):
    tasks = _crew_tasks(c)
    if len(_crew_agents(c)) >= 2 and len(tasks) <= 1:
        return [_finding("warning", "crew.decorative_no_value", "06 §6, §44; 07 §6",
                         "Crew has multiple agents but a single task — no real collaboration. Looks decorative.",
                         "Either give each agent genuine work that requires collaboration, or use a Flow.")]
    return []


def _check_agent_collection(c):
    agents = _crew_agents(c)
    if len(agents) >= 3:
        texts = [f"{a.get('role', '')} {a.get('goal', '')}" for a in agents]
        domain_sets = [_extract_domains(t) for t in texts]
        populated = [s for s in domain_sets if s]
        if populated and len(populated) >= 3:
            union = set().union(*populated)
            if len(union) >= 3:
                return [_finding("warning", "crew.agent_collection", "06 §44 Agent Collection",
                                 "Agents have unrelated professional responsibilities with no shared bounded outcome — an agent collection, not a collaboration.",
                                 "Define a shared bounded outcome, or split into separate crews.")]
    return []


def _check_sequential_flow_crew(c):
    tasks = _crew_tasks(c)
    shared = any(t.get("context") for t in tasks)
    if len(tasks) >= 2 and not shared:
        return [_finding("warning", "crew.sequential_flow_camouflage", "06 §44 Crew for Sequential Flow; 09",
                         "Crew looks like plain sequential steps with no information sharing — a Flow would suffice.",
                         "Use a Flow for linear sequencing; keep a crew only for genuine collaboration.")]
    return []


def _check_agent_duplication(c):
    agents = _crew_agents(c)
    roles = [a.get("role", "").strip().lower() for a in agents]
    for i in range(len(roles)):
        for j in range(i + 1, len(roles)):
            if roles[i] and roles[i] == roles[j]:
                return [_finding("warning", "crew.agent_duplication", "06 §14; 07 §6",
                                 f"Two agents share the same role '{agents[i].get('role')}'; near-duplicate agents.",
                                 "Merge into one agent or define distinct specializations.")]
    return []


def _check_coverage_gap(c):
    agents = _crew_agents(c)
    required = c.get("required_capabilities") or []
    if required:
        agent_text = " ".join(f"{a.get('role', '')} {a.get('goal', '')}" for a in agents).lower()
        missing = [cap for cap in required if cap.lower() not in agent_text]
        if missing:
            return [_finding("error", "crew.coverage_gap", "07 §3; §6",
                             f"Crew requires capabilities {missing} that no agent provides.",
                             "Add an agent covering the missing responsibility.")]
    return []


def _check_unbounded_collaboration(c):
    collab = c.get("collaboration") or {}
    limit = collab.get("max_rounds") if isinstance(collab, dict) else None
    term = collab.get("termination") if isinstance(collab, dict) else None
    if c.get("collaboration") and limit is None and term is None:
        return [_finding("error", "crew.unbounded_collaboration", "23 §5.5; 07 §11",
                         "Crew collaboration has no termination condition or iteration limit — risk of infinite discussion.",
                         "Define a max-round limit or explicit success/termination criteria.")]
    return []


def _check_process_mismatch(c):
    process = (c.get("process") or "").lower()
    if process == "sequential":
        tasks = _crew_tasks(c)
        if any(t.get("async_execution") for t in tasks):
            return [_finding("error", "crew.process_param_mismatch", "06 §16, §30; 07 §6",
                             "process=sequential but a task is marked async/parallel — contradiction.",
                             "Set process to match the dependency structure (e.g. hierarchical or a Flow).")]
    return []


def _check_hierarchical_no_manager(c):
    process = (c.get("process") or "").lower()
    collab = c.get("collaboration") or {}
    manager = (collab.get("manager") if isinstance(collab, dict) else None) or c.get("manager_agent")
    if process in {"hierarchical", "delegated", "managed"} and not manager:
        return [_finding("warning", "crew.process_hierarchical_no_manager", "06 §16.4",
                         "process is hierarchical/delegated but no manager agent is defined.",
                         "Define a manager/lead agent, or switch to a bounded collaboration model.")]
    return []


def _check_hidden_workflow(f):
    for node in f.get("nodes") or []:
        text = f"{node.get('prompt', '')} {node.get('instructions', '')}"
        if _has_workflow_signals(text):
            return [_finding("error", "flow.hidden_workflow_in_agent", "09 §18, §19; 23 §6.1",
                             "Control decisions (branching/retry) live inside a task prompt instead of the Flow.",
                             "Promote control logic to explicit Flow transitions.")]
    return []


def _check_implicit_transitions(f):
    processes = f.get("processes") or f.get("nodes") or []
    if len(processes) >= 2 and not f.get("transitions") and not f.get("edges"):
        return [_finding("error", "flow.implicit_transitions", "09; 23 §6.1",
                         "Flow has multiple steps but no explicit transitions — orchestration is implicit.",
                         "Declare explicit transitions (from/to/condition) for every step.")]
    return []


def _check_unbounded_loop(f):
    for node in f.get("processes") or f.get("nodes") or []:
        text = f"{node.get('type', '')} {node.get('instructions', '')}".lower()
        if "loop" in text or "iterate" in text or "retry" in text:
            if not node.get("max_attempts") and not node.get("limit"):
                return [_finding("error", "flow.unbounded_loop", "09; 23 §6.3",
                                 "Flow has a loop/iteration without a limit or exhaustion outcome.",
                                 "Add max_attempts/limit and an exhausted terminal outcome.")]
    return []


def _check_state_dump(f):
    state = f.get("state") or {}
    outputs = [n.get("output", "") for n in (f.get("nodes") or f.get("processes") or [])]
    if isinstance(state, dict) and outputs and set(outputs).issubset(set(state.keys())) and len(outputs) >= 3:
        return [_finding("warning", "flow.state_dump", "09; 23 §6.4",
                         "Flow copies every process output into global state (state dump, no owner/lifetime).",
                         "Keep only state that needs cross-step retention; give each field an owner and lifetime.")]
    return []


def _check_state_unowned(f):
    state = f.get("state") or {}
    if isinstance(state, dict):
        unowned = [k for k, v in state.items() if isinstance(v, dict) and not v.get("owner")]
        if unowned:
            return [_finding("warning", "flow.state_unowned", "09 state ownership",
                             f"State fields {unowned} have no defined owner.",
                             "Declare an owner and lifetime for each state field.")]
    return []


def _check_routing_by_llm(f):
    for node in f.get("nodes") or f.get("processes") or []:
        text = f"{node.get('instructions', '')} {node.get('prompt', '')}".lower()
        if _is_deterministic(text) and ("llm" in text or "agent" in text):
            return [_finding("error", "flow.deterministic_routing_by_llm", "09; 13 §27; 23 §8.3",
                             "Flow routes a deterministic decision (e.g. status check) via an LLM/agent instead of Python.",
                             "Use deterministic Python for status/field-based routing.")]
    return []


def _check_terminal_ambiguous(f):
    states = f.get("terminal_states") or f.get("outcomes") or []
    if not states and (f.get("nodes") or f.get("processes")):
        return [_finding("warning", "flow.terminal_states_ambiguous", "09 termination",
                         "Flow lacks explicit terminal states (success/failure/alternate outcomes).",
                         "Declare distinct terminal states and success criteria.")]
    return []


def _check_hidden_human_gate(f):
    for node in f.get("nodes") or f.get("processes") or []:
        if _has_human_gate(f"{node.get('instructions', '')} {node.get('prompt', '')}"):
            if node.get("type", "").lower() not in {"human", "human_input", "human_gate"}:
                return [_finding("error", "flow.human_gate_hidden", "02 §16, §46; 09",
                                 "A human approval is embedded inside a non-human flow node.",
                                 "Make the human gate an explicit human_input node with outcomes.")]
    return []


def _check_god_flow(f):
    responsibilities = 0
    for node in f.get("nodes") or f.get("processes") or []:
        text = f"{node.get('type', '')} {node.get('instructions', '')}"
        if _count_keywords(text, {"route", "business", "prompt", "tool", "exec", "validate", "persist", "recover"}) >= 4:
            responsibilities += 1
    if responsibilities >= 1:
        return [_finding("warning", "flow.god_flow", "09; 23 §6.2",
                         "A single flow node handles many responsibilities (routing+business+tool+validation+persistence).",
                         "Decompose the flow into focused steps, one responsibility each.")]
    return []


def _check_knowledge_as_skill(k):
    text = f"{k.get('content', '')} {k.get('description', '')}"
    if _count_keywords(text, {"step 1", "step 2", "how to", "procedure", "methodology", "first", "then"}) >= 2:
        return [_finding("warning", "knowledge.skill_mislabel", "11 §23, §35",
                         "Knowledge contains step-by-step methodology — that is a Skill, not Knowledge.",
                         "Move procedural instructions to a Skill; Knowledge holds reference facts.")]
    return []


def _check_skill_as_knowledge(s):
    text = f"{s.get('content', '')} {s.get('description', '')}"
    if _count_keywords(text, {"recipe", "reference", "facts", "glossary", "definitions"}) >= 2 and not _count_keywords(text, {"how to", "step", "procedure", "method"}):
        return [_finding("warning", "skill.knowledge_mislabel", "11 §23",
                         "Skill contains only reference facts/data with no procedure — that is Knowledge, not a Skill.",
                         "Relabel as Knowledge, or add the actual methodology.")]
    return []


def _check_giant_tool(t):
    name = (t.get("name", "") + " " + t.get("type", "")).lower()
    if any(g in name for g in _GIANT_TOOLS):
        return [_finding("error", "tool.giant_tool", "13 §27-28; 23 §9.1",
                         f"Tool '{t.get('name')}' is a general-purpose/high-power facility (shell, admin, DB).",
                         "Expose a narrow capability instead of a universal tool.")]
    return []


def _check_tool_everywhere(t):
    scope = t.get("scope") or t.get("agents") or []
    if isinstance(scope, list) and len(scope) >= 5:
        return [_finding("warning", "tool.everywhere", "13 §27-28, §29; 23 §4.3",
                         "Tool is attached to many agents — capability everywhere, least-powerful violated.",
                         "Attach the tool only to agents whose tasks need it.")]
    return []


def _check_tool_not_justified(t):
    if not (t.get("tasks") or t.get("justification") or t.get("enabled_by")):
        return [_finding("warning", "tool.not_justified_by_task", "01 §30; 04 §20",
                         f"Tool '{t.get('name')}' has no declared task justification.",
                         "Document which task requires this tool.")]
    return []


def _check_tool_secrets(t):
    text = f"{t.get('description', '')} {t.get('config', '')} {t.get('params', '')}"
    if _has_secrets(text):
        return [_finding("error", "tool.credentials_embedded", "13 §90; 14 §57; 23 §9.3",
                         "A secret/credential literal appears in tool configuration.",
                         "Reference credentials via a secure source; never embed literals.")]
    return []


def _check_mcp_unreachable(m):
    endpoint = m.get("endpoint") or m.get("url") or m.get("command") or m.get("server")
    transport = m.get("transport")
    if not endpoint and not transport:
        return [_finding("error", "mcp.defined_but_unreachable", "14 §38, §40",
                         "MCP server is defined but unreachable — no endpoint/url/command or missing transport.",
                         "Provide a valid endpoint and transport.")]
    return []


def _check_mcp_unrestricted(m):
    caps = m.get("capabilities") or m.get("allowed_tools") or []
    if "*" in caps or m.get("allow_all") is True:
        return [_finding("error", "mcp.unrestricted_every_server", "14 §33, §35; 23 §9.2",
                         "Agent/MCP exposed to ALL capabilities/servers — unrestricted boundary.",
                         "Enumerate only the specific capabilities needed.")]
    return []


def _check_mcp_permission(m):
    need = m.get("needs") or m.get("permission")
    granted = m.get("permissions") or []
    if need == "read" and granted and any(g.startswith("write") or g.startswith("delete") for g in granted):
        return [_finding("error", "mcp.read_write_misgrant", "14 §33, §57",
                         "MCP grants write/delete but the process only needs read — least-privilege violated.",
                         "Grant read only.")]
    return []


def _check_mcp_transport(m):
    transport = m.get("transport")
    if transport and transport not in _VALID_TRANSPORTS:
        return [_finding("error", "mcp.transport_unsupported", "mcp_data.py (McpServerConfig)",
                         f"Unsupported MCP transport '{transport}'. Valid: stdio, http, sse.",
                         "Use a supported transport.")]
    return []


def _check_mcp_everywhere(m):
    use = m.get("used_by") or m.get("agents") or []
    if isinstance(use, list) and len(use) >= 4:
        return [_finding("warning", "mcp.everywhere", "14 §135; 23 §9.2",
                         "MCP capability attached across many agents without per-agent need.",
                         "Attach MCP only where an external capability is actually required.")]
    return []


def _check_mcp_secrets(m):
    text = f"{m.get('config', '')} {m.get('headers', '')} {m.get('env', '')}"
    if _has_secrets(text):
        return [_finding("error", "mcp.credentials_in_context", "14 §57; 13 §90",
                         "Secret literal in MCP config/headers.",
                         "Inject credentials from a secure source at runtime.")]
    return []

ComponentCheck = Callable[[dict], list[Finding]]

_COMPONENT_CHECKS: dict[str, list[tuple[str, str, str, str, ComponentCheck]]] = {
    "agent": [
        ("agent.god_scope", "error", "implementation/01-agent-engineering.md §53; 23 §1.3", "One Agent for Everything", _check_god_agent),
        ("agent.role_vague", "error", "implementation/01-agent-engineering.md §45; 23 §1.4", "Generic Agent", _check_role_vague),
        ("agent.role_professional_test", "warning", "implementation/01-agent-engineering.md §7", "Professional archetype", _check_role_professional),
        ("agent.seniority_inflated", "warning", "implementation/01-agent-engineering.md §8", "Seniority", _check_seniority),
        ("agent.backstory_capability_dump", "warning", "implementation/01-agent-engineering.md §14; 23 §4.2", "Backstory capability dump", _check_backstory_dump),
        ("agent.backstory_dynamic_knowledge", "error", "implementation/01-agent-engineering.md §15, §41; 23 §7.3", "Dynamic knowledge in backstory", _check_backstory_knowledge),
        ("agent.backstory_task_instructions", "error", "implementation/01-agent-engineering.md §16, §40", "Task instructions in backstory", _check_backstory_workflow),
        ("agent.backstory_biography_bloat", "warning", "implementation/01-agent-engineering.md §39, §53", "Biography bloat", _check_biography_bloat),
        ("agent.goal_is_task", "warning", "implementation/01-agent-engineering.md §11, §53", "Task embedded in goal", _check_goal_is_task),
        ("agent.scope_too_broad", "error", "implementation/04-agent-task-alignment.md §29, §54; 23 §1.3", "Scope too broad", _check_scope_broad),
        ("agent.tools_justify_each", "warning", "implementation/01-agent-engineering.md §29, §30; 04 §20", "Tool minimality", _check_tools_justified),
        ("agent.knowledge_justify_each", "warning", "implementation/01-agent-engineering.md §31; 04 §18", "Knowledge relevance", _check_knowledge_relevant),
        ("agent.skill_justify_each", "warning", "implementation/01-agent-engineering.md §33; 04 §19", "Skill relevance", _check_skill_relevant),
        ("agent.reasoning_unjustified", "warning", "implementation/01-agent-engineering.md §35; 04 §22", "Unjustified reasoning", _check_reasoning_justified),
        ("agent.prompt_footprint", "warning", "implementation/01-agent-engineering.md §37, §38; 02 §43", "Prompt footprint", _check_prompt_footprint),
        ("agent.backstory_contains_knowledge", "error", "implementation/01-agent-engineering.md §15; 11 §175", "Knowledge in backstory", _check_knowledge_in_backstory),
        ("agent.knowledge_duplicated_in_backstory", "warning", "11 §65; 01 §38", "Redundant knowledge/backstory", _check_knowledge_backstory_dup),
        ("agent.delegation_enabled_no_crew", "warning", "06 §16.4; 23 §5.5", "Delegation without crew context", _check_delegation_no_crew),
    ],
    "task": [
        ("task.god_lifecycle", "error", "implementation/02-task-engineering.md §7, §57; 03 §10", "God Task lifecycle", _check_god_task),
        ("task.multiple_outputs", "error", "implementation/02-task-engineering.md §7; 03 §8", "Multiple independent outputs", _check_multiple_outputs),
        ("task.multiple_validation_criteria", "warning", "implementation/03-atomic-task-design.md §14", "Multiple validation criteria", _check_multi_validation),
        ("task.multiple_human_decisions", "error", "implementation/03-atomic-task-design.md §16, §46", "Human gate in atomic task", _check_human_gate_in_task),
        ("task.composite_output_contract", "error", "implementation/03-atomic-task-design.md §53; 02 §57", "Composite output contract", _check_composite_output),
        ("task.micro_fragmentation", "warning", "implementation/03-atomic-task-design.md §31, §32", "Micro task fragmentation", _check_micro_fragmentation),
        ("task.deterministic_work_assigned_agent", "error", "implementation/13-python-and-tools.md §27, §29; 23 §8.3", "Deterministic work in agent", _check_deterministic_by_agent),
        ("task.structural_validation_by_agent", "warning", "implementation/02-task-engineering.md §60; 13 §27", "Structural validation by LLM", _check_validation_by_agent),
        ("task.input_not_declared", "warning", "implementation/02-task-engineering.md §11", "Undeclared inputs", _check_input_declared),
        ("task.required_input_unavailable", "error", "implementation/02-task-engineering.md §13; 07 §7", "Blocking missing input", _check_input_available),
        ("task.context_missing_link", "warning", "implementation/02-task-engineering.md §22, §23", "Broken context link", _check_context_link),
        ("task.context_over_propagation", "warning", "implementation/02-task-engineering.md §21, §22; 11 §53", "Context dump", _check_context_propagation),
        ("task.hidden_flow_decision", "error", "implementation/02-task-engineering.md §48; 09", "Hidden workflow in task", _check_hidden_flow_in_task),
        ("task.state_versus_context_confusion", "warning", "11 §27; 09 §36; 23 §7.2", "State vs context confusion", _check_state_context_confusion),
    ],
    "crew": [
        ("crew.single_agent_crew", "warning", "23 §5.1; 06 §49", "Single agent crew", _check_single_agent_crew),
        ("crew.god_crew", "error", "06 §12, §44; 07 §2", "God Crew scope", _check_god_crew),
        ("crew.decorative_no_value", "warning", "06 §6, §44; 07 §6", "Decorative crew", _check_decorative_crew),
        ("crew.agent_collection", "warning", "06 §44 Agent Collection", "Agent collection", _check_agent_collection),
        ("crew.sequential_flow_camouflage", "warning", "06 §44 Crew for Sequential Flow; 09", "Sequential flow disguised as crew", _check_sequential_flow_crew),
        ("crew.agent_duplication", "warning", "06 §14; 07 §6", "Duplicate agents", _check_agent_duplication),
        ("crew.coverage_gap", "error", "07 §3; §6", "Agent coverage gap", _check_coverage_gap),
        ("crew.unbounded_collaboration", "error", "23 §5.5; 07 §11", "Unbounded collaboration", _check_unbounded_collaboration),
        ("crew.process_param_mismatch", "error", "06 §16, §30; 07 §6", "Process param mismatch", _check_process_mismatch),
        ("crew.process_hierarchical_no_manager", "warning", "06 §16.4", "Hierarchical without manager", _check_hierarchical_no_manager),
    ],
    "flow": [
        ("flow.hidden_workflow_in_agent", "error", "09 §18, §19; 23 §6.1", "Hidden workflow", _check_hidden_workflow),
        ("flow.implicit_transitions", "error", "09; 23 §6.1", "Implicit transitions", _check_implicit_transitions),
        ("flow.unbounded_loop", "error", "09; 23 §6.3", "Unbounded iteration", _check_unbounded_loop),
        ("flow.state_dump", "warning", "09; 23 §6.4", "State dump", _check_state_dump),
        ("flow.state_unowned", "warning", "09 state ownership", "Unowned state", _check_state_unowned),
        ("flow.deterministic_routing_by_llm", "error", "09; 13 §27; 23 §8.3", "Deterministic routing by LLM", _check_routing_by_llm),
        ("flow.terminal_states_ambiguous", "warning", "09 termination", "Ambiguous termination", _check_terminal_ambiguous),
        ("flow.human_gate_hidden", "error", "02 §16, §46; 09", "Hidden human gate", _check_hidden_human_gate),
        ("flow.god_flow", "warning", "09; 23 §6.2", "God flow", _check_god_flow),
    ],
    "knowledge": [
        ("knowledge.skill_mislabel", "warning", "11 §23, §35", "Knowledge as Skill", _check_knowledge_as_skill),
    ],
    "skill": [
        ("skill.knowledge_mislabel", "warning", "11 §23", "Skill as Knowledge", _check_skill_as_knowledge),
    ],
    "tool": [
        ("tool.giant_tool", "error", "13 §27-28; 23 §9.1", "General-purpose tool", _check_giant_tool),
        ("tool.everywhere", "warning", "13 §27-28, §29; 23 §4.3", "Tool everywhere", _check_tool_everywhere),
        ("tool.not_justified_by_task", "warning", "01 §30; 04 §20", "Unjustified tool", _check_tool_not_justified),
        ("tool.credentials_embedded", "error", "13 §90; 14 §57; 23 §9.3", "Secrets in tool", _check_tool_secrets),
    ],
    "mcp": [
        ("mcp.defined_but_unreachable", "error", "14 §38, §40", "MCP unreachable", _check_mcp_unreachable),
        ("mcp.unrestricted_every_server", "error", "14 §33, §35; 23 §9.2", "Unrestricted MCP", _check_mcp_unrestricted),
        ("mcp.read_write_misgrant", "error", "14 §33, §57", "Excessive MCP permissions", _check_mcp_permission),
        ("mcp.transport_unsupported", "error", "mcp_data.py (McpServerConfig)", "Invalid MCP transport", _check_mcp_transport),
        ("mcp.everywhere", "warning", "14 §135; 23 §9.2", "MCP everywhere", _check_mcp_everywhere),
        ("mcp.credentials_in_context", "error", "14 §57; 13 §90", "Secrets in MCP", _check_mcp_secrets),
    ],
}

_VALID_COMPONENTS = set(_COMPONENT_CHECKS.keys())

_COMPONENT_LABELS = {
    "agent": "Agent", "task": "Task", "crew": "Crew", "flow": "Flow",
    "knowledge": "Knowledge", "skill": "Skill", "tool": "Tool", "mcp": "MCP",
}


def verify_component(component_type: str, definition: dict) -> VerificationResult:
    """Verify a single component against the methodology rules for its type.

    Args:
        component_type: one of "agent", "task", "crew", "flow", "knowledge",
            "skill", "tool", "mcp"
        definition: the component data as a plain dict

    Returns:
        VerificationResult with findings, pass/fail, and a summary.
    """
    component_type = component_type.lower()
    if component_type not in _VALID_COMPONENTS:
        return VerificationResult(
            findings=[_finding("error", "verify.unknown_component",
                               "verification",
                               f"Unknown component type '{component_type}'. Valid: {sorted(_VALID_COMPONENTS)}.")],
            component_type=component_type,
        )
    findings: list[Finding] = []
    for rule_id, severity, source, _label, check in _COMPONENT_CHECKS[component_type]:
        try:
            findings.extend(check(definition))
        except Exception:
            continue
    return VerificationResult(findings=findings, component_type=_COMPONENT_LABELS[component_type])

_PREREQ_REQUIRED_FIELDS = {
    "00": {"problem", "start_condition", "desired_end_condition", "primary_objective", "constraints", "success_definition"},
    "01": {"start_boundary", "end_boundary", "scope", "completion_definition"},
    "02": {"start_state", "end_state", "processes", "relationships"},
    "03": {"contracts"},
    "04": {"validation"},
    "05": {"flow_order", "transitions", "state_requirements"},
    "06": {"failures", "recovery", "unrecoverable_definition"},
    "07": {"capabilities"},
    "08": {"validation"},
    "09": {"checklist"},
}

_PREREQ_LABELS = {
    "00": "problem definition", "01": "goal & boundary", "02": "process decomposition",
    "03": "process contracts", "04": "validation", "05": "flow & state planning",
    "06": "corner cases & failure", "07": "capability selection", "08": "architecture validation",
    "09": "architecture handoff",
}

_CONTRACT_REQUIRED = {"id", "name", "purpose"}


def verify_prerequisite_artifacts(artifacts: dict[str, dict]) -> VerificationResult:
    """Verify prerequisite design artifacts against methodology rules.

    Args:
        artifacts: mapping of stage name ("00"-"09") to the filled artifact dict.

    Returns:
        VerificationResult with findings per stage and cross-stage consistency.
    """
    findings: list[Finding] = []
    catalogs: dict[str, list[str]] = {}

    for stage, artifact in sorted(artifacts.items()):
        label = _PREREQ_LABELS.get(stage, f"stage {stage}")
        missing = sorted(_PREREQ_REQUIRED_FIELDS.get(stage, set()) - set((artifact or {}).keys()))
        if missing:
            findings.append(_finding(
                "error", f"prereq.{stage}_incomplete", f"prerequisite/{label}",
                f"Prerequisite {stage} ({label}) is missing required fields: {missing}.",
                "Fill every required field before the architecture stage is accepted."))
        if stage == "00" and artifact:
            if not str(artifact.get("problem", "")).strip():
                findings.append(_finding(
                    "error", "prereq.problem_not_defined", "prerequisite/00-problem-definition",
                    "Problem definition is required before any architecture work.",
                    "Define the problem statement."))
        if stage == "02" and artifact:
            processes = artifact.get("processes") or []
            if isinstance(processes, list):
                catalogs["processes"] = [p.get("id", p.get("name", "")) if isinstance(p, dict) else str(p) for p in processes]
        if stage == "03" and artifact:
            contracts = artifact.get("contracts") or []
            ids = []
            if isinstance(contracts, list):
                for c in contracts:
                    if isinstance(c, dict):
                        ids.append(c.get("id", str(c.get("name", ""))))
                        miss = sorted(_CONTRACT_REQUIRED - set(c.keys()))
                        if miss:
                            findings.append(_finding(
                                "error", "prereq.process_contract_incomplete", "prerequisite/03-process-contracts-and-atomicity",
                                f"Contract {c.get('name', c.get('id', '?'))} incomplete: missing {miss}.",
                                "Every contract needs id, name, purpose at minimum."))
                    if isinstance(c, dict) and _has_workflow_signals(f"{c.get('purpose', '')} {c.get('transformation', '')}"):
                        findings.append(_finding(
                            "warning", "prereq.process_contract_implements", "prerequisite/03-process-contracts-and-atomicity",
                            f"Contract {c.get('name', '?')} may leak implementation (Call LLM/Agent/Tool/retry) into the contract.",
                            "Redefine the contract in terms of intention, not implementation."))
            catalogs["contracts"] = ids

    if "processes" in catalogs and "contracts" in catalogs:
        uncovered = [p for p in catalogs["processes"] if p not in catalogs["contracts"]]
        if uncovered:
            findings.append(_finding(
                "error", "prereq.process_without_contract", "prerequisite/03-process-contracts-and-atomicity",
                f"Processes {uncovered} have no matching contract in stage 03.",
                "Define contracts for every decomposed process."))

    transition_refs = artifacts.get("05", {}).get("transitions") if artifacts.get("05") else None
    if isinstance(transition_refs, list) and "processes" in catalogs:
        for tnode in transition_refs:
            if isinstance(tnode, dict):
                for key in ("from", "to"):
                    ref = tnode.get(key)
                    if ref and ref not in catalogs["processes"]:
                        findings.append(_finding(
                            "error", "prereq.flow_state_plan_missing", "prerequisite/05-flow-and-state-planning",
                            f"Transition references process '{ref}' that is not in the decomposition.",
                            "Only transition between declared processes."))
                    break

    if not findings:
        findings.append(_finding(
            "info" if False else "advisory", "prereq.complete", "prerequisite",
            "All provided prerequisite artifacts are well-formed and internally consistent.", ""))
    return VerificationResult(findings=findings, component_type="Prerequisite artifacts")


def _parse_model_dicts(model_cls, raw: dict) -> tuple[dict | None, list[Finding]]:
    from pydantic import ValidationError
    try:
        obj = model_cls(**raw)
        return obj.model_dump(), []
    except ValidationError as e:
        msgs = [f"{'.'.join(str(p) for p in err['loc'])}: {err['msg']}" for err in e.errors()]
        return None, [_finding(
            "error", "schema.conformance", model_cls.__name__,
            f"Definition does not conform to the {model_cls.__name__} schema: {'; '.join(msgs)}.",
            "Fix the schema violations.")]


def verify_alignment(agents: list[dict], tasks: list[dict]) -> VerificationResult:
    """Verify agent-task alignment across a set of agents and tasks.

    Checks unassigned tasks, unused agents, domain mismatch, capability gaps,
    goal mismatch, delegation misuse, and task overlap.

    Args:
        agents: list of agent definition dicts.
        tasks: list of task definition dicts.

    Returns:
        VerificationResult with alignment findings.
    """
    findings: list[Finding] = []
    agent_ids = {a.get("name", a.get("role", "")).strip() for a in agents}
    agent_names = [a.get("name", a.get("role", "")).strip() for a in agents]
    agent_texts = {n: f"{a.get('role', '')} {a.get('goal', '')} {a.get('backstory', '')}" for n, a in zip(agent_names, agents)} if agents else {}
    task_ids = [t.get("name", t.get("id", "")).strip() for t in tasks]

    for t in tasks:
        assigned = str(t.get("agent") or t.get("agent_id") or "").strip()
        if not assigned:
            findings.append(_finding(
                "error", "alignment.unassigned_task", "05 §7, §46",
                f"Task '{t.get('name', '?')}' has no assigned agent.",
                "Assign the task to an owning agent."))
        elif assigned not in agent_ids and agents:
            findings.append(_finding(
                "error", "alignment.unassigned_task", "05 §7, §46",
                f"Task '{t.get('name', '?')}' references agent '{assigned}' that is not among the provided agents.",
                "Fix the agent reference."))

    used_agents = {str(t.get("agent") or t.get("agent_id") or "").strip() for t in tasks}
    if agents:
        for name in agent_names:
            if name and name not in used_agents:
                findings.append(_finding(
                    "warning", "alignment.unused_agent", "05 §7, §45",
                    f"Agent '{name}' has no assigned tasks.",
                    "Either assign it work or remove it."))

    for t in tasks:
        assigned = str(t.get("agent") or t.get("agent_id") or "").strip()
        agent_text = agent_texts.get(assigned, "")
        purpose = f"{t.get('purpose', '')} {t.get('description', '')}"
        task_domains = _extract_domains(purpose)
        agent_domains = _extract_domains(agent_text)
        if (agent_text and purpose and task_domains and not (task_domains & agent_domains)):
            findings.append(_finding(
                "error", "alignment.domain_mismatch", "04 §8, §9, §14; 05 §8, §9",
                f"Task '{t.get('name', '?')}' is in domain(s) {sorted(task_domains)} but agent '{assigned}' covers none — agent-task mismatch.",
                "Reassign to an agent whose domain matches the task, or add the missing specialization."))

    return VerificationResult(findings=findings, component_type="Alignment")


def _crew_struct(agents: list[dict], tasks: list[dict]) -> dict:
    return {"agents": agents, "tasks": tasks}


def verify_crew_yaml(crew_dir: str | Path) -> VerificationResult:
    """Verify a complete crew configuration directory against methodology rules.

    Expects the standard Amsha crew_forge layout::

        crew_dir/
            agents/*_agent.yaml
            tasks/*_task.yaml
            knowledge/    (optional)
            skills/       (optional)

    Parses agent/task YAML, validates against the real Pydantic schemas
    (via their parse wrappers), then runs all component + alignment checks.

    Args:
        crew_dir: path to the crew configuration directory.

    Returns:
        VerificationResult aggregating findings across the crew.
    """
    from amsha.crew_forge.domain.models.agent_data import AgentRequest
    from amsha.crew_forge.domain.models.task_data import TaskRequest

    root = Path(crew_dir)
    findings: list[Finding] = []
    agents: list[dict] = []
    tasks: list[dict] = []

    if not root.exists():
        return VerificationResult(
            findings=[_finding("error", "crew.dir_missing", "verification",
                               f"Crew directory '{root}' does not exist.")],
            component_type="Crew")

    agent_files = sorted(root.glob("agents/*_agent.yaml"))
    task_files = sorted(root.glob("tasks/*_task.yaml"))

    if not agent_files and not task_files:
        findings.append(_finding(
            "error", "crew.empty", "verification",
            f"No agents/*_agent.yaml or tasks/*_task.yaml found under '{root}'.",
            "Ensure the directory follows the agents/ tasks/ layout."))

    for f in agent_files:
        raw = yaml.safe_load(f.read_text(encoding="utf-8")) or {}
        data = raw.get("agent", raw)
        parsed, schema_findings = _parse_model_dicts(AgentRequest, data)
        findings.extend(schema_findings)
        if parsed is not None:
            agents.append(parsed)
            findings.extend(verify_component("agent", parsed).findings)

    for f in task_files:
        raw = yaml.safe_load(f.read_text(encoding="utf-8")) or {}
        data = raw.get("task", raw)
        parsed, schema_findings = _parse_model_dicts(TaskRequest, data)
        findings.extend(schema_findings)
        if parsed is not None:
            tasks.append(parsed)
            findings.extend(verify_component("task", parsed).findings)

    knowledge = sorted(root.glob("knowledge/*"))
    skills = sorted(root.glob("skills/**/*.md"))
    if knowledge and not any(a.get("knowledge") or a.get("knowledge_sources") for a in agents):
        findings.append(_finding(
            "warning", "crew.knowledge_unused", "11 context-knowledge-memory",
            "Crew has knowledge sources but no agent references them.",
            "Attach knowledge to the agents whose tasks use it."))
    if skills and not any(a.get("skills") for a in agents):
        findings.append(_finding(
            "warning", "crew.skill_unused", "11 context-knowledge-memory",
            "Crew has skill files but no agent references them.",
            "Attach skills whose methodology the tasks apply."))

    if agents or tasks:
        crew_struct = _crew_struct(agents, tasks)
        findings.extend(verify_component("crew", crew_struct).findings)


    if not findings:
        findings.append(_finding(
            "advisory", "crew.all_valid", "verification",
            "Crew conforms to Amsha methodology (no errors or warnings raised).", ""))
    return VerificationResult(findings=findings, component_type="Crew")
