# Cross-Module Architecture & Design

This document provides **system-level architectural diagrams and performance analysis** for the Amsha framework. Unlike per-module architecture documents (which show internal class/sequence diagrams), this document captures the **high-level system architecture**, **end-to-end data flows**, and **global performance metrics** across all 4 analyzed modules.

---

## 1. High-Level System Architecture

### 1.1 Layered Module Architecture

```mermaid
%%{init: {'theme': 'base'}}%%
flowchart TD
    classDef app fill:#ffd700,stroke:#333,stroke-width:2px;
    classDef core fill:#ff9999,stroke:#333,stroke-width:2px;
    classDef support fill:#99ccff,stroke:#333,stroke-width:2px;
    classDef shared fill:#ffffcc,stroke:#333,stroke-width:2px;
    classDef ext fill:#ddd,stroke:#666,stroke-width:1px;

    subgraph "Application Layer"
        direction LR
        DBApp["AmshaCrewDBApplication"]:::app
        FileApp["AmshaCrewFileApplication"]:::app
    end

    subgraph "Core Orchestration Layer"
        direction LR
        CF["crew_forge (56 files)"]:::core
        DBOrch["DbCrewOrchestrator"]:::core
        FileOrch["FileCrewOrchestrator"]:::core
    end

    subgraph "Support Services Layer"
        direction LR
        LLM["llm_factory (14 files)"]:::support
        MON["crew_monitor (7 files)"]:::support
        OUT["output_process (10 files)"]:::support
    end

    subgraph "Shared Foundation Layer"
        Utils["amsha.utils"]:::shared
    end

    subgraph "External Dependencies"
        CrewAI["CrewAI"]:::ext
        PSUtil["psutil + pynvml"]:::ext
        Pandas["pandas + numpy"]:::ext
        Pydantic["pydantic"]:::ext
        DI["dependency-injector"]:::ext
        MongoDB["pymongo"]:::ext
    end

    DBApp --> DBOrch
    FileApp --> FileOrch
    DBOrch --> CF
    FileOrch --> CF
    CF -->|"LLMContainer, LLMType"| LLM
    CF -->|"CrewPerformanceMonitor"| MON
    OUT -.->|"CrewParser (circular)"| CF

    CF --> Utils
    LLM --> Utils
    MON --> Utils
    OUT --> Utils

    CF --> CrewAI
    CF --> MongoDB
    CF --> Pydantic
    CF --> DI
    LLM --> CrewAI
    LLM --> Pydantic
    LLM --> DI
    MON --> PSUtil
    MON --> Pandas
    OUT --> Pandas
```

**Figure 1.** High-level layered architecture of the Amsha framework. The Application Layer provides user-facing entry points. The Core Orchestration Layer (crew_forge) coordinates Support Services (llm_factory, crew_monitor, output_process). All modules share a common utility foundation. One architectural violation exists: output_process depends upward on crew_forge.

---

### 1.2 Clean Architecture Compliance per Module

```mermaid
%%{init: {'theme': 'base'}}%%
flowchart TB
    classDef domain fill:#c8e6c9,stroke:#333;
    classDef service fill:#bbdefb,stroke:#333;
    classDef infra fill:#ffe0b2,stroke:#333;
    classDef app fill:#f8bbd0,stroke:#333;

    subgraph "crew_forge"
        CF_D["Domain\n(6 Pydantic models)"]:::domain
        CF_S["Services\n(Builder, Blueprint, Sync)"]:::service
        CF_I["Infrastructure\n(MongoRepo, Parser, DI)"]:::infra
        CF_A["Application\n(DB/File Orchestrators)"]:::app
        CF_A --> CF_S
        CF_S --> CF_D
        CF_I --> CF_D
    end

    subgraph "llm_factory"
        LLM_D["Domain\n(4 Pydantic models)"]:::domain
        LLM_S["Services\n(Builder, Settings)"]:::service
        LLM_I["Infrastructure\n(DI Container)"]:::infra
        LLM_S --> LLM_D
        LLM_I --> LLM_D
    end

    subgraph "crew_monitor"
        MON_D["Domain\n(3 Pydantic models)"]:::domain
        MON_S["Services\n(Monitor, Analyzer)"]:::service
        MON_S --> MON_D
    end

    subgraph "output_process"
        OUT_S["Services\n(Evaluator, Grader, Cleaner)"]:::service
        OUT_V["Validation\n(CrewValidator, JsonValidator)"]:::service
    end
```

**Figure 2.** Clean Architecture layer compliance for each module. crew_forge has the most complete layered architecture (4 layers). llm_factory has 3 layers. crew_monitor has 2 layers. output_process operates primarily at the service layer with no explicit domain models (uses raw dicts).

---

## 2. End-to-End Data Flow Architecture

### 2.1 Full Execution Pipeline (Provisioning → Execution → Monitoring → Evaluation)

```mermaid
%%{init: {'theme': 'base'}}%%
sequenceDiagram
    autonumber
    actor Client
    participant App as Application Layer
    participant LLM as llm_factory
    participant CF as crew_forge
    participant MON as crew_monitor
    participant OUT as output_process
    participant Utils as amsha.utils

    rect rgb(255, 248, 230)
        note over App,LLM: Phase 1: Privacy-Guarded LLM Provisioning
        App->>LLM: LLMContainer.config.llm.yaml_path(path)
        LLM->>Utils: YamlUtils.yaml_safe_load(llm_config.yaml)
        Utils-->>LLM: config dict
        LLM->>LLM: disable_telemetry() [dual-layer privacy]
        LLM->>LLM: build_creative() → LLMBuildResult
        LLM-->>App: (llm_instance, model_name)
    end

    rect rgb(230, 255, 230)
        note over App,CF: Phase 2: Blueprint-Driven Crew Assembly
        App->>CF: AtomicCrewManager(llm, model_name, configs)
        CF->>Utils: YamlUtils.yaml_safe_load(job_config.yaml)
        CF->>CF: CrewBluePrintService.get_by_name(crew_name)
        CF->>CF: Build agents and tasks from blueprint steps
        CF->>CF: CrewBuilderService.build() → Crew
    end

    rect rgb(230, 230, 255)
        note over CF,MON: Phase 3: Sandwich-Profiled Execution
        CF->>MON: CrewPerformanceMonitor(model_name)
        CF->>MON: start_monitoring()
        MON->>MON: Capture S(t₀): CPU%, RAM, GPU VRAM
        CF->>CF: crew.kickoff(inputs)
        CF->>MON: stop_monitoring()
        MON->>MON: Capture S(t₁): CPU%, RAM, GPU VRAM + util
        CF->>MON: log_usage(result)
        MON-->>CF: get_metrics() → {general, gpu}
    end

    rect rgb(255, 230, 230)
        note over OUT: Phase 4: Post-Processing Pipeline (Independent)
        Client->>OUT: JsonCleanerUtils(raw_output)
        OUT->>OUT: 3-stage cascade parse
        Client->>OUT: EvaluationProcessingTool.run()
        OUT->>OUT: Rubric-weighted scoring
        Client->>OUT: EvaluationAggregationTool.run()
        OUT->>OUT: Z-score relative grading
        Client->>OUT: EvaluationReportTool.run()
        OUT->>OUT: Multi-model pivot consolidation
    end
```

**Figure 3.** Complete end-to-end execution sequence spanning all 4 modules. Phase 1 provisions LLMs with privacy guard. Phase 2 materializes the crew from blueprints. Phase 3 wraps execution in a sandwich profiler. Phase 4 applies a 4-stage evaluation pipeline. Phases 1–3 are tightly coupled; Phase 4 operates independently on filesystem artifacts.

---

### 2.2 Data Transformation Pipeline

```mermaid
%%{init: {'theme': 'base'}}%%
flowchart LR
    classDef config fill:#fff3e0,stroke:#333;
    classDef data fill:#e3f2fd,stroke:#333;
    classDef result fill:#e8f5e9,stroke:#333;
    classDef metric fill:#fce4ec,stroke:#333;

    subgraph "Inputs"
        YAML["YAML Configs"]:::config
        Prompts["User Prompts"]:::config
    end

    subgraph "llm_factory"
        LLMInst["LLMBuildResult\n(llm, model_name)"]:::data
    end

    subgraph "crew_forge"
        Crew["Crew Instance\n(agents, tasks, process)"]:::data
        Raw["Raw LLM Output\n(str/JSON)"]:::result
    end

    subgraph "crew_monitor"
        Metrics["Performance Metrics\n{general, gpu}"]:::metric
    end

    subgraph "output_process"
        Clean["Cleaned JSON"]:::data
        Scored["Rubric Scores"]:::data
        Graded["Z-Score Grades"]:::result
        Report["Pivot Report"]:::result
    end

    YAML --> LLMInst
    LLMInst --> Crew
    YAML --> Crew
    Prompts --> Crew
    Crew --> Raw
    Crew --> Metrics
    Raw --> Clean
    Clean --> Scored
    Scored --> Graded
    Graded --> Report
```

**Figure 4.** Data transformation pipeline showing type transformations at each stage. YAML configs drive LLM provisioning and crew assembly. Raw LLM output undergoes 4-stage refinement into graded reports. Performance metrics are captured as a side-channel.

---

## 3. DI Container Hierarchy (System-Wide)

```mermaid
%%{init: {'theme': 'base'}}%%
flowchart TD
    classDef container fill:#e1bee7,stroke:#333;
    classDef provider fill:#b2dfdb,stroke:#333;
    classDef config fill:#ffeb3b,stroke:#333;

    subgraph "LLMContainer (llm_factory)"
        LConfig["config.llm.yaml_path"]:::config
        LYaml["yaml_data (Singleton)"]:::provider
        LSettings["llm_settings (Singleton)"]:::provider
        LBuilder["llm_builder (Factory)"]:::provider
        LCreative["creative_llm (Pre-wired)"]:::provider
        LEval["evaluation_llm (Pre-wired)"]:::provider

        LConfig --> LYaml
        LYaml --> LSettings
        LSettings --> LBuilder
        LBuilder --> LCreative
        LBuilder --> LEval
    end

    subgraph "CrewForgeContainer (crew_forge)"
        CConfig["config (YAML paths)"]:::config
        CMongo["MongoRepoContainer (nested)"]:::container
        CParser["crew_parser (Singleton)"]:::provider
        CBuilder["crew_builder (Factory)"]:::provider
        CDB["atomic_db_builder (Factory)"]:::provider
        CYAML["atomic_yaml_builder (Factory)"]:::provider
        CBP["blueprint_service (Callable)"]:::provider
        CSync["sync_service (Factory)"]:::provider

        CConfig --> CMongo
        CMongo --> CDB
        CParser --> CYAML
        CConfig --> CBuilder
        CBuilder --> CDB
        CBuilder --> CYAML
        CMongo --> CBP
        CMongo --> CSync
    end

    LCreative -.->|"consumed by"| CDB
    LCreative -.->|"consumed by"| CYAML
```

**Figure 5.** System-wide Dependency Injection container hierarchy. The `LLMContainer` (llm_factory) produces LLM instances consumed by `CrewForgeContainer` (crew_forge). Both use the `dependency-injector` library with Singleton, Factory, and Pre-wired provider strategies.

---

## 4. Module Coupling Architecture

### 4.1 Coupling Matrix

```mermaid
%%{init: {'theme': 'base'}}%%
flowchart TD
    classDef stable fill:#c8e6c9,stroke:#333,stroke-width:2px;
    classDef unstable fill:#ffcdd2,stroke:#333,stroke-width:2px;
    classDef neutral fill:#bbdefb,stroke:#333;

    subgraph "Instability Analysis"
        direction LR
        U["amsha.utils\nI=0.00 (Stable)"]:::stable
        L["llm_factory\nI=0.00 (Stable)"]:::stable
        M["crew_monitor\nI=0.00 (Stable)"]:::stable
        C["crew_forge\nI=0.75 (Unstable)"]:::unstable
        O["output_process\nI=1.00 (Max Unstable)"]:::unstable
    end

    C -->|"4 imports"| L
    C -->|"2 imports"| M
    O -.->|"1 import"| C
    C --> U
    L --> U
    M --> U
    O --> U
```

**Figure 6.** Module instability analysis. Dependencies flow from unstable modules (crew_forge, output_process) toward stable modules (llm_factory, crew_monitor, utils), following the Stable Dependencies Principle. The one violation (output_process→crew_forge) breaks this principle.

### 4.2 Coupling Metrics Table

| Module | Files | Efferent ($C_e$) | Afferent ($C_a$) | Instability ($I$) | Classification |
|:---|:---:|:---:|:---:|:---:|:---|
| `crew_forge` | 56 | 3 | 1 | 0.75 | Unstable (main consumer) |
| `llm_factory` | 14 | 0 | 2 | 0.00 | Maximally Stable (provider) |
| `crew_monitor` | 7 | 0 | 1 | 0.00 | Maximally Stable (provider) |
| `output_process` | 10 | 1 | 0 | 1.00 | Maximally Unstable (consumer) |
| `amsha.utils` | 4 | 0 | 4 | 0.00 | Maximally Stable (foundation) |

*Table 1.* Module coupling metrics using Robert Martin's Instability formula: $I = C_e / (C_a + C_e)$. Source: Cross-module import analysis (see `dependencies.md`).

---

## 5. System State Machine

```mermaid
%%{init: {'theme': 'base'}}%%
stateDiagram-v2
    [*] --> ConfigLoaded : Load YAML configs
    ConfigLoaded --> LLMProvisioned : llm_factory.build()
    LLMProvisioned --> CrewAssembled : crew_forge.build_atomic_crew()
    CrewAssembled --> MonitoringStarted : monitor.start_monitoring()
    MonitoringStarted --> Executing : crew.kickoff()
    Executing --> MonitoringStopped : monitor.stop_monitoring()
    MonitoringStopped --> ResultCaptured : monitor.log_usage()
    ResultCaptured --> JSONCleaned : JsonCleanerUtils.clean()
    JSONCleaned --> RubricScored : EvaluationProcessingTool.run()
    RubricScored --> ZScoreGraded : EvaluationAggregationTool.run()
    ZScoreGraded --> ReportGenerated : EvaluationReportTool.run()
    ReportGenerated --> [*]

    Executing --> ExecutionFailed : Exception
    ExecutionFailed --> MonitoringStopped : monitor.stop_monitoring()

    note right of ConfigLoaded : All modules use\nYamlUtils.yaml_safe_load()
    note right of LLMProvisioned : Privacy guard active\n(dual-layer)
    note right of MonitoringStarted : Sandwich profiler\nS(t₀) captured
```

**Figure 7.** System-wide state machine for a complete Amsha execution lifecycle. The lifecycle spans 4 modules in sequence: configuration loading (utils) → LLM provisioning (llm_factory) → crew execution (crew_forge + crew_monitor) → post-processing (output_process). Error handling ensures monitoring is stopped even on execution failure.

---

## 6. Module Size and Complexity Comparison

| Module | Files | Sub-Packages | Pydantic Models | Diagrams (per-module) | Algorithms | Design Patterns |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| `crew_forge` | 56 | 12 | 6 | 6 | 8 | 9 |
| `llm_factory` | 14 | 6 | 4 | 4 | 6 | 6 |
| `crew_monitor` | 7 | 3 | 3 | 3 | 7 | 7 |
| `output_process` | 10 | 3 | **0** ⚠️ | 3 | 7 | 8 |
| **System Total** | **87** | **24** | **13** | **16** | **28** | **30** |

*Table 2.* Module-level metrics from per-module analysis. crew_forge is the largest module (56 files). output_process lacks Pydantic domain models — a notable gap. Source: Module analysis documents.

---

## 7. External Dependency Architecture

```mermaid
%%{init: {'theme': 'base'}}%%
flowchart LR
    classDef core fill:#ff9999,stroke:#333;
    classDef dep fill:#e0e0e0,stroke:#666;

    CF["crew_forge"]:::core
    LLM["llm_factory"]:::core
    MON["crew_monitor"]:::core
    OUT["output_process"]:::core

    CrewAI["crewai"]:::dep
    PyMongo["pymongo"]:::dep
    PDantic["pydantic"]:::dep
    DepInj["dependency-injector"]:::dep
    Docling["docling"]:::dep
    PSUtil["psutil"]:::dep
    PyNVML["pynvml (optional)"]:::dep
    PandasLib["pandas"]:::dep
    NumPyLib["numpy"]:::dep
    OpXL["openpyxl"]:::dep

    CF --> CrewAI
    CF --> PyMongo
    CF --> PDantic
    CF --> DepInj
    CF --> Docling
    LLM --> CrewAI
    LLM --> PDantic
    LLM --> DepInj
    MON --> PSUtil
    MON --> PyNVML
    MON --> PandasLib
    OUT --> NumPyLib
    OUT --> PandasLib
    OUT --> OpXL
```

**Figure 8.** External dependency graph. crew_forge has the highest external dependency count (5 libraries). llm_factory shares 3 dependencies with crew_forge (crewai, pydantic, dependency-injector). crew_monitor's pynvml is optional (graceful degradation). pandas is shared between crew_monitor and output_process.

### External Dependency Risk Assessment

| Library | Used By | Risk Level | Reason |
|:---|:---|:---:|:---|
| `crewai` | crew_forge, llm_factory | **High** | Core framework, breaking API changes |
| `pydantic` | crew_forge, llm_factory | Medium | Stable, but v1→v2 migration risk |
| `dependency-injector` | crew_forge, llm_factory | Low | Mature, stable API |
| `pymongo` | crew_forge | Low | Stable driver |
| `docling` | crew_forge | Medium | Newer library, fewer guarantees |
| `psutil` | crew_monitor | Low | OS-level, very stable |
| `pynvml` | crew_monitor | Low | NVIDIA official, optional |
| `pandas` | crew_monitor, output_process | Low | Industry standard |
| `numpy` | output_process | Low | Industry standard |
| `openpyxl` | crew_monitor, output_process | Low | Stable Excel engine |

*Table 3.* External dependency risk assessment. crewai is the highest-risk dependency due to frequent API surface changes. Source: requirements analysis and external dependency survey.

---

## 8. Architectural Quality Summary

### Compliance Scorecard

| Quality Attribute | Score | Evidence |
|:---|:---:|:---|
| Clean Architecture Adherence | **7/8** relations valid | 1 violation: output_process → crew_forge |
| Dependency Direction | **Mostly correct** | Dependencies flow toward stable modules |
| Configuration Externalization | **4/4 modules** | Universal YAML pattern via amsha.utils |
| Domain Model Coverage | **3/4 modules** | output_process lacks Pydantic models |
| DI Container Usage | **2/4 modules** | crew_forge and llm_factory only |
| Monitoring Integration | **Seamless** | Negligible overhead ($\leq$0.05%) |
| Privacy Enforcement | **Dual-layer** | Environment + reflection-based |
| Testability | **High** | Protocol-based, DI-enabled |

### Recommendations for Architectural Improvement

1. **P0 — Break circular dependency:** Move `CrewParser` to `amsha.common.parsing`
2. **P1 — Add Pydantic models to output_process:** Formalize evaluation schemas
3. **P2 — Extend DI to crew_monitor and output_process:** Consistent instantiation pattern
4. **P3 — Add protocol-based decoupling:** Use Python Protocols for crew_forge → crew_monitor interface
