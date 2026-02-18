# Architectural Patterns Analysis

## 1. System-Wide Patterns

The Amsha project exhibits a structured use of standard enterprise design patterns to manage complexity and separation of concerns.

## 2. Key Patterns Identification

### 2.1 Repository Pattern
- **Location**: `crew_forge/repo`
- **Purpose**: Abstracts data access logic for `Agents`, `Tasks`, and `CrewConfigs`.
- **Implementation**: Uses interfaces (`IAgentRepository`, `ITaskRepository`) to decouple business logic from database implementation.

### 2.2 Factory Pattern
- **Location**: `llm_factory`
- **Purpose**: Centralizes the creation of LLM instances (OpenAI, DeepSeek, etc.).
- **Benefit**: Allows adding new LLM providers without modifying the client code in `crew_forge`.

### 2.3 Builder Pattern
- **Location**: `crew_forge/service/crew_builder_service.py`
- **Purpose**: Constructs complex `Crew` objects step-by-step.
- **Structure**:
    - Methods: `add_agent()`, `add_task()`, `build()`
    - Fluent interface style allows chaining.

### 2.4 Orchestrator Pattern
- **Location**: `crew_forge/orchestrator`
- **Purpose**: Coordinates the workflow of loading configs, building crews, and managing execution.
- **Implementation**: `FileCrewOrchestrator` and `DbCrewOrchestrator` manage different sources of truth (File vs DB).

## 3. Pattern Consistency

| Pattern | Usage Quality | Consistency | Notes |
|:---|:---|:---|:---|
| Repository | High | High | Consistently used across domain entities in `crew_forge`. |
| Factory | High | Focused | interactions restricted to `llm_factory`. |
| Builder | High | Single Use | Effectively simplifies the complex `Crew` initialization. |
| Dependency Injection | Moderate | Variable | Some manual injection in `service` layers, but containers (`CrewForgeContainer`) are evidenced. |

## 4. Architectural Style

The project follows a **Modular Monolith** architecture with a trend towards **Clean Architecture** (Domain, Repo, Service layers clearly separated).
