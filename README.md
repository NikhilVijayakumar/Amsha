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
*   **Multi-Format Support**: Uses `AmshaCrewDoclingSource` (powered by [Docling](https://github.com/DS4SD/docling)) to ingest knowledge. **(Currently tested with Markdown)**.
*   **Markdown Conversion**: Automatically converts various document formats into Markdown for optimal LLM consumption.
*   **Flexible Sources**: Supports both local file paths and URLs.

### 🔄 Input & Data Handling
*   **Flexible Inputs**: seamlessly handle inputs from multiple sources—direct configuration values, text files, or JSON data.
*   **MongoDB Sync**: The `SyncCrewConfigManager` allows you to sync your local crew configurations to a MongoDB database, keeping your deployment environment up-to-date with your local development.

### 🔌 Core Integrations
*   **Vak Integration**: Built on top of the [Vak](https://github.com/NikhilVijayakumar/Vak) library for robust core functionalities.
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
from nikhil.vak.domain.llm_factory.domain.llm_type import LLMType

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
from nikhil.vak.domain.llm_factory.domain.llm_type import LLMType

# Initialize with DB-specific logic
app = AmshaCrewDBApplication(config_paths=config_paths, llm_type=LLMType.CREATIVE)
```

### 3. Knowledge Management

Easily attach knowledge sources to your agents or crews using `AmshaCrewDoclingSource`.

```python
from nikhil.amsha.crew_forge.knowledge.amsha_crew_docling_source import AmshaCrewDoclingSource

# Create a knowledge source from a Markdown file
knowledge_source = AmshaCrewDoclingSource(
    file_paths=[
        "path/to/document.md"
    ]
)

# This source can now be passed to your CrewAI agents
```

### 4. Syncing Configurations to MongoDB

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

---

## ⚙️ Configuration Structure

Amsha relies on a structured configuration approach:

*   **`app_config.yaml`**: Global application settings (directories, logging, etc.).
*   **`job_config.yaml`**: Defines the pipeline, including which crews to run, their steps, and input/output handling.
*   **`llm_config.yaml`**: Configuration for the LLM Factory (provider, model, API keys).

---

## 📄 Documentation

For more detailed information on coding standards and architecture, please refer to:
*   [AGENTS.md](AGENTS.md): Coding Constitution & Standards
*   [DEPENDENCIES.md](DEPENDENCIES.md): Framework Dependencies & Isolation Strategies

---

## 📜 License

[Insert License Information Here]
