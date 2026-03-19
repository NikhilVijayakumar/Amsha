# Cross-Module Interactions Analysis

## 1. Overview

The Amsha framework follows a **hub-and-spoke** interaction model with `crew_forge` as the central orchestrator. This document traces every cross-module import at code level, mapping exact files, lines, and data flows across the 4 analyzed modules plus shared utilities.

---

## 2. Complete Import Dependency Graph

```mermaid
%%{init: {'theme': 'base'}}%%
flowchart TD
    classDef core fill:#ff9999,stroke:#333,stroke-width:2px;
    classDef support fill:#99ccff,stroke:#333,stroke-width:2px;
    classDef shared fill:#ffffcc,stroke:#333,stroke-width:2px;
    classDef circular fill:#ffcccc,stroke:#f00,stroke-width:2px;

    subgraph "Shared Foundation"
        Utils["amsha.utils<br/>(YamlUtils, JsonUtils, Utf8Utils)"]:::shared
    end

    subgraph "Core Orchestrator"
        CF["crew_forge<br/>(56 files, 12 sub-packages)"]:::core
    end

    subgraph "Support Modules"
        LLM["llm_factory<br/>(14 files, 6 sub-packages)"]:::support
        MON["crew_monitor<br/>(7 files, 3 sub-packages)"]:::support
        OUT["output_process<br/>(10 files, 3 sub-packages)"]:::support
    end

    subgraph "Consumer"
        GEN["crew_gen"]:::support
    end

    CF -->|"LLMContainer, LLMType"| LLM
    CF -->|"CrewPerformanceMonitor"| MON
    OUT -.->|"CrewParser ⚠️ CIRCULAR"| CF
    GEN -->|"LLMType"| LLM

    CF -->|"YamlUtils (6 files)"| Utils
    LLM -->|"YamlUtils (1 file)"| Utils
    MON -->|"JsonUtils, YamlUtils (2 files)"| Utils
    OUT -->|"JsonUtils, YamlUtils (3 files)"| Utils
```

---

## 3. Code-Verified Import Registry

Every cross-module import traced to exact file and line:

### 3.1 crew_forge → llm_factory

| Source File | Import | Line |
|:---|:---|:---:|
| [amsha_crew_db_application.py](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/crew_forge/orchestrator/db/amsha_crew_db_application.py) | `LLMContainer` | L7 |
| [amsha_crew_db_application.py](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/crew_forge/orchestrator/db/amsha_crew_db_application.py) | `LLMType` | L8 |
| [amsha_crew_file_application.py](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/crew_forge/orchestrator/file/amsha_crew_file_application.py) | `LLMContainer` | L7 |
| [amsha_crew_file_application.py](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/crew_forge/orchestrator/file/amsha_crew_file_application.py) | `LLMType` | L8 |

### 3.2 crew_forge → crew_monitor

| Source File | Import | Line |
|:---|:---|:---:|
| [db_crew_orchestrator.py](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/crew_forge/orchestrator/db/db_crew_orchestrator.py) | `CrewPerformanceMonitor` | L5 |
| [file_crew_orchestrator.py](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/crew_forge/orchestrator/file/file_crew_orchestrator.py) | `CrewPerformanceMonitor` | L5 |

### 3.3 output_process → crew_forge ⚠️ CIRCULAR

| Source File | Import | Line |
|:---|:---|:---:|
| [crew_validator.py](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/output_process/validation/crew_validator.py) | `CrewParser` | L7 |

### 3.4 crew_gen → llm_factory

| Source File | Import | Line |
|:---|:---|:---:|
| [crew_gen_app.py](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/crew_gen/application/crew_gen_app.py) | `LLMType` | L4 |
| [designer_crew_app.py](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/crew_gen/units/designer/designer_crew_app.py) | `LLMType` | L4 |

### 3.5 All Modules → amsha.utils

| Module | Utility | Files Using |
|:---|:---|:---|
| crew_forge | `YamlUtils` | 6 files (orchestrator apps, parsers, sync manager) |
| llm_factory | `YamlUtils` | 1 file (llm_container.py) |
| crew_monitor | `JsonUtils`, `YamlUtils` | 2 files (contribution_analyzer, reporting_tool) |
| output_process | `JsonUtils`, `YamlUtils` | 3 files (all evaluation tools) |

---

## 4. Full Execution Lifecycle Sequence

```mermaid
%%{init: {'theme': 'base'}}%%
sequenceDiagram
    autonumber
    actor Client
    participant CF as crew_forge<br/>(Orchestrator)
    participant LLM as llm_factory<br/>(LLM Provider)
    participant MON as crew_monitor<br/>(Profiler)
    participant OUT as output_process<br/>(Post-Processor)
    participant Utils as amsha.utils

    rect rgb(255, 248, 230)
        note over CF,LLM: Phase 1: LLM Provisioning
        CF->>LLM: LLMContainer.config.llm.yaml_path(path)
        LLM->>Utils: YamlUtils.yaml_safe_load(path)
        Utils-->>LLM: config dict
        CF->>LLM: container.creative_llm()
        LLM->>LLM: disable_telemetry() + build_creative()
        LLM-->>CF: LLMBuildResult(llm, model_name)
    end

    rect rgb(230, 255, 230)
        note over CF: Phase 2: Crew Assembly
        CF->>CF: CrewBluePrintService.get_by_name(crew_name)
        CF->>CF: AtomicDbBuilderService.build_crew()
        CF->>CF: CrewBuilderService.add_agent() × N
        CF->>CF: CrewBuilderService.add_task() × M
        CF->>CF: CrewBuilderService.build() → Crew
    end

    rect rgb(230, 230, 255)
        note over CF,MON: Phase 3: Monitored Execution
        CF->>MON: CrewPerformanceMonitor(model_name)
        CF->>MON: start_monitoring()
        MON->>MON: Capture S(t₀): CPU, RAM, GPU
        CF->>CF: crew.kickoff(inputs)
        CF->>MON: stop_monitoring()
        MON->>MON: Capture S(t₁): CPU, RAM, GPU
        CF->>MON: log_usage(result)
        MON-->>CF: get_metrics() → {general, gpu}
    end

    rect rgb(255, 230, 230)
        note over OUT: Phase 4: Post-Processing (Independent)
        Client->>OUT: JsonCleanerUtils(raw_output)
        OUT->>OUT: 4-stage cascade parse
        Client->>OUT: EvaluationProcessingTool.run()
        OUT->>OUT: Rubric-weighted scoring
        Client->>OUT: EvaluationAggregationTool.run()
        OUT->>OUT: Z-score relative grading
        Client->>OUT: EvaluationReportTool.run()
        OUT->>OUT: Multi-model pivot consolidation
    end
```

---

## 5. Data Flow Matrix (Code-Verified)

| Source → Target | Data Type | Mechanism | Code Reference |
|:---|:---|:---|:---|
| `crew_forge` → `llm_factory` | YAML path (str) | Container config inject | `LLMContainer.config.llm.yaml_path.from_value()` |
| `llm_factory` → `crew_forge` | `LLMBuildResult` (LLM + name) | Return value | `container.creative_llm()` |
| `crew_forge` → `crew_monitor` | model_name (str) | Constructor arg | `CrewPerformanceMonitor(model_name)` |
| `crew_monitor` → `crew_forge` | metrics dict | Return value | `monitor.get_metrics()` |
| `output_process` → `crew_forge` | None (imports only) | Static import | `from crew_forge...CrewParser` |
| All → `amsha.utils` | file paths, configs | Static utility calls | `YamlUtils.yaml_safe_load()`, `JsonUtils.*` |

---

## 6. Key Findings

1. **Strict Hub-and-Spoke:** `crew_forge` imports from `llm_factory` (4 imports) and `crew_monitor` (2 imports) — never the reverse. Clean unidirectional dependency.
2. **One Architectural Violation:** `output_process` → `crew_forge` creates a **circular dependency** via `CrewParser` import.
3. **Shared Foundation:** `amsha.utils` is the implicit shared layer — used by all 4 modules (12+ import sites).
4. **Loosely Coupled Post-Processing:** `output_process` evaluation tools operate **independently** of the execution pipeline — they consume filesystem artifacts, not runtime objects.
5. **Type-Only Coupling:** `crew_gen` depends on `llm_factory` only for the `LLMType` enum — minimal coupling.
