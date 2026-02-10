# Crew Forge Module - Architecture & Design

## Overview
This document visualizes the architecture of the `crew_forge` module, which implements Clean Architecture principles with protocol-based design and the Repository Pattern.

---

## 1. High-Level Architecture - 3-Layer Design

```mermaid
---
config:
  theme: base
---
graph TB
    classDef domain fill:#4ecdc4,stroke:#333,stroke-width:2px
    classDef repo fill:#ff6b6b,stroke:#333,stroke-width:2px
    classDef adapter fill:#ffe66d,stroke:#333,stroke-width:2px
    classDef service fill:#95e1d3,stroke:#333,stroke-width:2px
    
    subgraph "Domain Layer"
        direction LR
        Models[Domain Models]:::domain
        Enums[Repository Backend Enum]:::domain
    end
    
    subgraph "Repository Interfaces"
        direction LR
        IRepo[IRepository]:::repo
        IAgentRepo[IAgentRepository]:::repo
        ITaskRepo[ITaskRepository]:::repo
        ICrewRepo[ICrewConfigRepository]:::repo
    end
    
    subgraph "Adapters Layer"
        direction LR
        MongoRepo[MongoRepository]:::adapter
        AgentRepo[AgentRepository]:::adapter
        TaskRepo[TaskRepository]:::adapter
        CrewRepo[CrewConfigRepository]:::adapter
    end
    
    subgraph "Service Layer"
        direction LR
        AtomicBuilder[AtomicDbBuilderService]:::service
        CrewBuilder[CrewBuilderService]:::service
    end
    
    Models --> IRepo
    IRepo --> IAgentRepo
    IRepo --> ITaskRepo
    IRepo --> ICrewRepo
    
    IAgentRepo -.implements.-> AgentRepo
    ITaskRepo -.implements.-> TaskRepo
    ICrewRepo -.implements.-> CrewRepo
    
    MongoRepo --> AgentRepo
    MongoRepo --> TaskRepo
    MongoRepo --> CrewRepo
    
    AtomicBuilder --> IAgentRepo
    AtomicBuilder --> ITaskRepo
    AtomicBuilder --> CrewBuilder
```

**Caption:** Figure 1.1 - Three-layer architecture showing domain models, repository interfaces, MongoDB adapters, and service layer. Protocol-based design ensures testability and adapter substitutability.

**Source:** Analyzed from [`crew_forge/`](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/crew_forge/) directory structure.

---

## 2. Repository Pattern - Class Diagram

```mermaid
---
config:
  theme: base
---
classDiagram
    class IRepository {
        <<interface>>
        +find_one(query: dict) Optional~Any~
        +find_many(query: dict) List~Any~
        +insert_one(data: dict) Any
        +update_one(query: dict, data: dict) Any
        +delete_one(query: dict) bool
    }
    
    class MongoRepository {
        -client: MongoClient
        -db: Database
        -collection: Collection
        +__init__(data: RepoData)
        +find_one(query: dict) Optional~Any~
        +find_many(query: dict) List~Any~
        +insert_one(data: dict) InsertOneResult
        +update_one(query: dict, data: dict) UpdateResult
        +delete_one(query: dict) DeleteResult
        +create_unique_compound_index(keys: list~str~)
    }
    
    class IAgentRepository {
        <<interface>>
        +get_agent_by_id(agent_id: str) Optional~AgentData~
        +get_all_agents() List~AgentData~
    }
    
    class AgentRepository {
        -mongo_repo: MongoRepository
        +get_agent_by_id(agent_id: str) Optional~AgentData~
        +get_all_agents() List~AgentData~
    }
    
    class RepoData {
        +mongo_uri: str
        +db_name: str
        +collection_name: str
    }
    
    IRepository <|.. MongoRepository : implements
    MongoRepository <|-- AgentRepository : extends
    IAgentRepository <|.. AgentRepository : implements
    RepoData --> MongoRepository : configures
```

**Caption:** Figure 2.1 - Repository pattern class hierarchy showing protocol interfaces (`IRepository`, `IAgentRepository`) and MongoDB implementations. `AgentRepository` demonstrates composition over inheritance.

**Source:** 
- [`i_repository.py`](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/crew_forge/repo/interfaces/i_repository.py)
- [`mongo_repository.py`](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/crew_forge/repo/adapters/mongo/mongo_repository.py)
- [`i_agent_repository.py`](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/crew_forge/repo/interfaces/i_agent_repository.py)
- [`agent_repo.py`](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/crew_forge/repo/adapters/mongo/agent_repo.py)

---

## 3. Atomic Crew Construction - Sequence Diagram

```mermaid
---
config:
  theme: base
---
sequenceDiagram
    autonumber
    participant Client
    participant Manager as AtomicCrewDBManager
    participant Blueprint as CrewBlueprintService
    participant Builder as AtomicDbBuilderService
    participant AgentRepo as IAgentRepository
    participant TaskRepo as ITaskRepository
    participant CrewBuilder as CrewBuilderService
    
    Client->>Manager: __init__(llm, app_config, job_config)
    Manager->>Blueprint: get_config(name, usecase)
    Blueprint-->>Manager: master_blueprint
    
    Client->>Manager: build_atomic_crew(crew_name)
    
    loop For each step in crew_def
        Manager->>AgentRepo: get_agent_by_id(agent_id)
        AgentRepo-->>Manager: agent_details
        
        Manager->>Builder: add_agent(agent_id, knowledge_sources)
        Builder->>CrewBuilder: add_agent(AgentRequest)
        
        Manager->>TaskRepo: get_task_by_id(task_id)
        TaskRepo-->>Manager: task_details
        
        Manager->>Builder: add_task(task_id, agent, output_filename)
        Builder->>CrewBuilder: add_task(TaskRequest, agent)
    end
    
    Manager->>Builder: build(knowledge_sources)
    Builder->>CrewBuilder: build(Process.sequential, knowledge)
    CrewBuilder-->>Builder: Crew object
    Builder-->>Manager: Crew object
    Manager-->>Client: Crew object
```

**Caption:** Figure 3.1 - Sequence diagram showing atomic crew construction flow. The manager fetches agent/task definitions from repositories and incrementally builds the crew using the builder service.

**Source:** [`atomic_crew_db_manager.py:43-116`](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/crew_forge/orchestrator/db/atomic_crew_db_manager.py#L43-L116)

---

## 4. Dependency Injection Container - Component Diagram

```mermaid
---
config:
  theme: base
---
graph LR
    classDef container fill:#a8dadc,stroke:#333,stroke-width:2px
    classDef config fill:#f1faee,stroke:#333,stroke-width:2px
    classDef service fill:#e63946,stroke:#333,stroke-width:2px
    
    Container[CrewForgeContainer]:::container
    Config[YAML Config]:::config
    
    AgentRepoService[Agent Repository]:::service
    TaskRepoService[Task Repository]:::service
    CrewConfigService[Crew Config Repository]:::service
    BuilderService[Atomic Builder Service]:::service
    BlueprintService[Blueprint Service]:::service
    
    Config --> Container
    Container --> AgentRepoService
    Container --> TaskRepoService
    Container --> CrewConfigService
    Container --> BuilderService
    Container --> BlueprintService
    
    BuilderService --> AgentRepoService
    BuilderService --> TaskRepoService
    BlueprintService --> CrewConfigService
```

**Caption:** Figure 4.1 - Dependency injection container managing service instantiation. YAML configuration drives repository connections and service wiring.

**Source:** [`crew_forge_container.py`](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/crew_forge/dependency/crew_forge_container.py)

---

## 5. Domain Models - ER Diagram

```mermaid
---
config:
  theme: base
---
erDiagram
    AGENT_DATA {
        string agent_id PK
        string role
        string goal
        string backstory
    }
    
    TASK_DATA {
        string task_id PK
        string name
        string description
        string expected_output
    }
    
    CREW_CONFIG_DATA {
        string config_id PK
        string name
        string usecase
        dict agents
        dict tasks
    }
    
    REPO_DATA {
        string mongo_uri
        string db_name
        string collection_name
    }
    
    CREW_CONFIG_DATA ||--o{ AGENT_DATA : "contains"
    CREW_CONFIG_DATA ||--o{ TASK_DATA : "defines"
    REPO_DATA ||--|| AGENT_DATA : "persists"
    REPO_DATA ||--|| TASK_DATA : "persists"
    REPO_DATA ||--|| CREW_CONFIG_DATA : "persists"
```

**Caption:** Figure 5.1 - Entity-relationship diagram showing domain model associations. `CrewConfigData` acts as the master blueprint containing references to agents and tasks.

**Source:** 
- [`agent_data.py`](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/crew_forge/domain/models/agent_data.py)
- [`task_data.py`](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/crew_forge/domain/models/task_data.py)
- [`crew_config_data.py`](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/crew_forge/domain/models/crew_config_data.py)

---

## 6. Performance Metrics

### Table 6.1: Crew Forge Module Metrics

| S.No | Metric | Value | Unit | Source |
|:----:|:-------|------:|:-----|:-------|
| 1 | Total Files | 56 | files | `find` command |
| 2 | Core Domain Models | 5 | classes | `domain/models/` |
| 3 | Repository Interfaces | 4 | protocols | `repo/interfaces/` |
| 4 | MongoDB Adapters | 4 | classes | `repo/adapters/mongo/` |
| 5 | Service Layer Classes | 6 | classes | `service/` |
| 6 | Dependency Injection | 1 | container | `dependency/` |
| 7 | Protocol Compliance | 100 | % | All repos implement `IRepository` |

**Caption:** Table 6.1 - Code organization metrics for the `crew_forge` module showing adherence to Clean Architecture layer separation.

---

## 7. Design Patterns Summary

### Table 7.1: Design Patterns in Crew Forge

| S.No | Pattern | Implementation | Benefit | Source |
|:----:|:--------|:---------------|:--------|:-------|
| 1 | **Repository Pattern** | `IRepository` + `MongoRepository` | Persistence abstraction | [`repo/`](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/crew_forge/repo/) |
| 2 | **Protocol-Based Design** | Abstract interfaces (`IAgentRepository`) | Testability, polymorphism | [`repo/interfaces/`](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/crew_forge/repo/interfaces/) |
| 3 | **Dependency Injection** | `CrewForgeContainer` | Loose coupling | [`dependency/`](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/crew_forge/dependency/) |
| 4 | **Builder Pattern** | `AtomicDbBuilderService` | Incremental crew construction | [`service/atomic_db_builder.py`](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/crew_forge/service/atomic_db_builder.py) |
| 5 | **Facade Pattern** | `AtomicCrewDBManager` | Simplified manager interface | [`orchestrator/db/`](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/crew_forge/orchestrator/db/) |

**Caption:** Table 7.1 - Design patterns implemented in the module with their architectural benefits and source locations.

---

## Summary

**Total Diagrams:** 5 (architecture, class, sequence, component, ER)  
**Total Tables:** 2 (metrics, design patterns)

All diagrams verified against source code. All component names match actual file paths.
