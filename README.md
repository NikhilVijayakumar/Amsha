# Amsha

Amsha is a lightweight library designed to provide common configuration and helper utilities for CrewAI orchestration. It serves as a foundational component for building scalable and maintainable AI agent systems.

## Key Features

*   **Lightweight Core**: Focused on essential utilities and configurations, keeping the footprint small.
*   **Vak Integration**: Core dependency on [Vak](https://github.com/your-org/vak) for enhanced functionality.
*   **CrewAI Helpers**: Simplifies the setup and management of CrewAI agents and tasks.
*   **MongoDB Support**: Includes adapters for persisting agent and task configurations in MongoDB.

## Installation

Amsha requires Python 3.10+ and can be installed via pip.

```bash
pip install amsha
```

### Dependencies

Amsha depends on several key libraries, including:
*   `crewai`
*   `pymongo`
*   `pydantic`
*   `Vak` (Internal dependency)

See `pyproject.toml` for the full list of dependencies.

## Usage

### Basic Configuration

Amsha uses `pydantic` models for strict type validation of agent and task configurations.

```python
from amsha.models import AgentRequest, TaskRequest

# Define an agent
agent = AgentRequest(
    role="Researcher",
    goal="Discover new trends",
    backstory="An expert in market analysis."
)

# Define a task
task = TaskRequest(
    name="Market Research",
    description="Analyze the latest market trends.",
    expected_output="A comprehensive report."
)
```

### Using Repositories

Amsha provides repository interfaces for managing configurations.

```python
from amsha.repositories import AgentRepository, RepoData

repo_data = RepoData(
    mongo_uri="mongodb://localhost:27017/",
    db_name="crewai_db",
    collection_name="agents"
)
agent_repo = AgentRepository(repo_data)

# Create an agent in the database
agent_repo.create_agent(agent)
```

## Documentation

For more detailed information on coding standards and architecture, please refer to:
*   [AGENTS.md](AGENTS.md): Coding Constitution & Standards
*   [DEPENDENCIES.md](DEPENDENCIES.md): Framework Dependencies & Isolation Strategies

## License

[Insert License Information Here]
