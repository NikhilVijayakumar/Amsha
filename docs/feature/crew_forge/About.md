# Amsha

**Amsha** is a powerful, lightweight library designed to streamline **CrewAI** orchestration. It serves as a foundational "Crew Forge," providing essential boilerplate, configuration management, and helper utilities to build scalable and maintainable AI agent systems.

Whether you are managing agents via configuration files or orchestrating them dynamically from a MongoDB database, Amsha provides the tools to simplify your workflow.

---

## 🚀 Key Features

### 🛠️ Crew Forge & Orchestration
Amsha abstracts away the repetitive boilerplate code required to set up CrewAI agents and tasks.
*   **Boilerplate Generation**: Quickly spin up crews with standardized structures.
*   **Dual Orchestration Modes**:
    *   **File-Based**: Define agents and tasks in YAML files for version-controlled, file-driven workflows.
    *   **DB-Based**: Fetch agent and task definitions dynamically from MongoDB, allowing for centralized management and updates without code changes.

### 📚 Advanced Knowledge Management
Amsha integrates powerful knowledge source management capabilities.
*   **Multi-Format Support**: Uses `AmshaCrewDoclingSource` (powered by [Docling](https://github.com/DS4SD/docling)) to ingest documents (Markdown, PDF, DOCX, HTML, XLSX, PPTX, images), and `AmshaJsonKnowledgeSource` (powered by CrewAI's native `JSONKnowledgeSource`) for structured JSON files. Reasonably tested with Markdown; the other formats flow through the same source classes.
*   **Automatic Format Routing**: When a `knowledge_sources` entry ends in `.json` it is routed to `AmshaJsonKnowledgeSource`; every other format goes to `AmshaCrewDoclingSource`.
*   **Markdown Conversion**: Automatically converts various document formats into Markdown for optimal LLM consumption.
*   **Flexible Sources**: Supports both local file paths and URLs (URLs for docling sources only — the JSON source is local-file only).

### 🔄 Input & Data Handling
*   **Flexible Inputs**: seamlessly handle inputs from multiple sources—direct configuration values, text files, or JSON data.
*   **MongoDB Sync**: The `SyncCrewConfigManager` allows you to sync your local crew configurations to a MongoDB database, keeping your deployment environment up-to-date with your local development.

### 🔌 Core Integrations
*   **MongoDB**: Native adapters for persisting and retrieving agent and task configurations.

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

### 2. Orchestration (DB-Based)

Use `AmshaCrewDBApplication` to run crews with definitions fetched from MongoDB.

```python
from nikhil.amsha.crew_forge.orchestrator.db.amsha_crew_db_application import AmshaCrewDBApplication
from nikhil.amsha.llm_factory.domain.llm_type import LLMType

# Initialize with DB-specific logic
app = AmshaCrewDBApplication(config_paths=config_paths, llm_type=LLMType.CREATIVE)
```

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

### 6. Syncing Configurations to MongoDB

Keep your database in sync with your local YAML configurations.

```python
from nikhil.amsha.crew_forge.sync.manager.sync_crew_config_manager import SyncCrewConfigManager

sync_manager = SyncCrewConfigManager(
    app_config_path="config/app_config.yaml",
    job_config_path="config/job_config.yaml"
)

# Syncs the configurations to the output path specified in job_config
sync_manager.sync()
```

### 7. Multi-Crew Pipelines (Flows)

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

---

## ⚙️ Configuration Structure

Amsha relies on a structured configuration approach:

*   **`app_config.yaml`**: Global application settings (directories, logging, etc.).
*   **`job_config.yaml`**: Defines the pipeline, including which crews to run, their steps, and input/output handling.
*   **`llm_config.yaml`**: Configuration for the LLM Factory (provider, model, API keys).

---


