# CrewAI MongoDB Configuration Library Documentation

This document provides comprehensive documentation for a Python library designed to manage **CrewAI configurations** (Agents, Tasks, and Crews) using **MongoDB as persistent storage**, offering an alternative to traditional YAML file-based configurations.

---

## 1. Project Overview

This library streamlines the management of **CrewAI components** by persisting their definitions in a MongoDB database. It provides robust tools to define **LLM configurations**, **agents**, **tasks**, and **crew configurations** using a structured, database-driven approach while supporting initial setup via YAML files.

### Key Features:
- **MongoDB Persistence**: Store agent/task definitions in MongoDB for dynamic retrieval.
- **YAML as Initial Config**: Use YAML files for initial configuration of LLMs and optional agent/task definitions.
- **Dynamic Crew Assembly**: Retrieve agent/task definitions from MongoDB to dynamically construct and run CrewAI processes.
- **Scalability & Flexibility**: Enables scalable development environments with easy updates and modifications.

---

## 2. Key Concepts and Data Flow

### Core Concepts:

#### 📄 YAML as Initial Configuration
YAML files are used to:
1. Define LLM settings (e.g., `llm_config.yaml`).
2. Optionally define agents/tasks before they are persisted in MongoDB.

#### 🔐 Pydantic Models for Data Validation
All data structures use **Pydantic BaseModel** classes to ensure type safety and data integrity.

#### 🧱 MongoDB for Persistence
Repository classes handle CRUD operations:
- `AgentRepository`: For agent configurations.
- `TaskRepository`: For task configurations.
- `CrewConfigRepository`: For crew definitions linking agents/tasks by ID.

#### 💡 Dynamic Crew Assembly
The `CreateCrew` class dynamically retrieves agent/task definitions from MongoDB and assembles them into executable **CrewAI Agent**, **Task**, and **Crew** objects.

### Typical Data Flow:
1. Load LLM configurations from a YAML file.
2. Parse agent/task definitions (optional) from YAML files.
3. Persist these definitions in MongoDB using repositories.
4. Retrieve agent/task definitions from MongoDB to dynamically construct and run CrewAI processes.

---

## 3. Installation and Setup

### 📦 Dependencies
Install the following libraries via pip:

```bash
pip install pymongo pyyaml pydantic crewai crewai_tools python-dotenv
```

### 🔐 MongoDB Configuration
Provide connection details using the `RepoData` model:
- `mongo_uri`: MongoDB connection string (e.g., `mongodb://localhost:27017/`).
- `db_name`: Database name (e.g., `"crewai_configs"`).
- `collection_name`: Collection name (e.g., `"agents"`, `"tasks"`, `"crew_configs"`).

---

## 4. Data Models

The library uses **Pydantic BaseModel** classes to define and validate data structures.

### 🧑‍💼 4.1 Agent Models

#### `AgentRequest`
Represents the structure for creating/updating an agent.

```python
class AgentRequest(BaseModel):
    role: str = Field(..., description="The role or persona of the agent.")
    goal: str = Field(..., description="The primary objective or goal of the agent.")
    backstory: str = Field(..., description="The backstory or context for the agent.")
    usecase: Optional[str] = Field(None, description="Use case for the agent.")
```

#### `AgentResponse`
Represents an agent retrieved from MongoDB (includes MongoDB `_id`).

```python
class AgentResponse(BaseModel):
    id: Optional[str] = Field(None, alias="_id", description="MongoDB document ID")
    role: str = Field(..., description="The role or persona of the agent.")
    goal: str = Field(..., description="The primary objective or goal of the agent.")
    backstory: str = Field(..., description="The backstory or context for the agent.")
    usecase: Optional[str] = Field(None, description="Use case for the agent.")
```

---

### 🧩 4.2 Task Models

#### `TaskRequest`
Represents the structure for creating/updating a task.

```python
class TaskRequest(BaseModel):
    name: str = Field(..., description="The name of the task.")
    description: str = Field(..., description="Description of the task to be performed.")
    expected_output: str = Field(..., description="Expected output or result of the task.")
    usecase: Optional[str] = Field(None, description="Use case for the task.")
```

#### `TaskResponse`
Represents a task retrieved from MongoDB (includes `_id`).

```python
class TaskResponse(BaseModel):
    id: Optional[str] = Field(None, alias="_id", description="MongoDB document ID")
    name: str = Field(..., description="The name of the task.")
    description: str = Field(..., description="Description of the task to be performed.")
    expected_output: str = Field(..., description="Expected output or result of the task.")
    usecase: Optional[str] = Field(None, description="Use case for the task.")
```

---

### 🧑‍🤝‍🧑 4.3 Crew Configuration Models

#### `CrewConfigRequest`
Represents the structure for defining a **CrewAI crew**, linking agents/tasks by ID.

```python
class CrewConfigRequest(BaseModel):
    name: str = Field(..., description="The name of the crew.")
    agents: dict[str, str] = Field(..., description="Dictionary of agent names to their IDs")
    tasks: dict[str, str] = Field(..., description="Dictionary of task names to their IDs")
    usecase: Optional[str] = Field(None, description="Use case for the crew.")
```

#### `CrewConfigResponse`
Represents a crew configuration retrieved from MongoDB (includes `_id`).

```python
class CrewConfigResponse(BaseModel):
    id: Optional[str] = Field(None, alias="_id", description="MongoDB document ID")
    name: str = Field(..., description="The name of the crew.")
    agents: dict[str, str] = Field(..., description="Dictionary of agent names to their IDs")
    tasks: dict[str, str] = Field(..., description="Dictionary of task names to their IDs")
    usecase: Optional[str] = Field(None, description="Use case for the crew.")
```

---

### 🗄️ 4.4 Repository and Crew Data Models

#### `RepoData`
Defines connection parameters for MongoDB repositories.

```python
class RepoData(BaseModel):
    mongo_uri: str = Field(..., description="Mongo DB URI")
    db_name: str = Field(..., description="The name of the database")
    collection_name: str = Field(..., description="The name of the collection")
```

#### `CrewData`
Aggregates components to instantiate and run a **CrewAI Crew**.

```python
class CrewData(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    llm: LLM = Field(..., description="LLM model name")
    module_name: str = Field(..., description="The name of the module")
    agent_repo: AgentRepository = Field(..., description="Agent repository")
    task_repo: TaskRepository = Field(..., description="Task repository")
    output_dir_path: str = Field(..., description="Output directory path")
```

---

## 5. Configuration Parsing Utilities (YamlUtils, LLMConfig)

### 📁 5.1 YamlUtils

A utility class for loading and parsing YAML files.

#### Methods:
- `clean_multiline_string(text: str) -> str`: Cleans multiline strings by replacing newlines/tabs with spaces.
- `yaml_safe_load(config_file_path: str)`: Safely loads YAML content from a file path.
- `parse_agent(agent_yaml_file: str) -> AgentRequest`: Parses an agent definition from a YAML file.

#### Example `agent.yaml`:
```yaml
agent:
  role: "Persona Refiner"
  goal: |
          1. Receive a CrewAI agent definition in YAML format.
          2. Analyze the agent's current role, goals, and backstory for clarity and alignment.
          3. Enhance the agent's role to be more descriptive and focused.
          4. Refine the agent's goals to be specific, measurable, achievable, relevant, and time-bound (SMART-like).
          5. Condense and strengthen the agent's backstory to be concise and purposeful, adding voice or tone where beneficial.
          6. Output the improved agent definition in YAML format.
  backstory: |
                You are a master of crafting compelling and effective agent personas. You have a talent for taking raw agent definitions and polishing them into clear, focused, and engaging entities that seamlessly integrate into collaborative AI systems. Your expertise lies in distilling the essence of an agent's function into a concise narrative.
```

#### Example `task.yaml`:
```yaml
task:
  name: "Refine Agent Persona"
  description: |
                  Improve the persona of a given CrewAI agent to better align with modular design and clarity. This involves enhancing the agent's role, goals, and backstory for improved understanding and focus. Clarity, voice, and tone will be considered, and the backstory will be made concise yet purposeful.

                  Input:
                  - Agent Definition (YAML): {agent_yaml} (A YAML string containing the agent's role, goals, and backstory)

                  Steps:
                  1. Load and parse the `agent_yaml` to access the agent's `role`, `goal`, and `backstory`.
                  2. Review the existing `role` for clarity and conciseness, ensuring it clearly defines the agent's function.
                  3. Examine the `goal` statements for specificity and actionability, ensuring they directly support the agent's role.
                  4. Refine the `backstory` to be concise but purposeful, providing context and motivation without unnecessary detail. Consider adding a distinct voice or tone if it enhances the agent's persona and clarity.
                  5. Update the `role`, `goal`, and `backstory` as needed to improve modularity, clarity, and narrative.
                  6. Output the improved agent definition as a YAML string.

  expected_output: |
                      A YAML string representing the refined CrewAI agent definition, with an improved role, clearer and more focused goals, and a concise yet purposeful backstory.
```

#### `parse_task(task_yaml_file: str) -> TaskRequest`: Parses a task from YAML.

---

### 🧠 5.2 LLMConfig

Manages loading and instantiating **LLM models** from a YAML configuration using `YamlUtils`.

#### Example `llm_config.yaml`:
```yaml
llm:
  creative:
    default: phi
    models:
      phi:
        base_url: "http://localhost:1234/v1"
        model: "lm_studio/phi-4"
        api_key: "your_api_key"
      llama:
        base_url: "http://localhost:1234/v1"
        model: "lm_studio/meta-llama-3.1-8b-instruct"
        api_key: ""
  evaluation:
    default: gemma
    models:
      gemma:
        base_url: "http://localhost:1234/v1"
        model: "lm_studio/gemma-3-12b-it"
        api_key: ""
      qwen:
        base_url: "http://localhost:1234/v1"
        model: "lm_studio/gemma-3-12b-it"
        api_key: "xxxx"

llm_parameters:
  creative:
    temperature: 0.8
    top_p: 0.9
    max_completion_tokens: 8192
    presence_penalty: 0.6
    frequency_penalty: 0.4
    stop: ["###"]
  evaluation:
    temperature: 0.0
    top_p: 0.5
    presence_penalty: 0.0
    frequency_penalty: 0.0
    stop: ["###"]
```

---

## 6. MongoDB Repositories

Repository classes abstract interactions with MongoDB.

### 📁 6.1 BaseRepository (Base Class)

Provides common MongoDB CRUD operations:
- `find_one(query)`
- `find_many(query)`
- `insert_one(data)`
- `insert_many(data)`
- `update_one(query, data)`
- `delete_one(query)`
- `create_unique_compound_index(keys)`

### 🧑‍💼 6.2 AgentRepository

Manages agent configurations:
- `create_agent(agent: AgentRequest)` → `AgentResponse`
- `get_agent_by_id(agent_id)`
- `update_agent(agent_id, agent)`
- `delete_agent(agent_id)`
- `get_agents_by_usecase(usecase)`

### 🧩 6.3 TaskRepository

Manages task configurations:
- `create_task(task: TaskRequest)` → `TaskResponse`
- `get_task_by_id(task_id)`
- `update_task(task_id, task)`
- `delete_task(task_id)`
- `get_tasks_by_usecase(usecase)`

### 🧑‍🤝‍🧑 6.4 CrewConfigRepository

Manages crew configurations:
- Auto-creates a unique compound index on `(name, usecase)`.
- `create_crew_config(crew_config: CrewConfigRequest)` → `CrewConfigResponse`
- `get_crew_config_by_id(crew_config_id)`
- `update_crew_config(crew_config_id, crew_config)`
- `delete_crew_config(crew_config_id)`
- `get_crew_configs_by_usecase(usecase)`
- `get_crew_by_name_and_usecase(name, usecase)`

---

## 7. Crew Creation (`CreateCrew`)

The class orchestrates dynamic assembly of **CrewAI agents**, **tasks**, and **crews** from stored configurations.

### Methods:
- `__init__(data: CrewData)`
- `create_output_dir()`: Creates a timestamped output directory.
- `get_output_dir()` → `str`
- `crew_with_knowledge(process=Process.sequential, knowledge_sources=None)` → `Crew`
- `get_agent(agent_id: str)` → `AgentResponse`
- `get_task(task_id: str)` → `TaskResponse`
- `create_agent(agent_id: str, knowledge_sources=None, tools=None)` → `Agent`
- `create_task(task_id: str, agent: Agent, save=True, filename=None)` → `Task`
- `load_json(file_name)`: Loads JSON content from a file.

---

## 8. Usage Examples

### 🧪 8.1 Initializing LLM Configuration

```python
from your_library.llm_config import LLMConfig
from your_library.utils import YamlUtils

llm_config_path = "llm_config.yaml"
llm_config_manager = LLMConfig(llm_config_path)

# Create a creative LLM instance
creative_llm = llm_config_manager.create_creative_instance(model_key="llama")
print(f"Creative LLM Model: {llm_config_manager.model_name}")

# Create an evaluation LLM instance (disables telemetry)
evaluation_llm = llm_config_manager.create_evaluation_instance()
print(f"Evaluation LLM Model: {llm_config_manager.model_name}")
```

### 🏗️ 8.2 Setting Up Repositories

```python
from your_library.models import RepoData
from your_library.repositories import AgentRepository, TaskRepository, CrewConfigRepository

mongo_uri = "mongodb://localhost:27017/"
db_name = "crewai_db"

agent_repo_data = RepoData(mongo_uri=mongo_uri, db_name=db_name, collection_name="agents")
task_repo_data = RepoData(mongo_uri=mongo_uri, db_name=db_name, collection_name="tasks")
crew_config_repo_data = RepoData(mongo_uri=mongo_uri, db_name=db_name, collection_name="crew_configs")

agent_repo = AgentRepository(agent_repo_data)
task_repo = TaskRepository(task_repo_data)
crew_config_repo = CrewConfigRepository(crew_config_repo_data)

print("MongoDB Repositories initialized.")
```

### 🧑‍💻 8.3 Creating Agents/Tasks in MongoDB

```python
from your_library.models import AgentRequest, TaskRequest
from your_library.utils import YamlUtils

yaml_utils = YamlUtils()
agent_request = yaml_utils.parse_agent("agent.yaml")
agent_request.usecase = "content_creation"

created_agent_response = agent_repo.create_agent(agent_request)
if created_agent_response:
    print(f"Created Agent in DB: {created_agent_response.id} - {created_agent_response.role}")
```

### 🧑‍🤝‍🧑 8.4 Creating Crew Configurations

```python
from your_library.models import CrewConfigRequest

crew_config_request = CrewConfigRequest(
    name="Content Generation Crew",
    agents={"Persona Refiner": created_agent_response.id},
    tasks={"Refine Agent Persona": created_task_response.id},
    usecase="content_creation"
)

created_crew_config = crew_config_repo.create_crew_config(crew_config_request)
if created_crew_config:
    print(f"Created Crew Config: {created_crew_config.name}")
```

### 🚀 8.5 Assembling and Running a Crew

```python
from your_library.models import CrewData
from your_library.crew_creator import CreateCrew
from crewai import Process

crew_data = CrewData(
    llm=creative_llm,
    agent_repo=agent_repo,
    task_repo=task_repo,
    output_dir_path="./crew_outputs",
    module_name="my_first_crew"
)

crew_creator = CreateCrew(crew_data)
persona_refiner_agent = crew_creator.create_agent(created_agent_response.id)

crew_creator.create_task(
    task_id=created_task_response.id,
    agent=persona_refiner_agent,
    save=True,
    filename="refined_persona_output"
)

my_crew = crew_creator.crew_with_knowledge(process=Process.sequential)

inputs = {
    "agent_yaml": """
    agent:
      role: "Draft Persona"
      goal: "Draft a basic agent persona."
      backstory: "A simple agent without much refinement."
    """
}

result = my_crew.kickoff(inputs=inputs)
print("\n\n## Crew Work Results:")
print(result)

output_file_path = os.path.join(crew_creator.get_output_dir(), "refined_persona_output.json")
if os.path.exists(output_file_path):
    print(f"\nTask output saved to: {output_file_path}")
```

---

## 9. Error Handling

- **`ValueError`**: Raised for invalid `ObjectId` formats.
- **`DuplicateKeyError`** (from `pymongo.errors`): Raised when inserting documents with duplicate unique keys.

Example:
```python
try:
    agent_repo.create_agent(agent_request)
except ValueError as e:
    print(f"Invalid input: {e}")
except DuplicateKeyError:
    print("Agent already exists with this ID.")
```

---

## 10. Conclusion

This library provides a **scalable and flexible** way to manage CrewAI configurations using MongoDB, enabling dynamic agent/task creation, retrieval, and execution. It supports both initial YAML setup and real-time modifications via database operations.