# Proposal 08 — Expand AgentRequest/TaskRequest to Reach CrewAI's Actual Capability Surface

| | |
|---|---|
| **Priority** | Phase 3 — this unblocks nearly everything else |
| **Risk** | Medium — touches core domain models, needs backward compatibility |
| **Effort** | Medium |
| **Depends on** | [02](02-crewai-version-migration.md) |
| **Blocks** | [04](04-memory-adoption.md), [07](07-skills-adoption.md), and any use of reasoning/planning/guardrails |

## The core problem

This is the real bottleneck, more than the version pin. Today:

```python
class AgentRequest(BaseModel):
    role: str
    goal: str
    backstory: str
    usecase: Optional[str] = None

class TaskRequest(BaseModel):
    name: str
    description: str
    expected_output: str
    usecase: Optional[str] = None
```

And `CrewBuilderService` only ever constructs:

```python
Agent(role=..., goal=..., backstory=..., llm=self.llm, tools=tools or [])
Task(name=..., description=..., expected_output=..., agent=agent)
```

Even fully upgraded to CrewAI 1.15.18, **none of the following are reachable through Amsha's API today**, because there's no field to carry them from YAML/DB config through to the `Agent`/`Task` constructor call:

- Agent: `reasoning`, `max_reasoning_attempts`, `max_iter`, `max_rpm`, `max_execution_time`, `max_retry_limit`, `respect_context_window`, `multimodal`, `function_calling_llm`, `embedder`, `inject_date`/`date_format`, `system_template`/`prompt_template`/`response_template`/`use_system_prompt`, `allow_delegation`.
- Task: `context` (task dependency list), `async_execution`, `human_input`, `markdown`, `guardrail`/`guardrails`, `guardrail_max_retries`, `output_pydantic`/`output_json` (the builder already has an `output_json` *parameter* on `add_task`, but it's typed `Any` and just assigned raw — no structured Pydantic support), `callback`, `create_directory`.
- Crew: `planning`/`planning_llm`, `manager_llm` (hierarchical process), `before_kickoff_callbacks`/`after_kickoff_callbacks`, `cache`, `output_log_file`.

This is why memory, skills, reasoning, planning, and guardrails all show up as separate proposals but all point back here — there's nowhere to put the config today.

## Proposal

### 1. Extend the domain models — additive, backward-compatible

Every new field must be `Optional[...] = None` (or a sensible off-by-default value) so existing YAML/DB records with only `role/goal/backstory` continue to parse unchanged (per Amsha's own `FR-SYNC` unchanged-entity-detection logic, which presumably hashes/diffs YAML content — adding new optional fields shouldn't break that as long as `None` serializes consistently; verify against `crew_parser.py`/`database_seeder.py`).

```python
class AgentRequest(BaseModel):
    role: str
    goal: str
    backstory: str
    usecase: Optional[str] = None

    # New — execution tuning
    max_iter: Optional[int] = None
    max_rpm: Optional[int] = None
    max_execution_time: Optional[int] = None
    respect_context_window: Optional[bool] = None
    allow_delegation: Optional[bool] = None

    # New — capabilities
    reasoning: Optional[bool] = None
    max_reasoning_attempts: Optional[int] = None
    multimodal: Optional[bool] = None
    skills: Optional[List[str]] = None          # see 07
    knowledge_paths: Optional[List[str]] = None  # see 06

    # New — prompt customization
    system_template: Optional[str] = None
    prompt_template: Optional[str] = None
    response_template: Optional[str] = None
```

```python
class TaskRequest(BaseModel):
    name: str
    description: str
    expected_output: str
    usecase: Optional[str] = None

    # New
    context: Optional[List[str]] = None      # names of prerequisite TaskRequests
    async_execution: Optional[bool] = None
    human_input: Optional[bool] = None
    markdown: Optional[bool] = None
    guardrail: Optional[str] = None           # LLM-based guardrail description string, simplest form to expose via YAML
    guardrail_max_retries: Optional[int] = None
```

### 2. Update `CrewBuilderService` to pass through conditionally

Only set kwargs that were actually provided, so CrewAI's own defaults apply otherwise:

```python
def add_agent(self, agent_details: AgentRequest, knowledge_sources=None, tools: list = None) -> 'CrewBuilderService':
    kwargs = {"role": agent_details.role, "goal": agent_details.goal,
              "backstory": agent_details.backstory, "llm": self.llm, "tools": tools or []}
    for field in ("max_iter", "max_rpm", "max_execution_time", "respect_context_window",
                  "allow_delegation", "reasoning", "max_reasoning_attempts", "multimodal",
                  "skills", "system_template", "prompt_template", "response_template"):
        value = getattr(agent_details, field, None)
        if value is not None:
            kwargs[field] = value
    agent = Agent(**kwargs)
    ...
```

Same pattern for `add_task`. The `context` field needs a resolution step — Amsha builds tasks by name (`TaskRequest.name`), so `context: Optional[List[str]]` (task names) needs to be resolved to actual `Task` object references from `self._tasks` at build time, since CrewAI's `Task(context=[...])` expects `Task` instances, not names. This is the one field here that isn't a pure passthrough.

### 3. Update the YAML schema and MongoDB models to match

`crew_forge/seeding/parser/crew_parser.py`, `database_seeder.py`, and the two Mongo repo adapters (`agent_repo.py`, `task_repo.py`) presumably map YAML/DB documents 1:1 onto `AgentRequest`/`TaskRequest` today. This is where migration risk actually concentrates, so treat it as the **first implementation step, not an assumption to verify after the fact**:

- `grep -n "role\|goal\|backstory\|usecase" crew_parser.py` and the Mongo adapters — confirm whether they explicitly enumerate the four current fields (hardcoded shape, breaks silently on new fields) or deserialize generically via `AgentRequest(**doc)`/`TaskRequest(**doc)` (flows through automatically).
- Same check against `database_seeder.py`'s change-detection logic (`FR-SYNC-02`/`FR-SYNC-03` — "update if content changed," "no-op if unchanged") — if it hashes/diffs specific known fields rather than the full document, new optional fields could be silently ignored on update-detection even though they deserialize fine.
- Produce a short line-referenced inventory of what each of the four files actually does before writing any new field-handling code, so "flows through automatically" is a confirmed fact for this codebase, not a general Pydantic assumption.

### 4. Update `docs/feature/crew_forge/*.md` — this is a functional spec change

`functional.md`'s FR-STRUCT/FR-SYNC sections describe the YAML schema at a structural level (not field-by-field), so this may not need a rewrite — but any field-level documentation elsewhere in `docs/feature/crew_forge/` (`technical.md`) should be checked and updated.

## What NOT to do

- Don't expose every single CrewAI kwarg immediately — the list above is the ones with clear, immediate use cases (reasoning, planning, guardrails, context, skills are all things this exact proposal set wants). Things like `function_calling_llm`, `embedder` overrides, `inject_date` can be added on demand rather than speculatively.
- Don't make any new field required — that breaks every existing YAML/DB record Amsha users already have.
