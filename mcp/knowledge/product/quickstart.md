---
type: Reference
title: "Amsha Quick Start"
description: "The quick start procedure for the Amsha library, served standalone by the MCP server."
tags: [amsha, mcp, product, quickstart]
status: stable
section: "Quick Start"
source_file: "README.md"
generated: { by: "process:project-product-knowledge", at: 2026-09-30T00:00:00Z }
---

# Amsha Quick Start

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
