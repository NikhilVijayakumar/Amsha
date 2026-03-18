# Amsha Developer & User Guide

Welcome to **Amsha**, the highly modular, production-grade library for executing, managing, and orchestrating CrewAI workflows. The overarching goal of Amsha is to safely construct multi-agent environments using Strict Configuration dependencies, enforcing clean boundaries, and ensuring zero silent failures at runtime.

This guide details what Amsha provides out-of-the-box, how you can use it within your projects, the strict configuration structures you MUST provide, and where to find deep-dive module documentation.

---

## 1. Features Available

Amsha provides multiple robust systems aimed at enterprise-level CrewAI orchestration. Below are the key modules available:

- **Crew Forge (`amsha.crew_forge`)**: The core orchestrator module. Provides dual execution pathways—either through a Database (`AmshaCrewDBApplication`) or File System (`AmshaCrewFileApplication`). It dynamically builds Crews, tasks, and agents based on blueprints without needing to hardcode Crew logic.
- **LLM Factory (`amsha.llm_factory`)**: Centralized LLM Provider architecture. Safely defines API endpoints, default models, fallback behaviors, and unified configuration (OpenAI, Gemini, Local LM Studio).
- **Crew Monitor (`amsha.crew_monitor`)**: Quality assurance checks and event logging for active interactions, metrics gathering, and observability for long-running multi-agent systems.
- **Crew Generation (`amsha.crew_gen`)**: Dynamic code translation/generation utilities focused dynamically injecting task or scenario definitions on the fly.
- **Research / Information Retrieval (`amsha.research`)**: Implements tools pointing to web search, arXiv API, or Docling sources, feeding raw or processed text back to your Agents.

---

## 2. Configuration Guidelines (Strict Validation)

Amsha enforces **Strict Configuration Validation**. It requires users to pass complete config dictionaries/YAML files at runtime. It **does not fallback to risky defaults**. If a property is missing (like a `domain_root_path`), Amsha throws an `AmshaConfigurationException` right at initialization. 

You must provide three primary configuration blocks to initialize your Amsha app:

### A. App Configuration (`app_config.yaml`)
Global details detailing where artifacts should be saved, and where the domain definitions exist.
```yaml
backend: "mongo" # or "file"
domain_root_path: "path/to/my/app/crew_configs"
output_dir_path: "path/to/save/outputs"
mongo: # (If backend: mongo)
  uri: "mongodb://user:pass@localhost:27017"
  db_name: "amsha_db"
```

### B. LLM Configuration (`llm_config.yaml`)
Defines hyper-parameters, LLM Models, and provider mapping.
Certain properties (like `base_url` or `presence_penalty`) are strictly validated if provided, but remain optional as they don't apply to every model (e.g. Gemini).
```yaml
llm:
  creative:
    default: gemini
    models:
      gemini:
        model: "gemini/gemini-2.5-flash"
        api_key_env: "GEMINI_API_KEY"
      phi:
         model: "lm_studio/phi-4-reasoning"
         base_url: "http://localhost:1234/v1"
         api_key: "dummy"
llm_parameters:
  creative:
    temperature: 0.8
    top_p: 0.9
```

### C. Job Configuration (`job_config.yaml`)
Defines the pipeline execution structure and maps task parameters.
```yaml
pipeline:
  - my_marketing_crew

module_name: "marketing" # points to domain_root_path/marketing/...

crews:
  my_marketing_crew:
    steps:
      - task_key: "write_ad_copy_task"
        agent_key: "copywriter_agent"
    input:
      topic: "New AI Product Launch"
```

---

## 3. How to Use Amsha

### Step 1: Initialize your Application
Decide whether your blueprints (the Agent/Task Yamls) reside in a DB or as Files. Inherit from the relevant base class.

```python
from amsha.crew_forge.orchestrator.file.amsha_crew_file_application import AmshaCrewFileApplication
from amsha.llm_factory.domain.llm_type import LLMType

class MyMarketingApp(AmshaCrewFileApplication):
    def __init__(self, config_paths: dict):
        # The parent initializes the `StrictConfigValidator` automatically!
        super().__init__(config_paths, LLMType.CREATIVE)

    def run(self):
        # Custom logic looping through crews or custom inputs
        pipeline_steps = self.job_config.get("pipeline", [])
        for crew in pipeline_steps:
             inputs = self._prepare_inputs_for(crew)
             result = self.orchestrator.run_crew(crew_name=crew, inputs=inputs)
             print("Result:", result)
```

### Step 2: Define your Configurations & Execute
Pass the absolute/relative paths to your configuration files to instantiate and run.

```python
if __name__ == "__main__":
    configs = {
        "llm": "config/llm_config.yaml",
        "app": "config/app_config.yaml",
        "job": "config/job_config.yaml"
    }
    
    # Amsha processes the paths, maps Strict Data Models, and prepares the Dependency Injector Containers
    app = MyMarketingApp(config_paths=configs)
    try:
        app.run()
    except Exception as e:
        print(f"Error running application: {e}")
```

---

## 4. Deep Dive Documentation (Module Level)

For comprehensive technical insights, API contracts, sequence diagrams, and class layouts for each module, please visit the internal module documentation found in the `docs/` folder:

1. **[Crew Forge (docs/crew_forge/About.md)](docs/crew_forge/About.md)** - Blueprint execution, Job orchestrations, Atomic Builders, File vs. DB Modes.
2. **[LLM Factory (docs/llm_factory/About.md)](docs/llm_factory/About.md)** - Model abstractions, LiteLLM bindings, dynamic switching.
3. **[Crew Gen (docs/crew_gen/About.md)](docs/crew_gen/About.md)** - Utilities handling generator patterns and templates.
4. **[Crew Monitor (docs/crew_monitor/About.md)](docs/crew_monitor/About.md)** - Diagnostics, tracking loops, execution callbacks.
5. **[Research (docs/research/About.md)](docs/research/About.md)** - Knowledge parsing tools and providers.
6. **[Paper Compilation (docs/paper/About.md)](docs/paper/About.md)** - Tools for automatically parsing insights or source code into documentation suites or academic journals.

> **💡 Note for Developers:** All logic additions should be strictly isolated ensuring that inner layers (Domain) never query outer layers (Infrastructure/API). Please review `AGENTS.md` in the root repository to understand the comprehensive architecture rules (Clean Architecture, Protocol interfaces, DI Injection) enforced inside Amsha.
