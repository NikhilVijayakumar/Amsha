# Codebase Structure

**Analysis Date:** 2026-04-10

## Directory Layout

```
Amsha/
├── src/nikhil/amsha/          # Main library source
│   ├── crew_forge/            # Core CrewAI orchestration
│   ├── configuration/         # Config loading and validation
│   ├── llm_factory/           # LLM provider factory
│   ├── output_process/        # Output processing utilities
│   ├── crew_monitor/          # Performance monitoring
│   ├── execution_state/      # Execution state tracking
│   ├── execution_runtime/     # Runtime execution engine
│   ├── common/                # Shared utilities
│   └── utils/                 # General utilities
├── tests/                     # Test suite
├── example/                   # Example usage
├── config/                    # Configuration files
└── pyproject.toml            # Project metadata
```

## Directory Purposes

### src/nikhil/amsha/crew_forge/
- **Purpose:** Core library - CrewAI orchestration with Clean Architecture
- **Contains:**
  - `domain/` - Pure Pydantic models (no external deps)
  - `repo/interfaces/` - Repository abstractions (ABC)
  - `repo/adapters/` - Concrete implementations (MongoDB)
  - `service/` - Business logic services
  - `orchestrator/` - High-level orchestration
  - `protocols/` - External-facing Protocol definitions
  - `exceptions/` - Custom exception hierarchy
  - `dependency/` - DI container wiring
  - `knowledge/` - Knowledge source integrations
  - `seeding/` - Database seeding utilities
  - `sync/` - Configuration synchronization

**Key files:**
- `src/nikhil/amsha/crew_forge/__init__.py` - Empty (library exposes via submodules)
- `src/nikhil/amsha/crew_forge/service/atomic_db_builder.py` - DB-backed crew builder
- `src/nikhil/amsha/crew_forge/service/atomic_yaml_builder.py` - File-backed crew builder

### src/nikhil/amsha/configuration/
- **Purpose:** Configuration management with strict validation
- **Contains:**
  - `domain/models/` - Pydantic config models
  - `application/` - ConfigurationManager service
  - `infrastructure/` - Validators
  - `exceptions/` - Config-specific exceptions

**Key files:**
- `src/nikhil/amsha/configuration/application/configuration_manager.py` - YAML loading
- `src/nikhil/amsha/configuration/domain/models/amsha_app_config.py` - App config model
- `src/nikhil/amsha/configuration/domain/models/amsha_job_config.py` - Job config model

### src/nikhil/amsha/llm_factory/
- **Purpose:** Factory pattern for LLM provider instantiation
- **Contains:**
  - `domain/` - LLM type definitions
  - `dependency/` - LLM DI container
  - `adapters/` - Provider implementations (OpenAI, Anthropic, etc.)
  - `service/` - LLM builder services
  - `settings/` - LLM configuration

**Key files:**
- `src/nikhil/amsha/llm_factory/dependency/llm_container.py` - LLM DI setup
- `src/nikhil/amsha/llm_factory/domain/model/llm_type.py` - `LLMType` enum

### src/nikhil/amsha/output_process/
- **Purpose:** Output post-processing and validation
- **Contains:**
  - `optimization/` - JSON cleaning utilities
  - `validation/` - Output validators
  - `evaluation/` - Evaluation report tools

**Key files:**
- `src/nikhil/amsha/output_process/optimization/json_cleaner_utils.py` - JSON fixing
- `src/nikhil/amsha/output_process/validation/json_output_validator.py` - JSON validation

### src/nikhil/amsha/crew_monitor/
- **Purpose:** Performance monitoring and reporting
- **Contains:**
  - `service/` - Monitor implementations

### src/nikhil/amsha/execution_state/
- **Purpose:** Track crew execution state
- **Contains:**
  - `domain/` - State models and enums
  - `service/` - StateManager

### src/nikhil/amsha/execution_runtime/
- **Purpose:** Runtime execution management
- **Contains:**
  - `domain/` - ExecutionMode, ExecutionHandle
  - `service/` - RuntimeEngine

### src/nikhil/amsha/utils/
- **Purpose:** General utilities
- **Contains:**
  - `yaml_utils.py` - YAML helpers
  - `json_utils.py` - JSON helpers
  - `utf8_utils.py` - UTF-8 encoding helpers

### src/nikhil/amsha/common/
- **Purpose:** Common/shared code across modules

### src/nikhil/amsha/common/
- **Purpose:** Common utilities used across all modules

---

## Key File Locations

### Entry Points (Client-Facing)
- `src/nikhil/amsha/crew_forge/orchestrator/db/amsha_crew_db_application.py` - DB mode base class
- `src/nikhil/amsha/crew_forge/orchestrator/file/amsha_crew_file_application.py` - File mode base class

### Domain Models
- `src/nikhil/amsha/crew_forge/domain/models/agent_data.py` - `AgentRequest`, `AgentResponse`
- `src/nikhil/amsha/crew_forge/domain/models/task_data.py` - `TaskRequest`
- `src/nikhil/amsha/crew_forge/domain/models/crew_data.py` - `CrewData`

### Repository Interfaces
- `src/nikhil/amsha/crew_forge/repo/interfaces/i_agent_repository.py` - `IAgentRepository`
- `src/nikhil/amsha/crew_forge/repo/interfaces/i_task_repository.py` - `ITaskRepository`
- `src/nikhil/amsha/crew_forge/repo/interfaces/i_crew_config_repository.py` - `ICrewConfigRepository`

### Repository Implementations
- `src/nikhil/amsha/crew_forge/repo/adapters/mongo/agent_repo.py` - MongoDB agent repository
- `src/nikhil/amsha/crew_forge/repo/adapters/mongo/task_repo.py` - MongoDB task repository
- `src/nikhil/amsha/crew_forge/repo/adapters/mongo/mongo_repository.py` - Base MongoDB operations

### Services
- `src/nikhil/amsha/crew_forge/service/atomic_db_builder.py` - DB crew builder
- `src/nikhil/amsha/crew_forge/service/atomic_yaml_builder.py` - File crew builder
- `src/nikhil/amsha/crew_forge/service/crew_builder_service.py` - Core crew assembly

### DI Containers
- `src/nikhil/amsha/crew_forge/dependency/crew_forge_container.py` - Main container
- `src/nikhil/amsha/crew_forge/dependency/mongo_container.py` - MongoDB container

### Protocols
- `src/nikhil/amsha/crew_forge/protocols/crew_manager.py` - `CrewManager` Protocol
- `src/nikhil/amsha/crew_forge/protocols/crew_application.py` - Application Protocols

### Exceptions
- `src/nikhil/amsha/crew_forge/exceptions/__init__.py` - Exception exports
- `src/nikhil/amsha/crew_forge/exceptions/crew_forge_exception.py` - Base exception
- `src/nikhil/amsha/crew_forge/exceptions/crew_configuration_exception.py` - Config errors
- `src/nikhil/amsha/crew_forge/exceptions/crew_execution_exception.py` - Execution errors

---

## Naming Conventions

**Files:**
- Models: `*_data.py` (e.g., `agent_data.py`, `task_data.py`)
- Interfaces: `i_*.py` (e.g., `i_agent_repository.py`)
- Services: `*_service.py` or `*_builder.py` (e.g., `atomic_db_builder.py`)
- Exceptions: `*_exception.py` (e.g., `crew_forge_exception.py`)
- Utils: `*_utils.py` (e.g., `yaml_utils.py`, `json_utils.py`)

**Directories:**
- Domain layer: `domain/`
- Repository interfaces: `repo/interfaces/`
- Repository implementations: `repo/adapters/[backend]/`
- Services: `service/`
- Orchestrators: `orchestrator/[mode]/`
- Protocols: `protocols/`
- Exceptions: `exceptions/`
- Configuration: `application/`, `domain/`, `infrastructure/`

**Classes:**
- Interface: Prefix with `I` (e.g., `IAgentRepository`)
- Protocol: Suffix with `Protocol` (e.g., `CrewManager(Protocol)`)
- Exception: Suffix with `Exception` (e.g., `CrewForgeException`)
- Builder: Suffix with `Builder` or `Service` (e.g., `AtomicDbBuilderService`)

---

## Where to Add New Code

### New Feature (CrewAI-related)
- Primary code: `src/nikhil/amsha/crew_forge/service/`
- Domain models: `src/nikhil/amsha/crew_forge/domain/models/`
- Tests: `tests/`
- Configuration: `config/`

### New Repository Implementation
- Interface: `src/nikhil/amsha/crew_forge/repo/interfaces/`
- Implementation: `src/nikhil/amsha/crew_forge/repo/adapters/[backend]/`

### New LLM Provider
- Adapter: `src/nikhil/amsha/llm_factory/adapters/`
- Settings: `src/nikhil/amsha/llm_factory/settings/`

### New Output Processor
- Implementation: `src/nikhil/amsha/output_process/[category]/`

### New Utility
- Shared: `src/nikhil/amsha/utils/`
- Module-specific: Add to module's `utils/` subdirectory

---

## Where NOT to Add Code

**Anti-patterns to avoid:**
- ❌ Domain models importing from `repo/adapters/` - violates Clean Architecture
- ❌ Services instantiating repositories directly (`self.repo = AgentRepository()`) - violates DI
- ❌ Protocol definitions for DTOs - use Pydantic models
- ❌ Hardcoded logic in services - use configuration-driven behavior
- ❌ Generic exceptions (`ValueError`, `Exception`) - use custom exception hierarchy

---

## Special Directories

### tests/
- **Purpose:** Unit and integration tests
- **Structure:** Mirrors `src/` structure
- **Committed:** Yes
- **Generated:** No

### config/
- **Purpose:** Configuration YAML files
- **Committed:** Yes (example configs)
- **Note:** Never commit files with secrets - use `.env.example`

### example/
- **Purpose:** Example usage demonstrating library capabilities
- **Committed:** Yes
- **Generated:** No
- **Note:** Must be runnable and tested

---

*Structure analysis: 2026-04-10*