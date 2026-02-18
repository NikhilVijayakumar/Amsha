# Crew Monitor: Architecture & Design

## 1. Architectural Overview

The `crew_monitor` module employs a **Profiler Pattern** for system metrics and a **Batch Processing Pattern** for post-execution analysis. It bridges real-time resource tracking (CPU/GPU) with offline consensus analysis of multi-agent outputs.

### Class Diagram

```mermaid
%%{init: {'theme': 'base'}}%%
classDiagram
    class CrewPerformanceMonitor {
        -start_time: float
        -end_time: float
        -gpu_stats: Dict
        +start_monitoring()
        +stop_monitoring()
        +log_usage(result)
        +get_metrics(): Dict
        +get_summary(): str
    }

    class ContributionAnalyzer {
        -config: Dict
        +run()
        -_process_job(config)
        -_calculate_feature_contribution(data, total, key)
        -_save_summary_to_excel(data, file)
    }

    class ReportingTool {
        +generate_report()
    }

    style CrewPerformanceMonitor fill:#f9f,stroke:#333
    style ContributionAnalyzer fill:#bbf,stroke:#333
```

## 2. Monitoring Lifecycle

The sequence illustrates the "sandwich" pattern where monitoring wraps the core execution logic.

### Sequence Diagram: Resource Tracking

```mermaid
%%{init: {'theme': 'base'}}%%
sequenceDiagram
    autonumber
    participant Client
    participant Monitor as CrewPerformanceMonitor
    participant System as PSUtil/NVML
    participant Crew as CrewAgent

    Client->>Monitor: start_monitoring()
    Monitor->>System: Get CPU/Mem/GPU Snapshot
    System-->>Monitor: State T0
    
    rect rgb(240, 248, 255)
        note right of Client: Core Execution
        Client->>Crew: kickoff()
        Crew-->>Client: Result
    end

    Client->>Monitor: stop_monitoring()
    Monitor->>System: Get CPU/Mem/GPU Snapshot
    System-->>Monitor: State T1
    
    Client->>Monitor: log_usage(Result)
    Monitor->>Monitor: Parse Token Counts
    
    Client->>Monitor: get_metrics()
    Monitor-->>Client: {cpu: X%, mem: Ymb, tokens: Z}
```

## 3. Analysis Pipeline

The batch process for analyzing consensus across multiple model outputs.

### Activity Diagram: Contribution Analysis

```mermaid
%%{init: {'theme': 'base'}}%%
flowchart LR
    A[Start Job] --> B{Load Config}
    B -->|Valid| C[Load JSON Data]
    B -->|Invalid| Z[Exit]
    
    C --> D[Iterate Features]
    D --> E[Count Contributors]
    E --> F[Calculate %]
    F --> G[Update Dictionary]
    
    G --> H{Output Type?}
    H -->|JSON| I[Save JSON]
    H -->|Excel| J[Generate Excel Report]
    H -->|Both| I & J
    
    I --> K[End Job]
    J --> K
```
