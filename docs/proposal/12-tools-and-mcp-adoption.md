# Proposal 12 — Tools & MCP Integration (stdio-preferred)

| | |
|---|---|
| **Status** | ✅ Partial — Part 1 (Tools) done; Part 2 (MCP) config passthrough done and verified end-to-end on Windows against a real local LLM, lifecycle wrapper still deferred |
| **Priority** | New — requested directly, high value |
| **Risk** | Medium — MCP stdio is a real code-execution surface if exposed to untrusted YAML |
| **Effort** | Medium |
| **Depends on** | [02](02-crewai-version-migration.md), [08](08-agent-task-capability-expansion.md) |

## Execution Log

### Part 1 — Tools ✅ (2026-09-02)

- `tool_registry.py`: name→class mapping with `resolve_tools()`, `register_tool()`, `available_tools()`. Ships with 3 built-in tools (`file_read`, `directory_read`, `scrape_website`).
- `AgentRequest.tools: Optional[List[str]]` and `TaskRequest.tools: Optional[List[str]]` added to domain models.
- `CrewBuilderService.add_agent()`: resolves `agent_details.tools` via registry, merges with explicitly passed tools.
- `CrewBuilderService.add_task()`: resolves `task_details.tools` via registry — task-level tools override agent-level tools per CrewAI semantics.
- `CrewParser._pass_through_fields` automatically picks up `tools` from YAML (no parser changes needed).
- 6 unit tests in `test_tool_registry.py`, 6 new tests in `test_crew_builder_service.py`, 2 new tests in `test_crew_parser.py`.
- Custom tool registration: `register_tool("my_tool", MyToolClass)` for consumer-provided BaseTool subclasses.

### Part 2 — MCP Config Passthrough ✅ (2026-09-02)

- `McpServerConfig` Pydantic model in `mcp_data.py`: `transport` discriminator (`stdio`/`http`/`sse`), transport-specific fields (`command`/`args`/`env` for stdio; `url`/`headers` for http/sse).
- `AgentRequest.mcp_servers: Optional[List[McpServerConfig]]` added.
- `_mcp_config_to_crewai()` converts Amsha config to CrewAI's `MCPServerStdio`/`MCPServerHTTP` objects.
- `Agent(mcps=[...])` wired through `CrewBuilderService.add_agent()`.
- 2 new tests in `test_crew_builder_service.py`, 1 new test in `test_crew_parser.py`.

### Part 3 — Real example + Windows verification ✅ (2026-09-02)

`example/crew_forge/verify_capability_example.py --kickoff` now exercises this for real: the copywriter agent carries `tools: ["file_read"]` and an `mcp_servers` stdio entry pointing at `example/crew_forge/example_config/mcp_server/word_count_server.py` (a minimal `FastMCP` server), and the task instructs the agent to call `count_words` on each ad copy variation. Ran against a live local LLM (LM Studio, `qwen3.5-9b`) on Windows:

- **Windows stdio subprocess spawn/cleanup verified** — the previously-deferred blocker. `MCPServerStdio(command="python", args=[...])` spawned the server subprocess, the agent called `count_words` for real (output word counts matched, e.g. `"word_count": 23`), and the crew completed without a leaked/hung process.
- **Allowlist gate confirmed working as designed**: running without `AMSHA_MCP_STDIO_ALLOWLIST=python` set raises `CrewConfigurationException` before any subprocess spawns — the security mitigation from this proposal's Part 2 §2 is live, not just unit-tested.
- **Gotcha for anyone reproducing this**: `command: "python"` resolves against the *spawning process's* `PATH`, not `sys.executable` — if a system Python without `mcp` installed is ahead of the venv on `PATH`, the subprocess exits immediately and CrewAI reports it as `MCPConnectionError: Connection closed` (no import-error detail surfaces). Put the venv's `Scripts`/`bin` dir first on `PATH` before running `--kickoff`.
- **Correction to this proposal's own docs**: the "DSL `mcps=[...]` fails soft" claim in Part 2's "What CrewAI 1.15.18 offers" section does not hold in practice — a real connection failure raises `MCPConnectionError` and fails the crew, it does not silently degrade. Worth relying on the hard-fail behavior being real, not assuming soft-fail as a fallback.

### Deferred

- MCP adapter lifecycle management as an explicit Amsha-owned context-manager wrapper (open before `build()`, close after `kickoff()`) — CrewAI's own per-task `Agent.get_mcp_tools()` already handles connect/cleanup around the `mcps=[...]` DSL path (verified above), so this is now a "nice to have for explicit control," not a correctness gap.
- `tool_filter` on `McpServerConfig` — `create_static_tool_filter` not available in crewai 1.15.18; deferred until needed.
- HTTP/SSE transport full wiring — config shape ready, actual adapter wiring deferred.

## The gap, verified against source

Amsha's tool support today is a bare passthrough:

```python
def add_agent(self, agent_details: AgentRequest, knowledge_sources=None, tools: list = None) -> 'CrewBuilderService':
    ...
    "tools": tools or []
```

`AgentRequest` has **no `tools` field at all** — tools can only be attached by a Python caller passing a list directly to `add_agent()`, never through YAML config-as-code. There is zero MCP integration anywhere in the codebase (confirmed by grep — the only `BaseTool` reference in the whole repo is in an integration test, not production code). This is a real gap: CrewAI's own "Agent Capabilities" taxonomy splits into Action (Tools, MCP Servers, Apps) and Context (Skills, Knowledge) — Amsha has Context covered ([06](06-knowledge-json-native-support.md), [07](07-skills-adoption.md)) but nothing on the Action side beyond raw Python.

## Part 1 — Tools

### What CrewAI 1.15.18 offers

- Custom tools subclass `BaseTool`: `name`, `description`, optional `args_schema: Type[BaseModel]` (inferred from `_run()`'s signature if omitted), `_run(...)` does the work. A lighter `@tool("Tool Name")` decorator exists for function-based tools.
- **Attachment levels matter**: `tools=[...]` on `Agent` (used probabilistically across all its tasks) or on `Task` (scoped to one task). **Task-level tools override agent-level tools when both are set** — a real semantic Amsha's YAML schema needs to respect if it ever exposes tools at both levels.
- **Caching**: opt-in per tool via `tool.cache_function = fn(arguments, result) -> bool` — not automatic, no free win here.
- **Built-in catalog**: `crewai-tools` (already an Amsha dependency, pinned to `1.15.18`) ships 40+ ready-made tools — file/document, web scraping, search, DB/vector, AI/ML, cloud, automation. Amsha currently exposes none of these by name.

### Proposal

1. Add `tools: Optional[List[str]] = None` to `AgentRequest` and (new) `TaskRequest.tools: Optional[List[str]] = None` — string identifiers resolved against a small **tool registry**, not raw Python objects, since YAML can't carry callables. The registry maps a name (e.g. `"serper_search"`, `"file_read"`) to an actual `crewai_tools` class or an Amsha-authored `BaseTool` instance. Start the registry with a handful of the most commonly needed built-ins (search, file read, code interpreter) rather than trying to expose all 40+ up front.
2. `CrewBuilderService.add_agent()`/`.add_task()` resolve tool names through the registry the same way [07](07-skills-adoption.md) resolves skill names — bare name → registry lookup → raise `ValueError` on unknown name. Consistent pattern with what's already shipped.
3. Respect the task-overrides-agent precedence: if a `TaskRequest.tools` is set, pass it to `Task(tools=[...])` rather than relying on inherited agent tools — don't silently merge or ignore CrewAI's own override semantics.
4. Document (not build) a path for Amsha consumers to register their own custom `BaseTool` subclasses into the registry programmatically — Amsha doesn't need to invent a plugin system, a simple `register_tool(name, tool_instance)` function is enough.

## Part 2 — MCP, stdio-preferred

### What CrewAI 1.15.18 offers

Two integration paths:
- **DSL**: `Agent(mcps=["url", "slug#tool", ...])` — fails soft (unreachable server logged as a warning, agent proceeds with whatever resolved). Simple, but soft-fail is the wrong default for a config-as-code library where a broken MCP config should be loud, not silently degraded.
- **`MCPServerAdapter`** (from `crewai_tools`, wraps the `mcp` SDK) — explicit control, the path worth wrapping for Amsha's config-as-code model. Structured `MCPServerStdio`/`MCPServerHTTP`/`MCPServerSSE` classes exist in `crewai.mcp`.

Stdio config is the `mcp` SDK's own `StdioServerParameters`, not CrewAI-specific:

```python
from mcp import StdioServerParameters
import os

server_params = StdioServerParameters(
    command="python3",
    args=["servers/your_stdio_server.py"],
    env={"UV_PYTHON": "3.12", **os.environ},  # env REPLACES parent env, must re-include PATH etc.
)
with MCPServerAdapter(server_params, connect_timeout=60) as mcp_tools:
    agent = Agent(role="...", tools=mcp_tools)
```

**Lifecycle is the load-bearing detail**: the context-manager form kills the subprocess on exit, including on exception — this is the form to standardize on. The manual `.start()`/`.stop()` form requires the caller to guarantee `.stop()` runs (docs explicitly say "you MUST call `mcp_server_adapter.stop()`", recommending `try/finally`) — skipping this leaks the child process on any exception between start and use. `@CrewBase`-decorated crews get an implicit post-`kickoff()` shutdown hook.

### Security callout — this is the part to take seriously

Stdio MCP config is `command` + `args` + `env` for a subprocess CrewAI will actually spawn. **If Amsha's YAML schema lets an `agent.yaml`/`task.yaml` author specify an MCP stdio server's `command`/`args`, that YAML file becomes an arbitrary-code-execution vector** — anyone who can edit or supply that YAML can make Amsha's process launch anything. CrewAI's own docs provide no sandboxing, command allow-listing, or input sanitization for this — it's explicitly the integrator's problem. This matters more for Amsha than for a typical CrewAI app because Amsha's entire pitch is "YAML files as the source of truth, version-controlled like code" (`docs/feature/crew_forge/functional.md`) — which is exactly the surface an untrusted or compromised YAML file would exploit.

**Windows gotcha**: the stdio docs page has zero platform-specific notes — not "confirmed to work," just silent. Given Amsha's primary dev environment is Windows, this needs empirical verification (subprocess spawn/kill semantics differ Windows vs. POSIX) before shipping, not an assumption that it "should just work" because the docs don't say otherwise.

### Proposal

1. Add MCP config to `AgentRequest` as a **structured, non-freeform** field: `mcp_servers: Optional[List[McpServerConfig]] = None`, where `McpServerConfig` is an Amsha Pydantic model with `transport: Literal["stdio", "http", "sse"]` and transport-specific fields (`command`/`args`/`env` for stdio; `url`/`headers` for http/sse) — not a raw dict passthrough, so the schema itself documents and constrains what's expressible.
2. **Restrict stdio MCP config to a separate, explicitly-trusted config file** (e.g. `mcp_servers.yaml` at the app-config level, not per-agent YAML that might be authored by less-trusted contributors) — or, at minimum, an allowlist of permitted `command` values set by the application owner, not the YAML author. This is the concrete mitigation for the RCE-via-YAML concern above. Don't ship stdio MCP support that lets *any* `agent.yaml` in the repo declare an arbitrary subprocess command with no gate.
3. Wire the context-manager lifecycle into `CrewBuilderService`/`AtomicCrewFileManager` so MCP tool connections open before `build()` and close after `kickoff()` — mirroring the `try/finally` guarantee CrewAI's docs insist on, so a crash mid-build doesn't leak subprocesses.
4. Use `MCPServerAdapter` (explicit, hard-fail-friendly), not the DSL `mcps=[...]` form — the soft-fail behavior of DSL is wrong for a library whose whole point is making config errors loud and traceable, not silently degraded.
5. Verify stdio transport on Windows specifically as an implementation task, not an assumption — spawn a trivial local MCP stdio server, confirm subprocess cleanup actually happens on both normal exit and exception, before this ships as supported.
6. HTTP/SSE transports: lower priority than stdio per the user's stated preference, but the `McpServerConfig` model should have the shape ready (`url`/`headers`) since auth for those is just header-based — cheap to include now, not urgent to fully wire.

## What NOT to do

- Don't expose all 40+ `crewai_tools` by name on day one — start with a handful of concrete, requested-use-case tools in the registry, add more on demand.
- Don't use the DSL `mcps=[...]` soft-fail path as the primary integration — explicit `MCPServerAdapter` with hard failure on connection error is the right default for a config-as-code library.
- Don't let per-agent YAML declare arbitrary stdio `command`/`args` without an application-level allowlist gate — that's the one item in this proposal that's a security requirement, not a style preference.
- Don't skip the Windows stdio verification step — the docs' silence on Windows is not evidence it works.
