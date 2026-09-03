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


def _check_multimodal_unjustified(a):
    if a.get("multimodal") is True:
        text = f"{a.get('role', '')} {a.get('goal', '')} {a.get('backstory', '')}"
        if not re.search(r"\b(image|audio|video|visual|photo|diagram|screenshot|voice|multimodal)\b", text, re.IGNORECASE):
            return [_finding("warning", "agent.multimodal_unjustified", "implementation/01-agent-engineering.md §26",
                             "multimodal is enabled but nothing in role/goal/backstory suggests image/audio/document input.",
                             "Disable multimodal unless this agent's tasks genuinely consume non-text input.")]
    return []


def _check_execution_tuning_extreme(a):
    max_iter = a.get("max_iter")
    max_retry = a.get("max_retry_limit")
    if (isinstance(max_iter, int) and max_iter > 100) or (isinstance(max_retry, int) and max_retry > 10):
        return [_finding("warning", "agent.execution_tuning_extreme", "implementation/01-agent-engineering.md §26",
                         f"max_iter={max_iter!r}/max_retry_limit={max_retry!r} far exceeds CrewAI's defaults (25/2) — runaway cost/latency risk.",
                         "Justify the higher limit explicitly, or return to CrewAI's default.")]
    return []


def _check_prompt_template_override(a):
    if any(a.get(f) for f in ("system_template", "prompt_template", "response_template")):
        return [_finding("advisory", "agent.prompt_template_override", "implementation/01-agent-engineering.md §26",
                         "Custom prompt template(s) set — CrewAI requires specific placeholders in an overridden template; a missing placeholder degrades or breaks the agent silently.",
                         "Verify the override includes every placeholder CrewAI's default template provides before shipping.")]
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


_STRICT_OUTPUT_SIGNALS = re.compile(
    r"\b(valid json|json schema|matching the schema|structured output|"
    r"must be json|strictly formatted|schema-compliant|exact format)\b",
    re.IGNORECASE,
)
_VAGUE_GUARDRAILS = {"must be good", "must be correct", "be accurate", "good output", "output must be good"}


def _check_guardrail_missing(t):
    text = f"{t.get('expected_output', '')} {t.get('description', '')}"
    if _STRICT_OUTPUT_SIGNALS.search(text) and not t.get("guardrail"):
        return [_finding("warning", "task.guardrail_missing_for_strict_output", "implementation/02-task-engineering.md §32",
                         f"Task '{t.get('name', '')}' demands a strict output format but sets no guardrail to enforce it.",
                         "Add a guardrail describing the required format so CrewAI retries on violation instead of passing it through.")]
    return []


def _check_guardrail_vague(t):
    guardrail = (t.get("guardrail") or "").strip()
    if guardrail and (len(guardrail) < 15 or guardrail.lower() in _VAGUE_GUARDRAILS):
        return [_finding("warning", "task.guardrail_too_vague", "implementation/02-task-engineering.md §32",
                         f"Guardrail '{guardrail}' is too vague to reliably validate against.",
                         "State the concrete, checkable condition the output must satisfy.")]
    return []


def _check_markdown_output_contradiction(t):
    if t.get("markdown") is True:
        text = t.get("expected_output", "")
        if re.search(r"\b(valid json|json schema|json object|json array)\b", text, re.IGNORECASE):
            return [_finding("error", "task.markdown_output_contradiction", "implementation/02-task-engineering.md §25, §26",
                             f"Task '{t.get('name', '')}' sets markdown=true but expected_output demands JSON — contradictory output contract.",
                             "Pick one: markdown rendering or structured JSON, not both.")]
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


_TRACING_PRIVACY_ACK = re.compile(
    r"\b(privacy|privacy-preserving|sensitive|consent|opt-in|opt in|data exit|"
    r"cloud (cost|transfer|exposure)|exposure|acknowledg|llm endpoint|private prompt|saniti[sz])\b",
    re.IGNORECASE,
)
_MEMORY_RETENTION_NEED = re.compile(
    r"\b(across (runs|executions|iterations)|previous (run|execution|revision)|remember|retain|historical|"
    r"lessons? (from|learned)|reject(ed)? feedback|iterate (over|across) runs|prior (result|finding|decision)|"
    r"user correction|long-running|multi-run|memory of)\b",
    re.IGNORECASE,
)


def _crew_def_fields(cf) -> dict:
    """Return the lifecycle-relevant, schema-relevant subset of a crew definition."""
    known = {
        "name", "description", "goal", "usecase", "module_name",
        "process", "collaboration", "manager_agent", "memory", "tracing",
        "checkpoint", "knowledge_sources", "steps", "agents", "tasks",
    }
    return {k: v for k, v in (cf or {}).items() if k in known}


def _crew_def_prose(cf) -> str:
    def _text(v):
        if isinstance(v, str):
            return v
        if isinstance(v, (list, tuple)):
            return " ".join(str(x) for x in v)
        if isinstance(v, dict):
            return " ".join(str(x) for x in v.values())
        return ""

    return " ".join(_text(cf[k]) for k in ("description", "goal", "usecase") if cf.get(k))


def _check_tracing_no_warning(cf):
    if cf.get("tracing") is not True:
        return []
    if not _TRACING_PRIVACY_ACK.search(_crew_def_prose(cf)):
        return [_finding("warning", "crew.tracing_enabled_no_warning",
                         "implementation/19-observability-and-tracing.md §177",
                         "Crew enables tracing (sends full prompt/response content to the LLM provider) but nothing in the crew definition acknowledges the privacy/cloud cost.",
                         "Acknowledge the exposure (e.g. note privacy/consent and that prompts exit to the model provider), or leave tracing off for sensitive executions.")]
    return []


def _check_memory_unjustified(cf):
    if not cf.get("memory"):
        return []
    if not _MEMORY_RETENTION_NEED.search(_crew_def_prose(cf)):
        return [_finding("warning", "crew.memory_unjustified",
                         "implementation/11-context-knowledge-memory.md (Memory Practice)",
                         "Crew enables memory (retains historical information) but no cross-execution retention need is evident in the crew definition.",
                         "Justify why history must be retained across runs, or set memory=false for a single-shot crew that never re-consumes history.")]
    return []


def _check_checkpoint_no_events(cf):
    cp = cf.get("checkpoint")
    if not cp:
        return []
    if isinstance(cp, dict):
        enabled = cp.get("enabled", True)
        if not enabled:
            return []
        on_events = cp.get("on_events")
    else:
        on_events = None
    if not on_events:
        return [_finding("warning", "crew.checkpoint_no_events",
                         "implementation/17-checkpointing-and-recovery.md §4",
                         "Crew enables checkpointing but declares no on_events (recovery triggers), so no checkpoint is ever captured and recovery cannot resume.",
                         "Declare on_events at real recovery boundaries (e.g. [\"task_completed\"]), or disable checkpointing if no durable resume point is needed.")]
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

_LOCAL_HOST_MARKERS = ("localhost", "127.0.0.1", "0.0.0.0", "::1")


def _lmstudio_lifecycle_enabled(m: dict):
    lifecycle = m.get("lmstudio_lifecycle")
    if isinstance(lifecycle, dict) and lifecycle.get("enabled"):
        return lifecycle
    return None


def _check_lmstudio_missing_base_url(m):
    lifecycle = _lmstudio_lifecycle_enabled(m)
    if lifecycle and not m.get("base_url"):
        return [_finding("error", "llm.lmstudio_lifecycle_missing_base_url",
                         "docs/proposal/14-llm-lifecycle-management.md",
                         "lmstudio_lifecycle.enabled is true but base_url is not set.",
                         "Set base_url to the LM Studio server (e.g. http://localhost:1234/v1) — LLMBuilder.build() raises ValueError at runtime without it.")]
    return []


def _check_lmstudio_non_local_base_url(m):
    lifecycle = _lmstudio_lifecycle_enabled(m)
    base_url = m.get("base_url") or ""
    if lifecycle and base_url and not any(marker in base_url for marker in _LOCAL_HOST_MARKERS):
        return [_finding("warning", "llm.lmstudio_lifecycle_non_local_base_url",
                         "docs/proposal/14-llm-lifecycle-management.md",
                         f"lmstudio_lifecycle is enabled against a base_url ('{base_url}') that doesn't look local.",
                         "This feature is scoped to a local LM Studio server only — confirm this isn't a shared/remote instance other processes also depend on.")]
    return []


def _check_lmstudio_model_id_mismatch(m):
    lifecycle = _lmstudio_lifecycle_enabled(m)
    model = m.get("model") or ""
    if lifecycle:
        model_id = lifecycle.get("model_id") or ""
        if model_id and model.startswith("lm_studio/") and model_id == model:
            return [_finding("warning", "llm.lmstudio_lifecycle_model_id_mismatch",
                             "docs/proposal/14-llm-lifecycle-management.md",
                             "lmstudio_lifecycle.model_id is identical to the litellm-prefixed 'model' field, including the 'lm_studio/' prefix.",
                             "model_id must be LM Studio's own model key (from GET /api/v1/models 'key' field), not the litellm-prefixed model string — strip the 'lm_studio/' prefix.")]
    return []


def _check_lmstudio_context_length_unset(m):
    lifecycle = _lmstudio_lifecycle_enabled(m)
    if lifecycle and lifecycle.get("context_length") is None:
        return [_finding("advisory", "llm.lmstudio_lifecycle_context_length_unset",
                         "docs/proposal/14-llm-lifecycle-management.md",
                         "lmstudio_lifecycle.context_length is unset — an already-loaded model is reused as-is, whatever context it happens to be loaded with.",
                         "Set context_length explicitly if the crew depends on a specific context window; leave unset only when any resident context length is acceptable.")]
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
        ("agent.multimodal_unjustified", "warning", "implementation/01-agent-engineering.md §26", "Unjustified multimodal", _check_multimodal_unjustified),
        ("agent.execution_tuning_extreme", "warning", "implementation/01-agent-engineering.md §26", "Extreme execution tuning", _check_execution_tuning_extreme),
        ("agent.prompt_template_override", "advisory", "implementation/01-agent-engineering.md §26", "Prompt template override", _check_prompt_template_override),
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
        ("task.guardrail_missing_for_strict_output", "warning", "implementation/02-task-engineering.md §32", "Guardrail missing for strict output", _check_guardrail_missing),
        ("task.guardrail_too_vague", "warning", "implementation/02-task-engineering.md §32", "Guardrail too vague", _check_guardrail_vague),
        ("task.markdown_output_contradiction", "error", "implementation/02-task-engineering.md §25, §26", "Markdown/JSON contradiction", _check_markdown_output_contradiction),
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
    "llm_model": [
        ("llm.lmstudio_lifecycle_missing_base_url", "error", "docs/proposal/14-llm-lifecycle-management.md", "Missing base_url", _check_lmstudio_missing_base_url),
        ("llm.lmstudio_lifecycle_non_local_base_url", "warning", "docs/proposal/14-llm-lifecycle-management.md", "Non-local base_url", _check_lmstudio_non_local_base_url),
        ("llm.lmstudio_lifecycle_model_id_mismatch", "warning", "docs/proposal/14-llm-lifecycle-management.md", "model_id/model confusion", _check_lmstudio_model_id_mismatch),
        ("llm.lmstudio_lifecycle_context_length_unset", "advisory", "docs/proposal/14-llm-lifecycle-management.md", "Context length unset", _check_lmstudio_context_length_unset),
    ],
}

_VALID_COMPONENTS = set(_COMPONENT_CHECKS.keys())

_COMPONENT_LABELS = {
    "agent": "Agent", "task": "Task", "crew": "Crew", "flow": "Flow",
    "knowledge": "Knowledge", "skill": "Skill", "tool": "Tool", "mcp": "MCP",
    "llm_model": "LLM Model",
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


_CREW_DEF_CHECKS: list[tuple[str, str, str, str, ComponentCheck]] = [
    ("crew.tracing_enabled_no_warning", "warning", "implementation/19-observability-and-tracing.md §177",
     "Tracing privacy unacknowledged", _check_tracing_no_warning),
    ("crew.memory_unjustified", "warning", "implementation/11-context-knowledge-memory.md (Memory Practice)",
     "Memory unjustified", _check_memory_unjustified),
    ("crew.checkpoint_no_events", "warning", "implementation/17-checkpointing-and-recovery.md §4",
     "Checkpoint with no events", _check_checkpoint_no_events),
]


def _check_lifecycle_conformance(fields: dict, findings: list[Finding]) -> list[Finding]:
    """Shape-check the crew lifecycle fields against CrewData's rules.

    Validated inline against the real `crew_data.py` field rules (verified directly):
    memory: bool; tracing: Optional[bool]; checkpoint: Optional[bool | dict] with
    keys enabled/on_events/provider/location/max_checkpoints.
    """
    source = "crew_forge/domain/models/crew_data.py (CrewData)"
    for key in ("memory", "tracing"):
        if key in fields and not isinstance(fields[key], bool):
            findings.append(_finding("error", "crew.lifecycle_field_type", source,
                                     f"Crew lifecycle field '{key}' must be a boolean, got {type(fields[key]).__name__}.",
                                     f"Set '{key}' to true/false."))
    cp = fields.get("checkpoint")
    if cp is not None and not isinstance(cp, (bool, dict)):
        findings.append(_finding("error", "crew.checkpoint_shape", source,
                                 f"'checkpoint' must be a bool or a dict with enabled/on_events/provider/location/max_checkpoints, got {type(cp).__name__}.",
                                 "Use `checkpoint: true`/`false`, or `checkpoint: {enabled: true, on_events: [...]}`."))
    elif isinstance(cp, dict):
        allowed = {"enabled", "on_events", "provider", "location", "max_checkpoints"}
        unknown = set(cp) - allowed
        if unknown:
            findings.append(_finding("error", "crew.checkpoint_unknown_keys", source,
                                     f"'checkpoint' dict has unknown keys: {sorted(unknown)}.",
                                     f"Allowed keys: {sorted(allowed)}."))
    return findings


def verify_crew_def(crew_def: dict) -> VerificationResult:
    """Verify a single crew definition's lifecycle settings (memory/tracing/checkpoint).

    The crew lifecycle fields live on the `crews[<name>]` block of a `job_config.yaml`
    (see `atomic_crew_file_manager.py`), not the `agents/ tasks/` directory that
    `verify_crew_yaml` reads — this is the faithful surface for them.

    Args:
        crew_def: the crew block (name, memory, tracing, checkpoint, description/goal, steps).

    Returns:
        VerificationResult with lifecycle conformance + design findings.
    """
    cf = _crew_def_fields(crew_def)
    findings: list[Finding] = []
    _check_lifecycle_conformance(cf, findings)
    for rule_id, severity, source, _label, check in _CREW_DEF_CHECKS:
        try:
            findings.extend(check(cf))
        except Exception:
            continue
    if not findings:
        findings.append(_finding(
            "advisory", "crew.lifecycle_all_valid", "verification",
            "Crew lifecycle settings conform to Amsha methodology (no errors or warnings raised).", ""))
    return VerificationResult(findings=findings, component_type="Crew")


def verify_job_config(job_config_path: str | Path) -> VerificationResult:
    """Verify every crew block in a `job_config.yaml` (memory/tracing/checkpoint).

    Args:
        job_config_path: path to a job_config.yaml with a `crews:` map.

    Returns:
        VerificationResult aggregating per-crew lifecycle findings.
    """
    root = Path(job_config_path)
    if not root.exists():
        return VerificationResult(
            findings=[_finding("error", "crew.job_config_missing", "verification",
                               f"Job config '{root}' does not exist.")],
            component_type="Crew")
    raw = yaml.safe_load(root.read_text(encoding="utf-8")) or {}
    crews = raw.get("crews")
    if not isinstance(crews, dict):
        return VerificationResult(
            findings=[_finding("error", "crew.job_config_no_crews", "verification",
                               f"Job config '{root}' has no 'crews:' mapping to verify.")],
            component_type="Crew")
    findings: list[Finding] = []
    for name, block in crews.items():
        if not isinstance(block, dict):
            block = {}
        named = {**(block or {}), "name": name}
        findings.extend(verify_crew_def(named).findings)
    if not findings:
        findings.append(_finding(
            "advisory", "crew.lifecycle_all_valid", "verification",
            "All crew lifecycle settings conform to Amsha methodology.", ""))
    return VerificationResult(findings=findings, component_type="Crew")

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


_YAML_FENCE = re.compile(r"```ya?ml\s*\n(.*?)\n```", re.DOTALL | re.IGNORECASE)

# Map a YAML block's top-level key to the prerequisite stage whose required
# fields it most plausibly fills. Keyed by any representative top-level key a
# user is likely to write in their markdown, grounding in the docs' own YAML.
_STAGE_KEY_HINTS: dict[str, str] = {
    "problem": "00", "problem_definition": "00",
    "goal": "01", "boundary": "01", "goal_boundary": "01",
    "process": "02", "processes": "02", "process_decomposition": "02",
    "contract": "03", "contracts": "03",
    "validation": "04",
    "flow": "05", "flow_order": "05", "transitions": "05", "state": "05",
    "failure": "06", "failures": "06", "recovery": "06",
    "capability": "07", "capabilities": "07",
    "architecture": "08", "architecture_yaml": "08", "validation_outcome": "08",
    "handoff": "09", "checklist": "09",
}


def _attribute_stage(block: dict) -> str | None:
    """Attribute a parsed YAML block to a prerequisite stage (00-09), or None.

    Uses the block's top-level key against `_STAGE_KEY_HINTS` first, then falls
    back to the stage whose required-field set the block overlaps most with.
    """
    keys = set(block)
    for k in keys:
        if k in _STAGE_KEY_HINTS:
            return _STAGE_KEY_HINTS[k]
    best, best_score = None, 0
    for stage, required in _PREREQ_REQUIRED_FIELDS.items():
        score = len(keys & required)
        if score > best_score:
            best, best_score = stage, score
    return best if best_score >= 1 else None


def _extract_yaml_blocks(text: str) -> list[dict]:
    """Return all YAML mappings embedded in a markdown doc's fenced blocks."""
    blocks: list[dict] = []
    for m in _YAML_FENCE.finditer(text or ""):
        try:
            parsed = yaml.safe_load(m.group(1))
        except (yaml.YAMLError, Exception):
            continue
        if isinstance(parsed, dict):
            blocks.append(parsed)
    return blocks


def _attribute_block(block: dict) -> tuple[str | None, dict]:
    """Attribute a block to a stage and return the effective artifact mapping.

    If a block is a single mapping wrapper (e.g. `problem_definition: {...}` or
    `goal: {...}`), the wrapped inner dict is the effective artifact for that
    stage and the wrapper key drives attribution. A list-valued key such as
    `contracts: [...]` stays a top-level list (stage 03 expects that shape).
    Returns (stage, artifact).
    """
    keys = set(block)
    if len(keys) == 1:
        key = next(iter(keys))
        val = block[key]
        if isinstance(val, dict) and key in _STAGE_KEY_HINTS:
            return _STAGE_KEY_HINTS[key], val
    stage = _attribute_stage(block)
    return stage, block


def verify_prerequisite_files(doc_dir: str | Path, pattern: str = "*.md") -> VerificationResult:
    """Verify a user's prerequisite documentation written as markdown/YAML.

    Scans `doc_dir` for markdown files, extracts the YAML code blocks each file
    embeds (the form the prerequisite methodology docs prescribe), attributes
    every block to a prerequisite stage (00-09), then runs the same
    `verify_prerequisite_artifacts` engine that the JSON path uses.

    Unlike the JSON path, this reports *what is absent*: a stage with no file
    or no attributable YAML block is surfaced as incomplete, so a user who has
    not (yet) written a stage sees exactly which stage to create, instead of a
    silent pass.

    Args:
        doc_dir: folder containing the user's prerequisite markdown documents.
        pattern: glob for markdown files (default `*.md`).

    Returns:
        VerificationResult with per-stage presence/absence + structural findings.
    """
    root = Path(doc_dir)
    if not root.is_dir():
        return VerificationResult(
            findings=[_finding("error", "prereq.doc_dir_missing", "prerequisite",
                               f"Documentation folder '{root}' does not exist.",
                               "Create the folder (and your prerequisite markdown files) or pass an existing path.")],
            component_type="Prerequisite artifacts")

    files = sorted(root.glob(pattern))
    if not files:
        return VerificationResult(
            findings=[_finding("error", "prereq.no_doc_files", "prerequisite",
                               f"Folder '{root}' contains no {pattern} files to verify.",
                               "Create prerequisite documents following the methodology (see get_prerequisite_stage for the required fields per stage).")],
            component_type="Prerequisite artifacts")

    artifacts: dict[str, dict] = {}
    unattributed: list[str] = []
    for fp in files:
        text = (fp.read_text(encoding="utf-8", errors="replace") or "")
        blocks = _extract_yaml_blocks(text)
        if not blocks:
            unattributed.append(fp.name)
            continue
        for block in blocks:
            stage, effective = _attribute_block(block)
            if stage is None:
                unattributed.append(fp.name)
                continue
            # Merge multiple blocks for the same stage; last write wins per key.
            artifacts.setdefault(stage, {}).update(effective)

    findings = verify_prerequisite_artifacts(artifacts).findings
    covered = set(artifacts)
    for stage in sorted(_PREREQ_REQUIRED_FIELDS):
        if stage not in covered:
            label = _PREREQ_LABELS.get(stage, f"stage {stage}")
            findings.append(_finding(
                "warning", f"prereq.{stage}_missing_doc", f"prerequisite/{label}",
                f"No attributable document found for prerequisite stage {stage} ({label}).",
                "Create the document with the required fields — see get_prerequisite_stage for the checklist."))
    if unattributed:
        findings.insert(0, _finding(
            "warning", "prereq.unattributed_docs", "prerequisite",
            f"These files/blocks had no recognizable prerequisite stage and were ignored: {sorted(set(unattributed))}.",
            "Use a top-level YAML key the methodology recognizes (e.g. problem_definition, goal, contracts,"
            " failures, capabilities) so each block can be attributed to a stage."))
    if not findings:
        findings.append(_finding(
            "advisory", "prereq.files_complete", "prerequisite",
            "All prerequisite stages have attributable, well-formed, consistent documents.", ""))
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
