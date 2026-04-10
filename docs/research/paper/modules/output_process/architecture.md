# Output Process: Architecture & Design

## 1. Architectural Overview

The `output_process` module implements a **three-stage post-processing pipeline** for multi-agent AI outputs: **Optimization** (LLM output sanitization), **Validation** (pre-execution config checks + post-execution file auditing), and **Evaluation** (rubric scoring → relative grading → multi-model consolidation). With **10 Python files** across **3 sub-packages**, it transforms raw, noisy agent outputs into structured, graded, and publication-ready data.

### Layered Pipeline Diagram

```mermaid
%%{init: {'theme': 'base'}}%%
flowchart LR
    classDef opt fill:#fff3e0,stroke:#333,stroke-width:2px;
    classDef val fill:#e8f5e9,stroke:#333,stroke-width:2px;
    classDef eval fill:#e3f2fd,stroke:#333,stroke-width:2px;
    classDef data fill:#f3e5f5,stroke:#333,stroke-width:2px;

    subgraph "Stage 1: Optimization"
        Raw["Raw LLM Output"]:::data
        Cleaner["JsonCleanerUtils"]:::opt
        CleanJSON["Clean JSON"]:::data
    end

    subgraph "Stage 2: Validation"
        ConfigVal["CrewConfigValidator"]:::val
        OutputVal["JSONOutputManager"]:::val
    end

    subgraph "Stage 3: Evaluation"
        Scorer["EvaluationProcessingTool"]:::eval
        Aggregator["EvaluationAggregationTool"]:::eval
        Reporter["EvaluationReportTool"]:::eval
    end

    Raw --> Cleaner --> CleanJSON
    CleanJSON --> Scorer
    Scorer --> Aggregator
    Aggregator --> Reporter
    ConfigVal -.->|Pre-execution| Raw
    OutputVal -.->|Post-execution audit| CleanJSON
```

---

## 2. Sub-Package Structure

| Sub-Package | Files | Purpose |
|:---|:---:|:---|
| `optimization/` | 1 | `JsonCleanerUtils` — Multi-pass LLM output sanitization (fence stripping, concatenation, quote repair) |
| `validation/` | 2 | `CrewConfigValidator` — YAML config validation; `JSONOutputManager` — directory set-difference audit |
| `evaluation/` | 3 | `EvaluationProcessingTool` — rubric-weighted scoring; `EvaluationAggregationTool` — Z-score grading; `EvaluationReportTool` — multi-model pivot consolidation |

**Total:** 10 Python files, 3 sub-packages

---

## 3. Class Design

### Class Diagram

```mermaid
%%{init: {'theme': 'base'}}%%
classDiagram
    note "Three-stage pipeline: Optimization → Validation → Evaluation"

    class JsonCleanerUtils {
        -input_file_path: Path
        -output_file_path: Path
        +process_file() bool
        +process_content(str) bool
        -_clean_and_parse_string(str)$ Any
        -_derive_output_path() Path
        -_get_unique_filepath(Path)$ Path
    }

    class CrewConfigValidator {
        -crew_parser: CrewParser
        +validate(root_path, output_dir) dict
        -_collect_files_to_validate(root) dict
        -_process_and_validate_files(files) dict
        -_generate_summary(details)$ dict
        -_save_report_to_file(report, path)
    }

    class JSONOutputManager {
        -intermediate_dir: Path
        -final_dir: Path
        -output_filepath: str
        +run_comparison() List~Path~
        -_find_json_files(dir)$ List~Path~
        -_find_unique_files(source, comp)$ List~Path~
    }

    class EvaluationProcessingTool {
        -config: Dict
        +run_evaluations()
        -_process_job(config)
        -_calculate_evaluation_score(result, rubric, keys) Dict
        -_get_score_description(score, ranges)$ Tuple
    }

    class EvaluationAggregationTool {
        -config: Dict
        -score_summary: str
        -title: str
        +run()
        -_process_job(config)
        -_apply_relative_grading(df, scale) DataFrame
        -_load_all_evaluations(dir) List
        -_save_to_excel(df, summary, path)
    }

    class EvaluationReportTool {
        -config: Dict
        -grading_scale: Dict
        +run()
        -_generate_evaluation_report(config)
        -_apply_relative_grading(df) DataFrame
    }

    EvaluationProcessingTool ..> EvaluationAggregationTool : feeds
    EvaluationAggregationTool ..> EvaluationReportTool : feeds
    CrewConfigValidator --> CrewParser : uses
```

---

## 4. Evaluation Pipeline: Full 3-Stage Flow

### Sequence Diagram

```mermaid
%%{init: {'theme': 'base'}}%%
sequenceDiagram
    autonumber
    actor User as Researcher
    participant Clean as JsonCleanerUtils
    participant Scorer as EvaluationProcessingTool
    participant Agg as EvaluationAggregationTool
    participant Report as EvaluationReportTool
    participant FS as FileSystem
    participant NP as NumPy/Pandas

    Note over User,Report: Stage 1: Optimization
    User->>Clean: process_file()
    Clean->>FS: read raw LLM output
    Clean->>Clean: Fence extraction → Direct parse → Concat → Quote repair
    Clean->>FS: write clean JSON

    Note over User,Report: Stage 2: Rubric Scoring
    User->>Scorer: run_evaluations()
    Scorer->>FS: Load rubric JSON
    loop For each evaluation file
        Scorer->>FS: Load evaluation JSON
        Scorer->>Scorer: Calculate weighted scores (Σ rk × wk)
        Scorer->>Scorer: Compute F% = Σ Sw / Smax × 100
        Scorer->>Scorer: Classify tier (Weak/Moderate/Strong/Excellent)
        Scorer->>FS: Save scored JSON
    end

    Note over User,Report: Stage 3: Relative Grading
    User->>Agg: run()
    Agg->>FS: Load all scored JSONs from directory
    Agg->>NP: Calculate μ and σ
    loop For each evaluation
        Agg->>Agg: G(si) = Z-score grade (A/B/C/D)
        Agg->>Agg: F(si) = W(G) × si
    end
    Agg->>Agg: CGPA = mean(grade_points)
    Agg->>FS: Save graded JSON + Excel

    Note over User,Report: Stage 4: Multi-Model Consolidation
    User->>Report: run()
    Report->>FS: Load multiple aggregated JSONs
    Report->>Report: Extract eval_model from filename
    Report->>Report: Pivot: gen_model × eval_model → score
    Report->>Report: totalFinalScore = Σ across eval_models
    Report->>Report: Re-apply relative grading on totals
    Report->>FS: Save multi-sheet Excel + JSON
```

---

## 5. JSON Sanitization Pipeline

```mermaid
%%{init: {'theme': 'base'}}%%
flowchart TD
    classDef pass fill:#e3f2fd,stroke:#333;
    classDef fail fill:#ffcdd2,stroke:#333;
    classDef ok fill:#c8e6c9,stroke:#333;

    Input["Raw LLM Output"]
    S1["Stage 1: Strip Markdown Fences"]:::pass
    S2{"Stage 2: json.loads()"}
    S3["Stage 3: Extract {..} objects"]:::pass
    S4["Stage 4: Fix quote errors"]:::pass
    OK["✅ Valid JSON"]:::ok
    FAIL["❌ Parse Failed"]:::fail

    Input --> S1
    S1 --> S2
    S2 -->|Success| OK
    S2 -->|Fail| S3
    S3 -->|Success| OK
    S3 -->|Fail| S4
    S4 -->|Success| OK
    S4 -->|Fail| FAIL
```

---

## 6. Validation Workflow

```mermaid
%%{init: {'theme': 'base'}}%%
flowchart TD
    classDef val fill:#e8f5e9,stroke:#333;
    classDef audit fill:#fff3e0,stroke:#333;

    subgraph "Pre-Execution: Config Validation"
        Walk["os.walk(root)"]:::val
        Parse["CrewParser.parse_agent/task"]:::val
        Valid{"Valid?"}
        Report["Validation Report JSON"]:::val
    end

    subgraph "Post-Execution: Output Audit"
        Inter["intermediate/ directory"]:::audit
        Final["final/ directory"]:::audit
        Diff["Set Difference: I \ F"]:::audit
        Missing["Unprocessed Files List"]:::audit
    end

    Walk --> Parse --> Valid
    Valid -->|Yes| Report
    Valid -->|No| Report
    Inter --> Diff
    Final --> Diff
    Diff --> Missing
```

---

## 7. Cross-Module Dependencies

| Dependency | Direction | Usage |
|:---|:---|:---|
| `crew_forge.seeding.parser.CrewParser` | ← imports | [crew_validator.py:L7](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/output_process/validation/crew_validator.py#L7) uses parser for validation |
| `amsha.utils.json_utils.JsonUtils` | ← imports | Multiple files use shared JSON I/O |
| `amsha.utils.yaml_utils.YamlUtils` | ← imports | Config loading in all tools |

---

## 8. Design Patterns Catalog

| # | Pattern | Implementation | File | Benefit |
|---|:---|:---|:---|:---|
| 1 | **Pipeline** | Optimization → Scoring → Grading → Reporting | Entire module | Sequential transformation of agent output |
| 2 | **Cascading Parser** | 4-stage JSON sanitization | [json_cleaner_utils.py](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/output_process/optimization/json_cleaner_utils.py) | Handles noisy LLM outputs robustly |
| 3 | **Configuration Object** | YAML-driven jobs in all tools | All evaluation tools | Zero-code job definition |
| 4 | **Batch Processor** | Loop over `evaluations`/`aggregation_jobs` | [evaluation_processing_tool.py](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/output_process/evaluation/evaluation_processing_tool.py) | Config-driven multi-job execution |
| 5 | **Statistical Strategy** | Z-score grading with configurable scale | [evaluation_aggregate_tool.py](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/output_process/evaluation/evaluation_aggregate_tool.py) | Population-relative fairness |
| 6 | **Pivot Table** | Multi-model cross-comparison | [evaluation_report_tool.py](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/output_process/evaluation/evaluation_report_tool.py) | Multi-dimensional evaluation |
| 7 | **Set Difference** | Directory comparison for audit | [json_output_validator.py](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/output_process/validation/json_output_validator.py) | Identifies failed processing |
| 8 | **Unique Path Generator** | Counter-based file deduplication | [json_cleaner_utils.py:L48–L67](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/output_process/optimization/json_cleaner_utils.py#L48-L67) | Prevents output overwrites |

---

## 9. Module Metrics

| Metric | Value |
|:---|:---|
| Total Python Files | 10 |
| Sub-Packages | 3 |
| Design Patterns | 8 |
| Diagrams in this Document | 6 |
| Total Source Lines | ~860 |
| External Dependencies | 3 (numpy, pandas, openpyxl) |
| Cross-Module Imports | 3 (CrewParser, JsonUtils, YamlUtils) |
