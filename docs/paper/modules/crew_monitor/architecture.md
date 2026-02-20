# Crew Monitor: Architecture & Design

## 1. Architectural Overview

The `crew_monitor` module implements a **dual-layer observability system** for multi-agent AI workflows: a **Physical Layer** (CPU, RAM, GPU, Token tracking via sandwich profiler) and a **Logical Layer** (feature consensus analysis and report aggregation). With **7 Python files** across **3 sub-packages**, it serves as the "scientific instrument" that produces all experimental data for the research paper.

### Layered Architecture Diagram

```mermaid
%%{init: {'theme': 'base'}}%%
flowchart TD
    classDef consumer fill:#ffd700,stroke:#333,stroke-width:2px;
    classDef physical fill:#ff9f43,stroke:#333,stroke-width:2px;
    classDef logical fill:#bbf,stroke:#333,stroke-width:2px;
    classDef domain fill:#f9f,stroke:#333,stroke-width:2px;
    classDef ext fill:#bfb,stroke:#333,stroke-width:2px;

    subgraph "Consumer Modules"
        DbOrch["DbCrewOrchestrator"]:::consumer
        FileOrch["FileCrewOrchestrator"]:::consumer
    end

    subgraph "Physical Layer (Real-time)"
        Monitor["CrewPerformanceMonitor"]:::physical
    end

    subgraph "Logical Layer (Batch Post-Processing)"
        Analyzer["ContributionAnalyzer"]:::logical
        Reporter["ReportingTool"]:::logical
    end

    subgraph "Domain Layer"
        Schema["Pydantic Schemas"]:::domain
        GPUMetrics["GPUMetrics"]:::domain
        GenMetrics["GeneralMetrics"]:::domain
        PerfMetrics["PerformanceMetrics"]:::domain
    end

    subgraph "External Dependencies"
        PSUtil["psutil"]:::ext
        PyNVML["pynvml"]:::ext
        Pandas["pandas"]:::ext
        OpenPyXL["openpyxl"]:::ext
    end

    DbOrch --> Monitor
    FileOrch --> Monitor
    Monitor --> PSUtil
    Monitor --> PyNVML
    Monitor --> Schema
    Analyzer --> Pandas
    Reporter --> Pandas
    Reporter --> OpenPyXL
    Schema --> GPUMetrics
    Schema --> GenMetrics
    GenMetrics --> PerfMetrics
    GPUMetrics --> PerfMetrics
```

---

## 2. Sub-Package Structure

| Sub-Package | Files | Purpose |
|:---|:---:|:---|
| `domain/` | 1 | Pydantic schemas: `GPUMetrics`, `GeneralMetrics`, `PerformanceMetrics` |
| `service/` | 3 | `CrewPerformanceMonitor` (real-time profiler), `ContributionAnalyzer` (consensus), `ReportingTool` (Excel reporting) |
| Root | 1 | `__init__.py` |

**Total:** 7 Python files, 3 sub-packages

---

## 3. Class Design

### Class Diagram

```mermaid
%%{init: {'theme': 'base'}}%%
classDiagram
    note "Dual-layer observability: Physical + Logical"

    class CrewPerformanceMonitor {
        -model_name: Optional~str~
        -total_tokens: int
        -prompt_tokens: int
        -completion_tokens: int
        -start_time: float
        -end_time: float
        -start_cpu_percent: float
        -end_cpu_percent: float
        -start_memory_usage: int
        -end_memory_usage: int
        -gpu_stats: Dict
        +start_monitoring()
        +stop_monitoring()
        +log_usage(result)
        +get_metrics() Dict
        +get_summary() str
    }

    class ContributionAnalyzer {
        -config: Dict
        +run()
        -_process_job(config)
        -_calculate_feature_contribution(data, total, key)$
        -_save_summary_to_excel(data, file, key)$
    }

    class ReportingTool {
        -config: Dict
        +run()
        -_run_generate_jobs()
        -_run_combine_jobs()
        -_generate_single_report(config)
        -_combine_reports(config)
    }

    class GPUMetrics {
        +utilization_percent: float
        +memory_change_mb: float
        +memory_start_mb: float
        +memory_end_mb: float
    }

    class GeneralMetrics {
        +model_name: Optional~str~
        +total_tokens: int
        +prompt_tokens: int
        +completion_tokens: int
        +duration_seconds: float
        +cpu_usage_end_percent: float
        +memory_usage_change_mb: float
    }

    class PerformanceMetrics {
        +general: GeneralMetrics
        +gpu: Dict~str, GPUMetrics~
    }

    CrewPerformanceMonitor ..> PerformanceMetrics : produces
    PerformanceMetrics --> GeneralMetrics : contains
    PerformanceMetrics --> GPUMetrics : contains
```

---

## 4. Monitoring Lifecycle: Sandwich Pattern

The real-time profiler wraps crew execution in a resource-capture sandwich.

### Sequence Diagram: Full Monitoring Lifecycle

```mermaid
%%{init: {'theme': 'base'}}%%
sequenceDiagram
    autonumber
    participant Orch as DbCrewOrchestrator
    participant Monitor as CrewPerformanceMonitor
    participant PSUtil as psutil
    participant NVML as pynvml
    participant Crew as CrewAI Crew

    Orch->>Monitor: __init__(model_name)

    rect rgb(230, 255, 230)
        note over Monitor,PSUtil: Phase 1: Pre-Execution Snapshot
        Orch->>Monitor: start_monitoring()
        Monitor->>PSUtil: cpu_percent(interval=None)
        PSUtil-->>Monitor: CPU₀%
        Monitor->>PSUtil: virtual_memory().used
        PSUtil-->>Monitor: Mem₀ bytes

        alt GPU_AVAILABLE
            Monitor->>NVML: nvmlInit()
            loop For each GPU i
                Monitor->>NVML: nvmlDeviceGetMemoryInfo(i)
                NVML-->>Monitor: VRAM₀(i)
            end
        end
    end

    rect rgb(255, 248, 230)
        note over Orch,Crew: Phase 2: Agent Execution
        Orch->>Crew: kickoff(inputs)
        Crew-->>Orch: CrewOutput result
    end

    rect rgb(230, 230, 255)
        note over Monitor,NVML: Phase 3: Post-Execution Snapshot
        Orch->>Monitor: stop_monitoring()
        Monitor->>PSUtil: cpu_percent(interval=None)
        PSUtil-->>Monitor: CPU₁%
        Monitor->>PSUtil: virtual_memory().used
        PSUtil-->>Monitor: Mem₁ bytes

        alt GPU_AVAILABLE
            loop For each GPU i
                Monitor->>NVML: nvmlDeviceGetMemoryInfo(i)
                NVML-->>Monitor: VRAM₁(i)
                Monitor->>NVML: nvmlDeviceGetUtilizationRates(i)
                NVML-->>Monitor: Util(i)%
            end
            Monitor->>NVML: nvmlShutdown()
        end
    end

    rect rgb(255, 230, 230)
        note over Monitor: Phase 4: Token Extraction
        Orch->>Monitor: log_usage(result)
        Monitor->>Monitor: Parse token_usage (dict or obj)
    end

    Orch->>Monitor: get_metrics()
    Monitor-->>Orch: {general: {...}, gpu: {...}}
    Orch->>Monitor: get_summary()
    Monitor-->>Orch: formatted_string
```

---

## 5. Contribution Analysis Pipeline

### Sequence Diagram: Batch Consensus Analysis

```mermaid
%%{init: {'theme': 'base'}}%%
sequenceDiagram
    autonumber
    actor Admin as Researcher
    participant Analyzer as ContributionAnalyzer
    participant YAML as Config YAML
    participant JSON as JSON Utils
    participant PD as pandas

    Admin->>Analyzer: __init__(config_path)
    Analyzer->>YAML: yaml_safe_load(path)
    YAML-->>Analyzer: config dict

    Admin->>Analyzer: run()

    loop For each job in analyze_contributions
        Analyzer->>JSON: load_json_from_file(input)
        JSON-->>Analyzer: source_data

        loop For each feature F
            Analyzer->>Analyzer: P(F) = |C_F| / N_total × 100
        end

        alt output_json_file defined
            Analyzer->>JSON: save_json_to_file(data)
        end

        alt output_excel_file defined
            Analyzer->>PD: DataFrame(feature_rows)
            PD->>PD: to_excel(filename)
        end
    end
```

---

## 6. Report Generation & Combination Pipeline

### Activity Diagram: ReportingTool Dual Pipeline

```mermaid
%%{init: {'theme': 'base'}}%%
flowchart TD
    classDef gen fill:#e3f2fd,stroke:#333;
    classDef combine fill:#fff3e0,stroke:#333;
    classDef output fill:#e8f5e9,stroke:#333;

    Start[/"run()"/] --> Check1{generate_reports?}
    Check1 -->|Yes| GenLoop["For each generate job"]:::gen
    Check1 -->|No| Check2

    GenLoop --> LoadDir["Load JSON from directory"]:::gen
    LoadDir --> Extract["Extract features + metrics"]:::gen
    Extract --> Reorder["Reorder columns"]:::gen
    Reorder --> CalcMean["Calculate Mean row"]:::gen
    CalcMean --> SaveExcel1["Save to Excel"]:::output
    SaveExcel1 --> Check2

    Check2{combine_reports?}
    Check2 -->|Yes| CombLoop["For each combine job"]:::combine
    Check2 -->|No| Finish

    CombLoop --> ReadFiles["Read source Excel files"]:::combine
    ReadFiles --> CopySheets["Copy each as sheet"]:::combine
    CopySheets --> Melt["Melt: wide → long format"]:::combine
    Melt --> Pivot["Pivot: Feature × Source × Metric"]:::combine
    Pivot --> SaveExcel2["Save combined workbook"]:::output
    SaveExcel2 --> Finish[/"Complete"/]
```

---

## 7. Cross-Module Integration

The `CrewPerformanceMonitor` is the **only service consumed by other modules** — specifically both `crew_forge` orchestrators:

```mermaid
%%{init: {'theme': 'base'}}%%
flowchart LR
    classDef monitor fill:#ff9f43,stroke:#333;
    classDef consumer fill:#bbf,stroke:#333;

    Monitor["CrewPerformanceMonitor"]:::monitor

    DbOrch["DbCrewOrchestrator<br/>(crew_forge)"]:::consumer
    FileOrch["FileCrewOrchestrator<br/>(crew_forge)"]:::consumer

    DbOrch --> Monitor
    FileOrch --> Monitor
```

| Consumer | Import | Usage |
|:---------|:-------|:------|
| `DbCrewOrchestrator` | [db_crew_orchestrator.py:L5](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/crew_forge/orchestrator/db/db_crew_orchestrator.py#L5) | Wraps crew execution with resource profiling |
| `FileCrewOrchestrator` | [file_crew_orchestrator.py:L5](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/crew_forge/orchestrator/file/file_crew_orchestrator.py#L5) | Wraps crew execution with resource profiling |

---

## 8. Design Patterns Catalog

| # | Pattern | Implementation | File | Benefit |
|---|:---|:---|:---|:---|
| 1 | **Sandwich Profiler** | `start/stop_monitoring()` | [crew_performance_monitor.py](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/crew_monitor/service/crew_performance_monitor.py) | Non-intrusive resource measurement |
| 2 | **Graceful Degradation** | Conditional `pynvml` import | [crew_performance_monitor.py:L5–L9](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/crew_monitor/service/crew_performance_monitor.py#L5-L9) | Works on CPU-only machines |
| 3 | **Polymorphic Extraction** | `log_usage()` dict/obj handling | [crew_performance_monitor.py:L64–L82](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/crew_monitor/service/crew_performance_monitor.py#L64-L82) | Handles varying CrewAI result types |
| 4 | **Batch Processor** | `ContributionAnalyzer.run()` | [contribution_analyzer.py](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/crew_monitor/service/contribution_analyzer.py) | Config-driven multi-job execution |
| 5 | **Configuration Object** | YAML-loaded job configs | [contribution_analyzer.py:L18–L21](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/crew_monitor/service/contribution_analyzer.py#L18-L21) | Externalizes all job parameters |
| 6 | **ETL Pipeline** | `ReportingTool` generate + combine | [reporting_tool.py](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/crew_monitor/service/reporting_tool.py) | JSON → DataFrame → Excel transformation |
| 7 | **Pivot Table** | Melt + pivot for cross-report | [reporting_tool.py:L130–L142](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/crew_monitor/service/reporting_tool.py#L130-L142) | Multi-dimensional comparison |

---

## 9. Module Metrics

| Metric | Value |
|:---|:---|
| Total Python Files | 7 |
| Sub-Packages | 3 |
| Pydantic Models | 3 |
| Design Patterns | 7 |
| Diagrams in this Document | 7 |
| External Dependencies | 4 (psutil, pynvml, pandas, openpyxl) |
| Consumer Modules | 2 (crew_forge DB + File orchestrators) |
| Total Source Lines | ~330 |
