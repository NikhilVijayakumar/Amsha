# Technical Documentation

## 1. Class Reference

### `CrewPerformanceMonitor`
**Path**: `nikhil.amsha.crew_monitor.service.crew_performance_monitor`

*   `__init__(model_name: Optional[str] = None)`
*   `start_monitoring()`: Records start time, CPU, memory, and GPU stats.
*   `stop_monitoring()`: Records end stats and calculates resource usage.
*   `log_usage(result: Any)`: Parses a `CrewOutput` object to extract token usage (`total_tokens`, `prompt_tokens`, `completion_tokens`).
*   `get_metrics() -> Dict[str, Any]`: Returns a structured dictionary of all collected metrics.
*   `get_summary() -> str`: Returns a human-readable string summary.

### `ContributionAnalyzer`
**Path**: `nikhil.amsha.crew_monitor.service.contribution_analyzer`

*   `__init__(config_path: str)`: Loads YAML configuration.
*   `run()`: Executes all analysis jobs defined in `analyze_contributions`.

### `ReportingTool`
**Path**: `nikhil.amsha.crew_monitor.service.reporting_tool`

*   `__init__(config_path: str)`: Loads YAML configuration.
*   `run()`: Executes jobs in `generate_reports` and `combine_reports`.

---

## 2. Configuration Schema

The tools rely on a YAML configuration file. Below are the key sections.

### Contribution Analysis (`analyze_contributions`)

```yaml
analyze_contributions:
  - name: "Analysis Job Name"
    input_file: "path/to/input.json"
    output_json_file: "path/to/output.json"
    output_excel_file: "path/to/output.xlsx"
    total_llms: 5  # Total number of agents/models involved
    options:
      feature_list_key: "features"  # JSON key containing the list of items
```

### Report Generation (`generate_reports`)

```yaml
generate_reports:
  - name: "Report Job Name"
    input_directory: "path/to/json_logs/"
    output_filename: "path/to/report.xlsx"
    options:
      feature_name_key: "featureName"
      evaluation_list_key: "evaluation"
      metric_name_key: "metricName"
      score_key: "weightedScore"
      summary_key: "scoreSummary"
```

### Report Combination (`combine_reports`)

```yaml
combine_reports:
  - name: "Combine Job Name"
    output_filename: "path/to/combined_summary.xlsx"
    files_and_columns:
      "path/to/report1.xlsx": ["Metric1_Score", "Metric2_Score"]
      "path/to/report2.xlsx": ["Metric1_Score", "Metric2_Score"]
```

---

## 3. Data Models (`pydantic`)

**Path**: `nikhil.amsha.crew_monitor.domain.schemas`

### `PerformanceMetrics`
The root monitoring object.
*   `general`: `GeneralMetrics`
*   `gpu`: `Dict[str, GPUMetrics]`

### `GeneralMetrics`
*   `model_name`: `Optional[str]`
*   `total_tokens`, `prompt_tokens`, `completion_tokens`: `int`
*   `duration_seconds`: `float`
*   `cpu_usage_end_percent`: `float`
*   `memory_usage_change_mb`: `float`

### `GPUMetrics`
*   `utilization_percent`: `float`
*   `memory_change_mb`: `float`
