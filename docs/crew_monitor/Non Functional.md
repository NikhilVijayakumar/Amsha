# Non-Functional Requirements & Constraints

## 1. Dependencies

The `crew_monitor` package adds specific dependencies for optimal operation:

### Essential
*   `psutil`: Required for CPU and Memory tracking.
*   `pandas`: Used by `ContributionAnalyzer` and `ReportingTool` for data manipulation.
*   `openpyxl`: Required by `pandas` for reading/writing Excel files.

### Optional
*   `pynvml` (NVIDIA Management Library):
    *   **Purpose**: Tracking GPU usage.
    *   **Behavior**: The code gracefully handles the absence of this library. If unavailable or if no NVIDIA GPU is detected, GPU metrics are simply skipped without causing runtime errors.

---

## 2. Performance Impact

### Monitoring Overhead
*   **Minimal Intrusion**: The `CrewPerformanceMonitor` uses lightweight `psutil` calls at the start and end of execution. It does *not* poll continuously in the background, ensuring near-zero impact on the agent's performance.
*   **Token Parsing**: Token usage extraction is a simple dictionary lookup and does not impact latency.

---

## 3. Data Persistence

### File-Based
*   Currently, all analysis and reporting tools operate on **local files** (JSON logs and Excel reports).
*   **Scalability**: Suitable for development, testing, and small-to-medium scale deployments. For large-scale production monitoring, consider extending the classes to write to a database (e.g., MongoDB) which is supported by the broader Amsha architecture but not essentially by this specific module yet.
