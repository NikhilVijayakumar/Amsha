# Crew Forge: Architecture & Design

## 1. Architectural Overview

The `crew_forge` module implements a robust **Clean Architecture** for AI Agent orchestration. It separates the domain logic of Crew composition from the data sources (YAML files vs. MongoDB) using the **Builder** and **Repository** patterns.

### Component Diagram

```mermaid
%%{init: {'theme': 'base'}}%%
flowchart TD
    classDef domain fill:#f9f,stroke:#333,stroke-width:2px;
    classDef service fill:#bbf,stroke:#333,stroke-width:2px;
    classDef infra fill:#bfb,stroke:#333,stroke-width:2px;

    subgraph "Domain Layer"
        Models[Data Models]:::domain
        Interfaces[Repository Interfaces]:::domain
    end

    subgraph "Service Layer"
        CBS[CrewBuilderService]:::service
        ADB[AtomicDbBuilder]:::service
        AYB[AtomicYamlBuilder]:::service
    end

    subgraph "Infrastructure Layer"
        Mongo[MongoRepository]:::infra
        YParse[YamlParser]:::infra
        DI[Dependency Container]:::infra
    end

    ADB --> CBS
    AYB --> CBS
    ADB --> Interfaces
    AYB --> YParse
    Mongo --> Interfaces
    DI --> ADB
```

## 2. Class Design (Builder Pattern)

The core logical unit is `CrewBuilderService`, which constructs the Crew. Wrappers like `AtomicDbBuilderService` act as Facades that fetch data from repositories before delegating to the core builder.

### Class Diagram

```mermaid
%%{init: {'theme': 'base'}}%%
classDiagram
    note "Core orchestration logic decoupled from data sources"
    
    class CrewBuilderService {
        -_agents: List
        -_tasks: List
        +add_agent(AgentRequest)
        +add_task(TaskRequest)
        +build(): Crew
    }

    class AtomicDbBuilderService {
        -builder: CrewBuilderService
        -agent_repo: IAgentRepository
        -task_repo: ITaskRepository
        +add_agent(agent_id: str)
        +add_task(task_id: str)
        +build(): Crew
    }

    class IAgentRepository {
        <<interface>>
        +get_agent_by_id(id: str)*
    }

    class MongoAgentRepo {
        +get_agent_by_id(id: str)
    }

    AtomicDbBuilderService --> CrewBuilderService : delegates
    AtomicDbBuilderService --> IAgentRepository : depends on
    IAgentRepository <|.. MongoAgentRepo : implements
```

## 3. Execution Flow (Sequence Diagram)

The following sequence illustrates how a Crew is built from database records, demonstrating the interaction between the Application, Builder, and Repository layers.

### Sequence Diagram: DB-Based Construction

```mermaid
%%{init: {'theme': 'base'}}%%
sequenceDiagram
    autonumber
    actor App as Client Application
    participant ADB as AtomicDbBuilder
    participant Repo as MongoAgentRepo
    participant Core as CrewBuilderService
    participant Crew as CrewAI Framework

    App->>ADB: add_agent(agent_id)
    ADB->>Repo: get_agent_by_id(agent_id)
    Repo-->>ADB: AgentData(Role, Goal...)
    ADB->>Core: add_agent(AgentData)
    Core-->>ADB: self (chainable)
    
    App->>ADB: add_task(task_id, agent)
    ADB->>Core: add_task(TaskData)
    Core-->>ADB: self
    
    App->>ADB: build()
    ADB->>Core: build()
    Core->>Crew: Crew(agents, tasks)
    Crew-->>Core: crew_instance
    Core-->>ADB: crew_instance
    ADB-->>App: crew_instance
```

## 4. Design Patterns Implemented

| Pattern | Implementation | Benefit |
| :--- | :--- | :--- |
| **Builder** | `CrewBuilderService` | Allows step-by-step construction of complex Crew objects. |
| **Repository** | `IAgentRepository` | Decouples business logic from MongoDB implementation. |
| **Facade** | `AtomicDbBuilderService` | Simplifies the interface for creating crews from DB IDs. |
| **Dependency Injection** | `CrewForgeContainer` | Manages component lifecycles and dependencies. |
