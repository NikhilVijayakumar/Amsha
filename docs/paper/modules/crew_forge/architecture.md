# Crew Forge: Architecture & Design

## 1. Architectural Overview

The `crew_forge` module implements a **four-layer Clean Architecture** for AI Agent orchestration, extending beyond simple Crew construction to encompass configuration management, multi-format knowledge ingestion, and dual-backend persistence. With **56 Python files** across **12 sub-packages**, it is the largest and most structurally mature module in the Amsha framework.

### Layered Architecture Diagram

```mermaid
%%{init: {'theme': 'base'}}%%
flowchart TD
    classDef app fill:#ffd700,stroke:#333,stroke-width:2px;
    classDef orch fill:#ff9f43,stroke:#333,stroke-width:2px;
    classDef service fill:#bbf,stroke:#333,stroke-width:2px;
    classDef domain fill:#f9f,stroke:#333,stroke-width:2px;
    classDef infra fill:#bfb,stroke:#333,stroke-width:2px;

    subgraph "Application Layer"
        DBApp["AmshaCrewDBApplication"]:::app
        FileApp["AmshaCrewFileApplication"]:::app
    end

    subgraph "Orchestrator Layer"
        DbOrch["DbCrewOrchestrator"]:::orch
        FileOrch["FileCrewOrchestrator"]:::orch
        DBMgr["AtomicCrewDBManager"]:::orch
        FileMgr["AtomicCrewFileManager"]:::orch
    end

    subgraph "Service Layer"
        CBS["CrewBuilderService"]:::service
        ADB["AtomicDbBuilderService"]:::service
        AYB["AtomicYamlBuilderService"]:::service
        BPS["CrewBluePrintService"]:::service
        CSS["ConfigSyncService"]:::service
        Seeder["DatabaseSeeder"]:::service
    end

    subgraph "Domain Layer"
        Models["Pydantic Models"]:::domain
        Interfaces["ABC Interfaces"]:::domain
        Enums["RepoBackend Enum"]:::domain
    end

    subgraph "Infrastructure Layer"
        Mongo["MongoRepository"]:::infra
        AgentRepo["AgentRepository"]:::infra
        TaskRepo["TaskRepository"]:::infra
        CrewRepo["CrewConfigRepository"]:::infra
        Parser["CrewParser"]:::infra
        Knowledge["AmshaCrewDoclingSource"]:::infra
        DI["CrewForgeContainer"]:::infra
        MongoDI["MongoRepoContainer"]:::infra
    end

    DBApp --> DbOrch
    FileApp --> FileOrch
    DbOrch --> DBMgr
    FileOrch --> FileMgr
    DBMgr --> ADB
    FileMgr --> AYB
    ADB --> CBS
    AYB --> CBS
    ADB --> Interfaces
    AYB --> Parser
    DBMgr --> BPS
    CSS --> Seeder
    Seeder --> Parser
    Seeder --> Interfaces
    AgentRepo --> Mongo
    TaskRepo --> Mongo
    CrewRepo --> Mongo
    Mongo --> Interfaces
    DI --> MongoDI
    DBMgr --> Knowledge
    FileMgr --> Knowledge
```

---

## 2. Sub-Package Structure

| Sub-Package | Files | Purpose |
|:---|:---:|:---|
| `domain/models/` | 6 | Pydantic data models (`AgentRequest/Response`, `TaskRequest/Response`, `CrewData`, `CrewConfigData`, `RepoData`, `SyncConfig`) |
| `domain/enum/` | 1 | `RepoBackend` enum (`MONGO`, `IN_MEMORY`, `COSMOS`) |
| `repo/interfaces/` | 4 | ABC interfaces (`IRepository`, `IAgentRepository`, `ITaskRepository`, `ICrewConfigRepository`) |
| `repo/adapters/mongo/` | 4 | MongoDB implementations with compound index enforcement |
| `service/` | 5 | Business logic layer (Builder, Facades, Blueprint, ConfigSync) |
| `orchestrator/db/` | 3 | DB-backed crew lifecycle management |
| `orchestrator/file/` | 3 | File-backed crew lifecycle management |
| `seeding/` | 2 | YAML→DB synchronization with idempotent upsert |
| `knowledge/` | 1 | Multi-format document ingestion via Docling |
| `dependency/` | 2 | DI containers (declarative, hierarchical) |
| `sync/` | 1 | Crew config export to JSON |
| `exceptions/` | 4 | Typed exception hierarchy |

---

## 3. Class Design: Builder Pattern Hierarchy

### Class Diagram

```mermaid
%%{init: {'theme': 'base'}}%%
classDiagram
    note "Dual-backend crew construction with shared core builder"

    class CrewBuilderService {
        -_agents: List~Agent~
        -_tasks: List~Task~
        -output_files: List~str~
        -llm: LLM
        -module_name: str
        +add_agent(AgentRequest, knowledge, tools) self
        +add_task(TaskRequest, Agent, filename, validation) self
        +build(Process, knowledge) Crew
        +get_last_agent() Agent
        +get_last_file() str
    }

    class AtomicDbBuilderService {
        -builder: CrewBuilderService
        -agent_repo: IAgentRepository
        -task_repo: ITaskRepository
        +add_agent(agent_id, knowledge, tools)
        +add_task(task_id, Agent, filename, validation)
        +build(Process, knowledge) Crew
    }

    class AtomicYamlBuilderService {
        -builder: CrewBuilderService
        -parser: CrewParser
        -agent_yaml_file: str
        -task_yaml_file: str
        +add_agent(knowledge, tools)
        +add_task(Agent, filename, validation)
        +build(Process, knowledge) Crew
    }

    class IAgentRepository {
        <<interface>>
        +create_agent(AgentRequest)*
        +get_agent_by_id(id)*
        +find_by_role_and_usecase(role, usecase)*
        +update_agent(id, AgentRequest)*
        +delete_agent(id)*
        +get_agents_by_usecase(usecase)*
    }

    class ITaskRepository {
        <<interface>>
        +create_task(TaskRequest)*
        +get_task_by_id(id)*
        +find_by_name_and_usecase(name, usecase)*
        +update_task(id, TaskRequest)*
        +delete_task(id)*
        +get_tasks_by_usecase(usecase)*
    }

    class MongoRepository {
        -client: MongoClient
        -db: Database
        -collection: Collection
        +find_one(query)
        +find_many(query)
        +insert_one(data)
        +update_one(query, data)
        +delete_one(query)
        +create_unique_compound_index(keys)
    }

    class AgentRepository {
        +create_agent(AgentRequest)
        +get_agent_by_id(id)
        +find_by_role_and_usecase(role, usecase)
    }

    AtomicDbBuilderService --> CrewBuilderService : delegates
    AtomicYamlBuilderService --> CrewBuilderService : delegates
    AtomicDbBuilderService --> IAgentRepository : depends
    AtomicDbBuilderService --> ITaskRepository : depends
    IAgentRepository <|.. AgentRepository : implements
    MongoRepository <|-- AgentRepository : extends
```

---

## 4. Orchestrator Layer: Dual-Backend Crew Lifecycle

The orchestrator layer provides the complete crew execution lifecycle: initialization → blueprint loading → crew building → execution with monitoring → result extraction.

### Sequence Diagram: DB-Backed Full Lifecycle

```mermaid
%%{init: {'theme': 'base'}}%%
sequenceDiagram
    autonumber
    actor Client as Client Application
    participant App as AmshaCrewDBApplication
    participant LLM as LLMContainer
    participant Mgr as AtomicCrewDBManager
    participant BP as CrewBluePrintService
    participant Orch as DbCrewOrchestrator
    participant Builder as AtomicDbBuilderService
    participant Repo as AgentRepository
    participant Core as CrewBuilderService
    participant Monitor as CrewPerformanceMonitor
    participant Crew as CrewAI Framework

    Client->>App: __init__(config_paths, llm_type)
    App->>LLM: build_creative() / build_evaluation()
    LLM-->>App: llm_instance, model_name

    App->>Mgr: __init__(llm, app_config, job_config)
    Mgr->>BP: get_config(name, usecase)
    BP-->>Mgr: master_blueprint

    App->>Orch: __init__(manager)

    Client->>App: run via orchestrator
    App->>Orch: run_crew(crew_name, inputs)
    Orch->>Mgr: build_atomic_crew(crew_name)

    loop For each step in crew_def
        Mgr->>Builder: add_agent(agent_id, knowledge)
        Builder->>Repo: get_agent_by_id(id)
        Repo-->>Builder: AgentResponse
        Builder->>Core: add_agent(AgentRequest)
        Core-->>Builder: self

        Mgr->>Builder: add_task(task_id, agent)
        Builder->>Core: add_task(TaskRequest, agent)
    end

    Mgr->>Builder: build(knowledge_sources)
    Builder->>Core: build()
    Core->>Crew: Crew(agents, tasks, process)
    Crew-->>Orch: crew_instance

    Orch->>Monitor: start_monitoring()
    Orch->>Crew: kickoff(inputs)
    Crew-->>Orch: result
    Orch->>Monitor: stop_monitoring()
    Orch->>Monitor: log_usage(result)
    Orch-->>Client: result
```

---

## 5. Configuration Synchronization Flow

### Sequence Diagram: YAML → MongoDB Sync

```mermaid
%%{init: {'theme': 'base'}}%%
sequenceDiagram
    autonumber
    actor Admin as Administrator
    participant Sync as ConfigSyncService
    participant Seeder as DatabaseSeeder
    participant Parser as CrewParser
    participant FS as FileSystem
    participant AgentRepo as AgentRepository
    participant TaskRepo as TaskRepository
    participant CrewRepo as CrewConfigRepository

    Admin->>Sync: synchronize()
    Sync->>Seeder: synchronize(root_path)
    Seeder->>FS: os.walk(root_path)
    FS-->>Seeder: directory tree

    loop For each YAML file
        Seeder->>Parser: parse_agent/parse_task(file)
        Parser-->>Seeder: AgentRequest / TaskRequest
    end

    loop For each usecase
        loop For each agent
            Seeder->>AgentRepo: find_by_role_and_usecase()
            alt Not Exists
                Seeder->>AgentRepo: create_agent()
            else Changed
                Seeder->>AgentRepo: update_agent()
            else Unchanged
                Note over Seeder: SKIP
            end
        end
        loop For each task
            Seeder->>TaskRepo: find_by_name_and_usecase()
            alt Not Exists / Changed
                Seeder->>TaskRepo: create_task() / update_task()
            end
        end
        Seeder->>CrewRepo: create/update crew_config()
    end
```

---

## 6. Knowledge Source Integration

```mermaid
%%{init: {'theme': 'base'}}%%
flowchart LR
    classDef source fill:#e8f5e9,stroke:#333;
    classDef process fill:#e3f2fd,stroke:#333;
    classDef output fill:#fff3e0,stroke:#333;

    subgraph "Input Sources"
        PDF["PDF Files"]:::source
        DOCX["DOCX Files"]:::source
        MD["Markdown"]:::source
        HTML["HTML Pages"]:::source
        IMG["Images"]:::source
        XLSX["Spreadsheets"]:::source
        URL["URLs"]:::source
    end

    subgraph "Processing Pipeline"
        Validate["validate_content()"]:::process
        Convert["DocumentConverter"]:::process
        Chunk["HierarchicalChunker"]:::process
    end

    subgraph "Output"
        Chunks["Text Chunks"]:::output
        RAG["CrewAI RAG"]:::output
    end

    PDF --> Validate
    DOCX --> Validate
    MD --> Validate
    HTML --> Validate
    IMG --> Validate
    XLSX --> Validate
    URL --> Validate
    Validate --> Convert
    Convert --> Chunk
    Chunk --> Chunks
    Chunks --> RAG
```

---

## 7. Dependency Injection Container Hierarchy

```mermaid
%%{init: {'theme': 'base'}}%%
flowchart TD
    classDef config fill:#ffeb3b,stroke:#333;
    classDef container fill:#e1bee7,stroke:#333;
    classDef provider fill:#b2dfdb,stroke:#333;

    Config["Application Config (YAML)"]:::config

    subgraph CrewForgeContainer
        direction TB
        MongoCont["MongoRepoContainer"]:::container
        AgentRepo["AgentRepo (Factory)"]:::provider
        TaskRepo["TaskRepo (Factory)"]:::provider
        CrewRepo["CrewConfigRepo (Factory)"]:::provider
        Parser["CrewParser (Singleton)"]:::provider
        DbBuilder["AtomicDbBuilder (Factory)"]:::provider
        YamlBuilder["AtomicYamlBuilder (Factory)"]:::provider
        Blueprint["BluePrintService (Callable)"]:::provider
        SyncSvc["ConfigSyncService (Factory)"]:::provider
    end

    Config --> CrewForgeContainer
    Config --> MongoCont
    MongoCont --> AgentRepo
    MongoCont --> TaskRepo
    MongoCont --> CrewRepo
    AgentRepo --> DbBuilder
    TaskRepo --> DbBuilder
    Parser --> YamlBuilder
    CrewRepo --> Blueprint
    AgentRepo --> SyncSvc
    TaskRepo --> SyncSvc
    CrewRepo --> SyncSvc
```

---

## 8. Design Patterns Catalog

| # | Pattern | Implementation | File(s) | Benefit |
|---|:---|:---|:---|:---|
| 1 | **Builder** | `CrewBuilderService` | [crew_builder_service.py](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/crew_forge/service/crew_builder_service.py) | Step-by-step construction of complex Crew objects with fluent chaining |
| 2 | **Repository** | `IAgentRepository`, `ITaskRepository`, `ICrewConfigRepository` | [repo/interfaces/](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/crew_forge/repo/interfaces/) | Decouples domain logic from MongoDB storage |
| 3 | **Facade** | `AtomicDbBuilderService`, `AtomicYamlBuilderService` | [service/](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/crew_forge/service/) | Simplifies heterogeneous data source access behind unified interface |
| 4 | **Abstract Factory** | `AtomicCrewDBManager`, `AtomicCrewFileManager` | [orchestrator/](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/crew_forge/orchestrator/) | Produces families of related crew objects from config |
| 5 | **Blueprint** | `CrewBluePrintService` + `CrewConfigResponse` | [crew_blueprint_service.py](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/crew_forge/service/crew_blueprint_service.py) | Master template for crew topology |
| 6 | **Dependency Injection** | `CrewForgeContainer` + `MongoRepoContainer` | [dependency/](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/crew_forge/dependency/) | Hierarchical container with Factory/Singleton/Callable providers |
| 7 | **Strategy** | Dual-backend resolution (DB vs. YAML) | `atomic_db_builder.py`, `atomic_yaml_builder.py` | Interchangeable data fetching strategies |
| 8 | **Template Method** | `AmshaCrewDBApplication` / `AmshaCrewFileApplication` | [orchestrator/db/](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/crew_forge/orchestrator/db/), [orchestrator/file/](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/crew_forge/orchestrator/file/) | Shared initialization skeleton with backend-specific steps |
| 9 | **Observer** | `CrewPerformanceMonitor` integration | [db_crew_orchestrator.py](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/crew_forge/orchestrator/db/db_crew_orchestrator.py) | Non-intrusive performance tracking |

---

## 9. Metrics Summary

| Metric | Value |
|:---|:---|
| Total Python Files | 56 |
| Sub-Packages | 12 |
| Domain Models (Pydantic) | 6 |
| ABC Interfaces | 4 |
| Design Patterns | 9 |
| Diagrams in this Document | 7 |
| Supported Knowledge Formats | 7 (MD, PDF, DOCX, HTML, IMAGE, XLSX, PPTX) |
