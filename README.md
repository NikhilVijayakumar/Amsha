# Amsha

**Amsha** is a lightweight library for **CrewAI** orchestration. It provides configuration management, agent/task definition, knowledge integration, and monitoring utilities — letting you define crews in YAML (or MongoDB) and run them with minimal boilerplate.

---

## Key Features

### Crew Forge & Orchestration
- **Dual Modes**: File-based (YAML) or DB-based (MongoDB) crew definitions.
- **Flows**: Multi-crew pipelines via CrewAI `Flow` — ordered execution with shared state.
- **Memory & Checkpointing**: Opt-in per crew (`memory: true`, `checkpoint:` config) — off by default.
- **Tracing**: Opt-in CrewAI native tracing (`tracing: true`) — off by default, sends prompts to CrewAI's hosted dashboard.

### Tools & MCP
- **Tool Registry**: Agents and tasks declare tools by name in YAML (`tools: [file_read, directory_read]`). Ships with built-in tools; extend with `register_tool()`.
- **MCP Servers**: Agents connect to MCP servers via structured YAML (`mcp_servers:`) — stdio, HTTP, or SSE transports.

### Knowledge Management
- **Multi-Format**: Docling-powered sources for Markdown, PDF, DOCX, HTML, XLSX, PPTX, images.
- **JSON Native**: CrewAI's `JSONKnowledgeSource` for structured JSON files.
- **Auto-Routing**: `.json` paths route to JSON source; everything else to Docling.

### Skills
- **Runtime Skills**: Agents reference CrewAI skills by name in YAML (`skills: ["domain-skills"]`). Amsha resolves names to skill search paths.

### Monitoring & Observability
- **CrewPerformanceMonitor**: Real-time CPU/GPU/memory tracking during execution.
- **AmshaEventListener**: Event-bus subscriber for per-task, per-LLM-call, per-tool-call lifecycle logs — local, no cloud dependency.
- **Contribution Analysis & Reporting**: Feature attribution analysis and Excel report generation.

### LLM Factory
- **Unified Config**: One YAML for all LLM providers (Ollama, LM Studio, OpenRouter, Azure, Gemini).
- **Purpose Profiles**: Creative (high temperature) vs. Evaluation (deterministic) modes.

---

## Installation

```bash
pip install amsha
```

Optional: for document processing features:
```bash
pip install docling
```

---

## Quick Start

```python
from nikhil.amsha.crew_forge.orchestrator.file.amsha_crew_file_application import AmshaCrewFileApplication
from nikhil.amsha.llm_factory.domain.llm_type import LLMType

config_paths = {
    "app": "config/app_config.yaml",
    "job": "config/job_config.yaml",
    "llm": "config/llm_config.yaml"
}

app = AmshaCrewFileApplication(config_paths=config_paths, llm_type=LLMType.CREATIVE)
```

### Agent YAML with Tools, Skills, and MCP

```yaml
# agents/researcher_agent.yaml
agent:
  role: "Researcher"
  goal: "Research topics thoroughly"
  backstory: "Expert researcher with access to web and files"
  tools: [file_read, directory_read]
  skills: ["domain-skills"]
  mcp_servers:
    - transport: stdio
      command: python
      args: [servers/db_server.py]
      env:
        DB_HOST: localhost
```

### Crew Config with Memory, Checkpointing, Tracing

```yaml
# job_config.yaml
crews:
  research_crew:
    memory: true
    checkpoint:
      enabled: true
      provider: json
      location: "./.Amsha/execution/checkpoints"
    tracing: true      # opt-in: sends prompts to CrewAI dashboard
    steps:
      - task_key: research_task
        agent_key: researcher_agent
```

### Multi-Crew Pipeline

```yaml
pipeline:
  - "research_crew"
  - "writing_crew"
```

```python
outputs = app.run_pipeline({"brief": "..."})
```

---

## Configuration Structure

- **`app_config.yaml`**: Global settings (directories, output paths).
- **`job_config.yaml`**: Crew definitions, steps, pipelines, knowledge sources.
- **`llm_config.yaml`**: LLM provider, model, API keys, creative/evaluation profiles.

---

## Testing

```bash
python -m pytest tests/unit/
```

With coverage:
```bash
python -m pytest tests/unit/ --cov=amsha --cov-report=term-missing
```

---

## Documentation

- [Crew Forge](docs/feature/crew_forge/About.md) — orchestration, YAML schema, tools, MCP, flows
- [Crew Monitor](docs/feature/crew_monitor/About.md) — performance monitoring, event observability
- [LLM Factory](docs/feature/llm_factory/About.md) — LLM configuration and profiles
