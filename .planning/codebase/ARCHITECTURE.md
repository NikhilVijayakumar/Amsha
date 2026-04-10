# Architecture

**Analysis Date:** 2026-04-10

## Pattern Overview

**Overall:** Clean Architecture with Ports and Adapters pattern

This project follows **Clean Architecture** with strict adherence to the Dependency Rule. The codebase is organized to ensure inner layers (Domain) never depend on outer layers (Infrastructure/API), enabling testability, flexibility, and maintainability across multiple dependent projects.

**Key Characteristics:**
- **Dependency Rule:** Domain (inner) → Service/Application → Orchestrator → Infrastructure (outer)
- **Interface Segregation:** `ABC` for internal repository contracts, `Protocol` for external client boundaries
- **Dependency Injection:** All complex dependencies injected via constructors; wiring in containers
- **Dual-Mode Orchestration:** Database-backed and File-backed execution modes with identical interfaces

## Layers

### Domain Layer (innermost)
- **Purpose:** Pure Python data models and enums - no external framework dependencies
- **Location:** `src/nikhil/amsha/crew_forge/domain/`, `src/nikhil/amsha/*/domain/`
- **Contains:** Pydantic `BaseModel` classes (`AgentRequest`, `AgentResponse`, `TaskRequest`, `CrewData`)
- **Depends on:** Nothing (pure domain)
- **Used by:** All outer layers

**Example files:**
- `src/nikhil/amsha/crew_forge/domain/models/agent_data.py` - `AgentRequest`, `AgentResponse`
- `src/nikhil/amsha/crew_forge/domain/models/task_data.py` - `TaskRequest`
- `src/nikhil/amsha/crew_forge/domain/models/crew_data.py` - `CrewData`

### Repository Interfaces (Abstraction Layer)
- **Purpose:** Abstract contracts defining data access operations
- **Location:** `src/nikhil/amsha/crew_forge/repo/interfaces/`
- **Contains:** `ABC`-based interfaces (`IAgentRepository`, `ITaskRepository`, `ICrewConfigRepository`)
- **Depends on:** Domain models only
- **Used by:** Service/application layer

**Example files:**
- `src/nikhil/amsha/crew_forge/repo/interfaces/i_agent_repository.py`
- `src/nikhil/amsha/crew_forge/repo/interfaces/i_task_repository.py`

```python
# Interface pattern from i_agent_repository.py
class IAgentRepository(ABC):
    @abstractmethod
    def get_agent_by_id(self, agent_id: str) -> Optional[AgentResponse]:
        ...
    
    @abstractmethod
    def create_agent(self, agent: AgentRequest) -> AgentResponse:
        ...
```

### Service/Application Layer (Business Logic)
- **Purpose:** Orchestrates business logic, builds CrewAI crews
- **Location:** `src/nikhil/amsha/crew_forge/service/`
- **Contains:** Builder services, orchestrator base classes
- **Depends on:** Domain models and repository interfaces (never implementations)
- **Used by:** Orchestrator layer

**Example files:**
- `src/nikhil/amsha/crew_forge/service/atomic_db_builder.py` - Builds crews from MongoDB
- `src/nikhil/amsha/crew_forge/service/crew_builder_service.py` - Core crew assembly
- `src/nikhil/amsha/crew_forge/service/base_crew_orchestrator.py` - Execution orchestration base

```python
# Service with DI pattern from atomic_db_builder.py
class AtomicDbBuilderService:
    def __init__(self, data: CrewData, agent_repo: IAgentRepository, task_repo: ITaskRepository):
        self.agent_repo: IAgentRepository = agent_repo  # Injected, not instantiated
        self.task_repo: ITaskRepository = task_repo
        self.builder: CrewBuilderService = CrewBuilderService(data)
```

### Orchestrator Layer (Entry Points)
- **Purpose:** High-level orchestration and execution control
- **Location:** `src/nikhil/amsha/crew_forge/orchestrator/`
- **Contains:** `DbCrewOrchestrator`, `FileCrewOrchestrator`, application base classes
- **Depends on:** Service layer, Protocol interfaces
- **Used by:** Client applications

**Example files:**
- `src/nikhil/amsha/crew_forge/orchestrator/db/db_crew_orchestrator.py`
- `src/nikhil/amsha/crew_forge/orchestrator/db/amsha_crew_db_application.py`
- `src/nikhil/amsha/crew_forge/orchestrator/file/amsha_crew_file_application.py`

### Infrastructure Layer (outermost)
- **Purpose:** Concrete implementations - MongoDB adapters, external integrations
- **Location:** `src/nikhil/amsha/crew_forge/repo/adapters/mongo/`
- **Contains:** Repository implementations, database clients
- **Depends on:** Interface contracts, domain models

**Example files:**
- `src/nikhil/amsha/crew_forge/repo/adapters/mongo/agent_repo.py` - `AgentRepository(MongoRepository, IAgentRepository)`
- `src/nikhil/amsha/crew_forge/repo/adapters/mongo/mongo_repository.py` - Base MongoDB operations

## Data Flow

**DB-Backed Crew Execution:**

1. `AmshaCrewDBApplication.__init__()` loads YAML configs
2. `_initialize_llm()` creates LLM via `LLMContainer`
3. `AtomicCrewDBManager` receives LLM and job config
4. `AtomicDbBuilderService` fetches agents/tasks from `IAgentRepository`, `ITaskRepository`
5. `CrewBuilderService` assembles CrewAI `Crew` with agents and tasks
6. `DbCrewOrchestrator.run_crew()` executes the crew

**File-Backed Crew Execution:**

1. `AmshaCrewFileApplication.__init__()` loads YAML configs
2. YAML configs parsed by `CrewParser` instead of repository
3. `AtomicYamlBuilderService` reads agent/task configs from YAML files
4. Assembly and execution follow same path as DB mode

## Key Abstractions

### Protocol for External Boundaries
- **Purpose:** Client-facing interfaces with structural typing
- **Location:** `src/nikhil/amsha/crew_forge/protocols/`
- **Pattern:** `Protocol` with `@runtime_checkable`

**Files:**
- `src/nikhil/amsha/crew_forge/protocols/crew_manager.py` - `CrewManager` Protocol
- `src/nikhil/amsha/crew_forge/protocols/crew_application.py` - Application Protocols

```python
# Protocol pattern from crew_manager.py
@runtime_checkable
class CrewManager(Protocol):
    def build_atomic_crew(self, crew_name: str, filename_suffix: Optional[str] = None, output_json: Any = None) -> Crew:
        ...
    
    @property
    def model_name(self) -> str:
        ...
```

### ABC for Internal Contracts
- **Purpose:** Repository interfaces requiring runtime enforcement
- **Pattern:** `ABC` with `@abstractmethod`

### Dependency Injection Container
- **Purpose:** Wire all dependencies centrally
- **Location:** `src/nikhil/amsha/crew_forge/dependency/`
- **Pattern:** `dependency-injector` library with `DeclarativeContainer`

**Files:**
- `src/nikhil/amsha/crew_forge/dependency/crew_forge_container.py` - Main container
- `src/nikhil/amsha/crew_forge/dependency/mongo_container.py` - MongoDB container

```python
# DI container pattern from crew_forge_container.py
class CrewForgeContainer(containers.DeclarativeContainer):
    agent_repo = mongo_container.provided.agent_repo
    
    atomic_db_builder = providers.Factory(
        AtomicDbBuilderService,
        agent_repo=agent_repo(),
        task_repo=task_repo(),
        data=providers.Factory(CrewData)
    )
```

## Entry Points

**DB-Backed Application:**
- Location: `src/nikhil/amsha/crew_forge/orchestrator/db/amsha_crew_db_application.py`
- Class: `AmshaCrewDBApplication`
- Responsibilities: Load configs, initialize LLM, create manager, provide `clean_json()` utility

**File-Backed Application:**
- Location: `src/nikhil/amsha/crew_forge/orchestrator/file/amsha_crew_file_application.py`
- Class: `AmshaCrewFileApplication`
- Responsibilities: Same as DB mode, but parses YAML configs instead of database

## Error Handling

**Strategy:** Custom exception hierarchy per AGENTS.md Section 5

**Patterns:**
1. **Base Exception:** `CrewForgeException` in `src/nikhil/amsha/crew_forge/exceptions/`
2. **Specific Exceptions:** `CrewConfigurationException`, `CrewExecutionException`, `CrewManagerException`, `InputPreparationException`
3. **Error Context:** `ErrorContext` and `ErrorMessageBuilder` for structured error handling

**Files:**
- `src/nikhil/amsha/crew_forge/exceptions/__init__.py` - Exception exports
- `src/nikhil/amsha/crew_forge/exceptions/crew_forge_exception.py` - Base exception
- `src/nikhil/amsha/crew_forge/exceptions/crew_configuration_exception.py` - Config errors

## Cross-Cutting Concerns

**Configuration Management:**
- Location: `src/nikhil/amsha/configuration/`
- Pattern: YAML-based config with strict validation via Pydantic
- Classes: `ConfigurationManager`, domain config models (`AmshaAppConfig`, `AmshaJobConfig`, `AmshaLLMConfig`)

**LLM Factory:**
- Location: `src/nikhil/amsha/llm_factory/`
- Pattern: Factory pattern for flexible LLM provider instantiation
- Supports: `LLMType.CREATIVE` and `LLMType.EVALUATION`

**Output Processing:**
- Location: `src/nikhil/amsha/output_process/`
- Contains: JSON cleaning, validation, evaluation tools

---

*Architecture analysis: 2026-04-10*