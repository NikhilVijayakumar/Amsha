# Crew Monitor: Research Gap Analysis

## 1. Quality Assurance Gaps (CRITICAL)

### Missing Unit Tests
The `tests/unit/crew_monitor` directory structure exists but contains **zero test files**. The monitoring logic and contribution analysis are unverified.

- **Gap ID:** QA-003
- **Severity:** Critical +
- **Description:** No automated verification of metrics calculation or CSV/Excel export.
- **Impact:** High risk of incorrect performance data in the final paper.
- **Recommendation:** Implement `test-scaffolder` to verify `CrewPerformanceMonitor` with mock `psutil`/`pynvml`.

## 2. Implementation Gaps

### Hardware-Specific Dependency (Minor)
 The module relies on `pynvml` which is specific to NVIDIA GPUs.

- **Gap ID:** HW-001
- **Severity:** Minor
- **Description:** No support for AMD (ROCm) or Apple Silicon (MPS) acceleration tracking.
- **Source Reference:** `src/nikhil/amsha/crew_monitor/service/crew_performance_monitor.py:6` (`import pynvml`)
- **Recommendation:** Abstract the GPU interface to support `torch.cuda` or platform-agnostic libraries.

### Synchronous Blocking Calls (Moderate)
The `psutil` and file I/O operations are synchronous.

- **Gap ID:** PERF-003
- **Severity:** Moderate
- **Description:** Monitoring calls block the main thread, potentially affecting the observed agent latency.
- **Recommendation:** Offload monitoring snapshots to a background thread.

## 3. Experimental Gaps

### Lack of Overhead Analysis
There is no data on the "Observer Effect" - how much the monitor itself slows down the system.

- **Gap ID:** EXP-001
- **Severity:** Minor
- **Recommendation:** Measure system performance with and without the monitor attached.
