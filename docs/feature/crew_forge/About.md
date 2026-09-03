# Amsha

**Amsha** is a powerful, lightweight library designed to streamline **CrewAI** orchestration. It serves as a foundational "Crew Forge," providing essential boilerplate, configuration management, and helper utilities to build scalable and maintainable AI agent systems.

Amsha manages your agents and tasks via version-controlled YAML configuration files, providing the tools to simplify your workflow.

---

## 🚀 Key Features

### 🛠️ Crew Forge & Orchestration
Amsha abstracts away the repetitive boilerplate code required to set up CrewAI agents and tasks.
*   **Boilerplate Generation**: Quickly spin up crews with standardized structures.
*   **File-Based Orchestration**: Define agents and tasks in YAML files for version-controlled, file-driven workflows.

### 📚 Advanced Knowledge Management
Amsha integrates powerful knowledge source management capabilities.
*   **Multi-Format Support**: Uses `AmshaCrewDoclingSource` (powered by [Docling](https://github.com/DS4SD/docling)) to ingest documents (Markdown, PDF, DOCX, HTML, XLSX, PPTX, images), and `AmshaJsonKnowledgeSource` (powered by CrewAI's native `JSONKnowledgeSource`) for structured JSON files. Reasonably tested with Markdown; the other formats flow through the same source classes.
*   **Automatic Format Routing**: When a `knowledge_sources` entry ends in `.json` it is routed to `AmshaJsonKnowledgeSource`; every other format goes to `AmshaCrewDoclingSource`.
*   **Markdown Conversion**: Automatically converts various document formats into Markdown for optimal LLM consumption.
*   **Flexible Sources**: Supports both local file paths and URLs (URLs for docling sources only — the JSON source is local-file only).

### 🔄 Input & Data Handling
*   **Flexible Inputs**: seamlessly handle inputs from multiple sources—direct configuration values, text files, or JSON data.

---

## 📦 Installation

Amsha requires Python 3.10+ and can be installed via pip.

```bash
pip install amsha
```

**Note**: To use the advanced document processing features, ensure you have `docling` installed:
```bash
uv add docling
# or
pip install docling
```

---

## 📖 Usage

### 1. Orchestration (File-Based)

Use `AmshaCrewFileApplication` to run crews defined in YAML configuration files.

```python
from nikhil.amsha.crew_forge.orchestrator.file.amsha_crew_file_application import AmshaCrewFileApplication
from nikhil.amsha.llm_factory.domain.llm_type import LLMType

# Define paths to your configuration files
config_paths = {
    "app": "config/app_config.yaml",
    "job": "config/job_config.yaml",
    "llm": "config/llm_config.yaml"
}

# Initialize and run
app = AmshaCrewFileApplication(config_paths=config_paths, llm_type=LLMType.CREATIVE)
# The application will automatically load agents/tasks from the YAMLs defined in job_config
```

### 2. Agent & Task Capability Tuning

Beyond `role`/`goal`/`backstory`, `AgentRequest` and `TaskRequest` expose CrewAI's execution-tuning and capability fields directly through YAML — no Python required.

**Agent-level** (`agents/*_agent.yaml`):

```yaml
agent:
  role: "Senior Researcher"
  goal: "..."
  backstory: "..."
  max_iter: 25              # max reasoning/tool-call iterations (CrewAI default: 25)
  max_rpm: 10                # requests-per-minute cap
  max_execution_time: 300    # seconds
  max_retry_limit: 2         # retries on tool failure (CrewAI default: 2)
  respect_context_window: true
  allow_delegation: false    # CrewAI default: false
  reasoning: true            # enable CrewAI's reasoning model
  max_reasoning_attempts: 3
  multimodal: true           # enable image/audio inputs
  system_template: "..."     # override the system prompt template
  prompt_template: "..."
  response_template: "..."
```

Every field is optional (`None` by default) — an unset field falls through to CrewAI's own default (verified: `max_iter=25`, `max_retry_limit=2`, `allow_delegation=False`, `reasoning=False`).

**Task-level** (`tasks/*_task.yaml`):

```yaml
task:
  name: "review_draft"
  description: "..."
  expected_output: "..."
  context: ["research_task"]   # names of prerequisite tasks whose output feeds this one
  async_execution: false
  human_input: true             # require human approval before final output
  markdown: true                 # render output as markdown
  guardrail: "Output must be valid JSON matching the report schema."
  guardrail_max_retries: 3
```

`context` resolves task **names** to CrewAI `Task` objects at build time — referencing an unknown task name raises a clear error rather than failing silently.

### 3. Knowledge Management

Easily attach knowledge sources to your agents or crews. In the file-based orchestrator, list paths under a crew's or a step's `knowledge_sources` in the job config; `.json` entries automatically use `AmshaJsonKnowledgeSource` and every other format uses `AmshaCrewDoclingSource`. You can also construct sources directly:

```python
from nikhil.amsha.crew_forge.knowledge.amsha_crew_docling_source import AmshaCrewDoclingSource
from nikhil.amsha.crew_forge.knowledge.amsha_json_knowledge_source import AmshaJsonKnowledgeSource

# Document knowledge source (Markdown, PDF, DOCX, HTML, XLSX, PPTX, images)
doc_source = AmshaCrewDoclingSource(
    file_paths=["path/to/document.md"]
)

# Structured JSON knowledge source (local file paths only)
json_source = AmshaJsonKnowledgeSource(
    file_paths=["path/to/products.json"]
)

# These sources can now be passed to your CrewAI agents
```

### 4. Skills

CrewAI Skills inject instructions/context ("how to think") rather than callable actions. Place a `skills/` directory next to an agent's `agents/` and `tasks/` directories inside its use case, with each immediate child being a skill search path whose own subdirectories contain a `SKILL.md`. Reference a skill in the agent YAML by its search-path directory name:

```yaml
# copy/agents/copywriter_agent.yaml
agent:
  role: "Expert Copywriter"
  ...
  skills: ["domain-skills"]   # resolves to <use case>/skills/domain-skills
```

```text
copy/
├── agents/copywriter_agent.yaml
├── tasks/ad_copy_task.yaml
└── skills/
    └── domain-skills/
        └── ad-copy/
            └── SKILL.md
```

Amsha resolves the bare name to the `skills/<name>` path before passing it to CrewAI. This is a runtime **agent/crew Skill** — unrelated to the Claude Code project-development skills under `docs/reference/agent/skills/` that are used to work *on* Amsha's own codebase.

### 5. Memory & Checkpointing

Crew-level execution features are opted in per crew in `job_config.yaml`. Both are **off by default**, preserving existing behavior.

```yaml
crews:
  copy_crew:
    memory: true
    checkpoint:
      enabled: true
      provider: json        # or "sqlite"
      location: "./.Amsha/execution/checkpoints"
      on_events: ["task_completed"]
      max_checkpoints: 5
    steps: [...]
```

-   **Memory** (`memory: true`) enables CrewAI's unified memory (`Crew(memory=True)`). Storage stays at CrewAI's default LanceDB path `./.crewai/memory`. **Gotcha:** memory's write-time LLM analysis means every memory write costs an extra LLM call (short queries <200 chars skip it) — see the token-usage spike in `CrewPerformanceMonitor` if you enable memory.
-   **Checkpointing** (`checkpoint:`) maps `enabled`/`provider`/`location`/`on_events`/`max_checkpoints` onto CrewAI's `CheckpointConfig`. `enabled: false` (or omitting the block) keeps checkpointing off. After a run, `BaseCrewOrchestrator` records the checkpoint `location` on its `ExecutionState`; resume any previously checkpointed run with:

```python
app.orchestrator.resume_crew(
    crew_name="copy_crew",
    inputs={},
    execution_id="<previous execution id>",
    restore_from="<crewai checkpoint id>",   # e.g. 20260902_123456_abcd1234
)
```

`resume_crew` builds a fresh crew and calls CrewAI's `kickoff(from_checkpoint=...)`, which skips already-completed tasks.

### 6. Multi-Crew Pipelines (Flows)

When a `job_config.yaml` declares a `pipeline` (an ordered list of crew names), it can be run as a CrewAI `Flow` instead of driving each crew manually. Every pipeline step delegates to the same `run_crew()` path, so each crew keeps its execution state, performance monitoring, and checkpoint recording — nothing is orphaned by the Flow split.

```yaml
pipeline:            # ordered: each runs only after the previous completes
  - "copy_crew"
  - "review_crew"
```

```python
app = MyApp(config_paths, llm_type)
outputs = app.run_pipeline({"brief": "..."})     # INTERACTIVE -> dict {crew_name: result}
# or async submit:
handle = app.run_pipeline({"brief": "..."}, mode=ExecutionMode.BACKGROUND)  # ExecutionHandle
```

`outputs` maps each crew name to its raw result (`PipelineState.outputs`). Inputs passed to `run_pipeline` are fed to every crew step; omitted, they default to the union of each pipeline crew's declared `input` definitions. Single-crew runs remain exactly as before via `orchestrator.run_crew()` — the Flow path is strictly additive, and branching (`@router`) is a future extension, not part of this version.

### 7. Tools

Agents and tasks can declare tools by name in YAML. Tool names are resolved against a registry that ships with built-in tools (`file_read`, `directory_read`, `scrape_website`) and can be extended with custom `BaseTool` subclasses.

```yaml
# copy/agents/researcher_agent.yaml
agent:
  role: "Researcher"
  ...
  tools: [file_read, directory_read]
```

Task-level tools override agent-level tools for that task (CrewAI's own precedence):

```yaml
# copy/tasks/scrape_task.yaml
task:
  name: "scrape"
  ...
  tools: [scrape_website]    # replaces agent tools for this task only
```

Register custom tools programmatically:

```python
from amsha.crew_forge.service.tool_registry import register_tool
from crewai.tools import BaseTool

class MyCustomTool(BaseTool):
    name: str = "my_tool"
    description: str = "Does something useful"
    def _run(self, **kwargs) -> str:
        return "result"

register_tool("my_tool", MyCustomTool)
```

### 8. MCP Server Integration

Agents can connect to MCP servers (stdio, HTTP, or SSE transports) via structured YAML configuration. Stdio is the recommended transport for local MCP servers.

```yaml
# copy/agents/db_agent.yaml
agent:
  role: "Database Agent"
  ...
  mcp_servers:
    - transport: stdio
      command: python
      args: [servers/db_server.py]
      env:
        DB_HOST: localhost
```

**Security note:** Stdio config specifies a `command` + `args` for a subprocess. Restrict which commands are permitted at the application level — don't let untrusted YAML declare arbitrary subprocess commands.

### 9. Crew Tracing (Opt-In)

CrewAI native tracing sends full prompt/response content to CrewAI's hosted dashboard. **Off by default** — enable explicitly only if you've reviewed the cloud dependency and data-sensitivity implications.

```yaml
# job_config.yaml
crews:
  copy_crew:
    tracing: true          # requires crewai login; sends prompts to app.crewai.com
    steps: [...]
```

Amsha's `AmshaEventListener` (local, self-hosted observability) remains the primary default path. Tracing is additive for teams that specifically want CrewAI's hosted trace UI.

---

## ⚙️ Configuration Structure

Amsha relies on a structured configuration approach:

*   **`app_config.yaml`**: Global application settings (directories, logging, etc.).
*   **`job_config.yaml`**: Defines the pipeline, including which crews to run, their steps, and input/output handling.
*   **`llm_config.yaml`**: Configuration for the LLM Factory (provider, model, API keys).

---

