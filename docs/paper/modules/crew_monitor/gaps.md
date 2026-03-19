# Crew Monitor: Research Gap Analysis

This document identifies gaps against Scopus-indexed publication standards, categorized by severity and effort.

---

## 1. Quality Assurance Gaps

### GAP QA-001: Zero Unit Tests for All Services (CRITICAL)

The `tests/unit/crew_monitor/` directory contains **zero test files**. All three services (`CrewPerformanceMonitor`, `ContributionAnalyzer`, `ReportingTool`) are completely unverified.

- **Severity:** Critical ⛔
- **Impact:** This module IS the scientific instrument — if metrics are wrong, **all experimental data in the paper is invalid**. This is a double risk: module reliability AND paper credibility.
- **Source:** No test files in `tests/unit/crew_monitor/`.
- **Recommendation:** Priority test targets:
  1. `CrewPerformanceMonitor.get_metrics()` — Mock `psutil` and `pynvml`, verify delta calculations
  2. `ContributionAnalyzer._calculate_feature_contribution()` — Test with known contributor counts
  3. `ReportingTool._generate_single_report()` — Verify Mean row calculation
  4. `ReportingTool._combine_reports()` — Verify melt-pivot output shape
- **Estimated Effort:** 3 days

### GAP QA-002: No Schema Validation in Monitor (MODERATE)

The `CrewPerformanceMonitor.get_metrics()` returns a raw dict. The Pydantic `PerformanceMetrics` schema in `domain/schemas.py` is **defined but never used** in the monitor itself.

- **Severity:** Moderate
- **Impact:** No guarantee that returned metrics conform to the schema.
- **Source:** [schemas.py](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/crew_monitor/domain/schemas.py) defined but not imported in [crew_performance_monitor.py](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/crew_monitor/service/crew_performance_monitor.py).
- **Recommendation:** Have `get_metrics()` return `PerformanceMetrics` instead of raw dict.
- **Estimated Effort:** 0.5 days

---

## 2. Experimental Gaps

### GAP EXP-001: No Observer Effect Analysis (CRITICAL)

No data exists on how much the monitor itself affects the measured system — the classic "Observer Effect" in instrumentation.

- **Severity:** Critical ⛔
- **Description:** `psutil.cpu_percent()` and `pynvml` calls consume CPU/memory themselves. Without quantifying this overhead, all measurements have an unknown systematic error.
- **Source:** [crew_performance_monitor.py:L27–L62](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/crew_monitor/service/crew_performance_monitor.py#L27-L62)
- **Recommendation:** Run identical crews with and without monitoring, compare execution times.
- **Estimated Effort:** 1 day

### GAP EXP-002: No Consensus Accuracy Validation (CRITICAL)

The consensus metric $P(F)$ is never validated against ground truth. There is no evidence that higher consensus correlates with higher accuracy.

- **Severity:** Critical ⛔
- **Description:** The claim that "100% consensus = high confidence feature" is assumed but untested. All LLMs could unanimously hallucinate.
- **Source:** [contribution_analyzer.py:L65–L79](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/crew_monitor/service/contribution_analyzer.py#L65-L79)
- **Recommendation:** Create labeled ground truth dataset, compute correlation between $P(F)$ and accuracy.
- **Estimated Effort:** 3 days

### GAP EXP-003: No Statistical Significance (MODERATE)

The Mean row in `ReportingTool` reports arithmetic mean without confidence intervals or standard deviation.

- **Severity:** Moderate
- **Source:** [reporting_tool.py:L79–L81](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/crew_monitor/service/reporting_tool.py#L79-L81) — Only computes `mean()`.
- **Recommendation:** Add std, median, and 95% confidence interval rows.
- **Estimated Effort:** 0.5 days

---

## 3. Implementation Gaps

### GAP HW-001: NVIDIA-Only GPU Support (MODERATE)

GPU monitoring depends on `pynvml` which only supports NVIDIA GPUs.

- **Severity:** Moderate
- **Description:** AMD (ROCm), Apple Silicon (MPS), and Intel ARC GPUs are unsupported.
- **Source:** [crew_performance_monitor.py:L6](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/crew_monitor/service/crew_performance_monitor.py#L6) — `import pynvml`
- **Recommendation:** Abstract GPU interface behind a Protocol, implement per-vendor adapters.
- **Estimated Effort:** 2 days

### GAP IMPL-001: Synchronous Blocking Calls (MODERATE)

All `psutil` and `pynvml` calls block the main thread synchronously.

- **Severity:** Moderate
- **Description:** The monitoring overhead is injected into the critical path. In performance-sensitive scenarios, this adds latency to the measured execution.
- **Source:** [crew_performance_monitor.py:L31–L32, L48–L49](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/crew_monitor/service/crew_performance_monitor.py#L31-L32)
- **Recommendation:** Offload snapshots to a background thread.
- **Estimated Effort:** 1 day

### GAP IMPL-002: GPU Memory Leak Risk (MINOR)

If `stop_monitoring()` is never called (e.g., exception during crew execution), `pynvml.nvmlShutdown()` is never invoked.

- **Severity:** Minor
- **Description:** NVML resource handle may leak if the lifecycle is interrupted.
- **Source:** [crew_performance_monitor.py:L60](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/crew_monitor/service/crew_performance_monitor.py#L60) — `nvmlShutdown()` only in `stop_monitoring()`
- **Recommendation:** Use context manager (`__enter__` / `__exit__`) pattern for automatic cleanup.
- **Estimated Effort:** 0.5 days

### GAP IMPL-003: CPU Snapshot vs Average (MINOR)

`cpu_percent(interval=None)` returns an instantaneous snapshot, not an average over the execution window.

- **Severity:** Minor
- **Description:** A single-point CPU reading is unreliable (could be 5% or 95% depending on the instant).
- **Source:** [crew_performance_monitor.py:L31](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/crew_monitor/service/crew_performance_monitor.py#L31) — `interval=None`
- **Recommendation:** Sample CPU at intervals during execution and compute average.
- **Estimated Effort:** 1 day

### GAP IMPL-004: Private Method Used as Public API (MINOR)

`JsonUtils._load_json_from_directory()` is called directly in `ReportingTool` despite the leading underscore indicating it's private.

- **Severity:** Minor
- **Source:** [reporting_tool.py:L51](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/crew_monitor/service/reporting_tool.py#L51)
- **Recommendation:** Either make it public (`load_json_from_directory`) or add a proper public method.
- **Estimated Effort:** 5 minutes

---

## 4. Gap Summary Matrix

| Gap ID | Category | Severity | Effort | Priority |
|--------|----------|----------|--------|----------|
| QA-001 | Testing | Critical ⛔ | 3 days | P0 |
| QA-002 | Schema | Moderate | 0.5 day | P2 |
| EXP-001 | Benchmark | Critical ⛔ | 1 day | P0 |
| EXP-002 | Validation | Critical ⛔ | 3 days | P0 |
| EXP-003 | Statistics | Moderate | 0.5 day | P2 |
| HW-001 | Hardware | Moderate | 2 days | P2 |
| IMPL-001 | Performance | Moderate | 1 day | P2 |
| IMPL-002 | Resource | Minor | 0.5 day | P3 |
| IMPL-003 | Accuracy | Minor | 1 day | P3 |
| IMPL-004 | API | Minor | 5 min | P3 |

**Total Critical Gaps:** 3 | **Total Gaps:** 10 | **Estimated Total Effort:** ~13 days
