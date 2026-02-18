# System Dependency Analysis

## 1. Dependency Graph

The following directed graph illustrates the module dependencies within the `nikhil.amsha` namespace.

```mermaid
---
config:
  theme: base
---
flowchart TD
    classDef core fill:#ff9999,stroke:#333,stroke-width:2px;
    classDef support fill:#99ff99,stroke:#333,stroke-width:1px;
    
    subgraph Core Layer
        Forge[Crew Forge]:::core
    end
    
    subgraph Support Layer
        LLM[LLM Factory]:::support
        Monitor[Crew Monitor]:::support
        Output[Output Process]:::support
    end
    
    Forge -->|Uses| LLM
    Forge -->|Uses| Monitor
    Forge -->|Uses| Output
    
    Output -.->|Imports (Circular)| Forge
```

## 2. Coupling Internal Analysis

### 2.1 Core Orchestrator (`crew_forge`)
- **Coupling**: High (Efferent)
- **Role**: Consumer of all other modules.
- **Risk**: High stability risk; changes in any support module can impact the orchestrator.

### 2.2 Support Modules (`llm_factory`, `crew_monitor`)
- **Coupling**: Low (Afferent only)
- **Role**: Independent service providers.
- **Stability**: High; they have no internal dependencies on other system modules.

### 2.3 Output Process (`output_process`)
- **Coupling**: Moderate
- **Issue Detected**: **Circular Dependency**
    - `src/nikhil/amsha/output_process/validation/crew_validator.py` imports `CrewParser` from `src/nikhil/amsha/crew_forge/seeding/parser/crew_parser.py`.
    - This creates a feedback loop where `crew_forge` depends on `output_process` for validation, but `output_process` depends on `crew_forge` for parsing logic.

## 3. Architectural Validation

| Relationship | Expected Direction | Actual Direction | Status |
|:---|:---|:---|:---|
| Orchestrator -> LLM Provider | Downward | Downward | ✅ Valid |
| Orchestrator -> Monitor | Downward | Downward | ✅ Valid |
| Orchestrator -> Validator | Downward | Downward | ✅ Valid |
| Validator -> Orchestrator (Parser) | None (Forbidden) | Upward | ❌ **Violation** |

## 4. Recommendations

1.  **Break Circular Dependency**: Move `CrewParser` to a shared `utils` or `common` module that both `crew_forge` and `output_process` can import.
2.  **Interface Segregation**: Ensure `crew_forge` relies on interfaces for monitoring and validation to reduce direct implementation coupling.
