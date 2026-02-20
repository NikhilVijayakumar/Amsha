# Crew Monitor: Mathematical Foundations

This document formalizes the algorithms within the `crew_monitor` module, covering resource delta calculation, token usage parsing, feature consensus quantification, report aggregation with statistical summation, and Excel pivot-table generation.

---

## 1. Resource Usage Delta Calculation (Sandwich Profiler)

The `CrewPerformanceMonitor` captures the computational cost of an agent execution window by measuring the state change of system resources between two temporal checkpoints using a "sandwich" pattern.

### Code Verification
- **Source:** [crew_performance_monitor.py](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/crew_monitor/service/crew_performance_monitor.py)
- **Lines:** L27–L62 (`start_monitoring`, `stop_monitoring`), L84–L123 (`get_metrics`)

### Formalization

Let $S(t)$ be the system state vector at time $t$:

$$
S(t) = \langle \texttt{Mem}(t),\; \texttt{CPU}(t),\; \{G_i(t)\}_{i=0}^{N_{gpu}-1} \rangle
$$

Where each GPU state $G_i(t) = (\texttt{VRAM}_i(t),\; \texttt{Util}_i(t))$.

The monitoring sandwich captures two states $S(t_0)$ and $S(t_1)$ around the execution:

$$
\texttt{Profile}(execution) = \left( S(t_0),\; execution(),\; S(t_1) \right)
$$

**Derived Metrics:**

| Metric | Formula | Code | Line |
|:---|:---|:---|:---|
| Duration | $\Delta_t = t_1 - t_0$ | `end_time - start_time` | L89 |
| Memory Delta | $\Delta_{mem} = \frac{\texttt{Mem}(t_1) - \texttt{Mem}(t_0)}{1024^2}$ (MB) | `memory_diff_mb` | L90 |
| GPU VRAM Delta | $\Delta_{vram_i} = \frac{\texttt{VRAM}_i(t_1) - \texttt{VRAM}_i(t_0)}{1024^2}$ (MB) | `end_mem - start_mem` | L118 |
| CPU Usage | $\texttt{CPU}_{end} = \texttt{psutil.cpu\_percent}(t_1)$ | `end_cpu_percent` | L48 |
| GPU Utilization | $\texttt{Util}_i(t_1)$ | `utilization.gpu` | L59 |

### GPU Graceful Degradation

The module uses **conditional import** for GPU monitoring:

$$
\texttt{GPU\_AVAILABLE} = \begin{cases}
\texttt{True} & \text{if } \texttt{import pynvml} \text{ succeeds} \\
\texttt{False} & \text{otherwise (skip GPU metrics)}
\end{cases}
$$

This allows operation on CPU-only machines without errors (L5–L9).

### Complexity
- **Time:** $O(N_{gpu})$ per snapshot — Linear in number of GPUs.
- **Space:** $O(N_{gpu})$ for storing per-GPU start/end memory values.

---

## 2. Token Usage Parsing (Polymorphic Extraction)

The `log_usage()` method extracts token consumption from CrewAI results using a polymorphic extraction pattern that handles both dictionary and object-style responses.

### Code Verification
- **Source:** [crew_performance_monitor.py](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/crew_monitor/service/crew_performance_monitor.py)
- **Lines:** L64–L82

### Formalization

Let $R$ be the CrewAI result object. The extraction function $\mathcal{E}: R \to \mathbb{Z}^3$:

$$
\mathcal{E}(R) = \begin{cases}
(R.\texttt{token\_usage}[T_p],\; R.\texttt{token\_usage}[T_c],\; R.\texttt{token\_usage}[T_t]) & \text{if } \texttt{isinstance}(usage, dict) \\
(\texttt{getattr}(usage, T_p, 0),\; \texttt{getattr}(usage, T_c, 0),\; \texttt{getattr}(usage, T_t, 0)) & \text{if } \texttt{hasattr}(usage, T_t) \\
(0,\; 0,\; 0) & \text{otherwise (warning logged)}
\end{cases}
$$

Where $T_p = \texttt{prompt\_tokens}$, $T_c = \texttt{completion\_tokens}$, $T_t = \texttt{total\_tokens}$.

### Complexity
- **Time:** $O(1)$ — Constant-time attribute access.
- **Space:** $O(1)$ — Three integer fields.

---

## 3. Feature Consensus Quantification

The `ContributionAnalyzer` quantifies the reliability of agent-generated features by computing a **consensus percentage** across a population of $N$ LLMs.

### Code Verification
- **Source:** [contribution_analyzer.py](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/crew_monitor/service/contribution_analyzer.py)
- **Lines:** L65–L79 (`_calculate_feature_contribution`)

### Formalization

Let $\mathcal{L}$ be the set of all participating LLMs, $|\mathcal{L}| = N_{total}$.
Let $\mathcal{F} = \{F_1, F_2, \dots, F_M\}$ be the set of extracted features.
Let $C_k \subseteq \mathcal{L}$ be the subset of LLMs that contributed to feature $F_k$.

The **Contribution Percentage** $P: \mathcal{F} \to [0, 100]$:

$$
P(F_k) = \left( \frac{|C_k|}{N_{total}} \right) \times 100
$$

### Confidence Interpretation

$$
\texttt{Confidence}(F_k) = \begin{cases}
\texttt{UNANIMOUS} & \text{if } P(F_k) = 100\% \\
\texttt{MAJORITY} & \text{if } 50\% < P(F_k) < 100\% \\
\texttt{MINORITY} & \text{if } P(F_k) \leq 50\% \\
\texttt{SINGULARITY} & \text{if } |C_k| = 1
\end{cases}
$$

### Guard Clause

$$
\texttt{Valid}(N_{total}) \iff N_{total} > 0 \quad \text{(prevents division by zero, L70–L72)}
$$

### Complexity
- **Time:** $O(M \times \bar{K})$ where $M$ = features, $\bar{K}$ = avg contributors per feature.
- **Space:** $O(1)$ — In-place modification of existing feature dictionary.

### Variable Mapping

| LaTeX Symbol | Code Variable | File | Line |
| :--- | :--- | :--- | :--- |
| $N_{total}$ | `total_llms` | `contribution_analyzer.py` | L46 |
| $|C_k|$ | `num_contributors` | `contribution_analyzer.py` | L76 |
| $P(F_k)$ | `percentage` | `contribution_analyzer.py` | L77 |
| $\mathcal{F}$ | `feature_list` | `contribution_analyzer.py` | L74 |

---

## 4. Batch Job Orchestration Pipeline

The `ContributionAnalyzer` processes multiple analysis jobs sequentially from a YAML configuration, implementing a batch processing pipeline.

### Code Verification
- **Source:** [contribution_analyzer.py](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/crew_monitor/service/contribution_analyzer.py)
- **Lines:** L25–L61 (`run`, `_process_job`)

### Formalization

Let $\mathcal{J} = \{J_1, J_2, \dots, J_P\}$ be the set of analysis jobs defined in the YAML config.

Each job $J_i$ is a 5-tuple:

$$
J_i = (\texttt{name}_i,\; \texttt{input}_i,\; N_i,\; \texttt{out\_json}_i,\; \texttt{out\_excel}_i)
$$

The batch pipeline:

$$
\texttt{run}() = \bigcirc_{i=1}^{P} \texttt{process}(J_i) = \bigcirc_{i=1}^{P} \left[ \texttt{Load}(J_i) \to \texttt{Analyze}(J_i) \to \texttt{Export}(J_i) \right]
$$

Export fan-out:

$$
\texttt{Export}(J_i) = \begin{cases}
\texttt{SaveJSON}(J_i) & \text{if } \texttt{out\_json}_i \neq \bot \\
\texttt{SaveExcel}(J_i) & \text{if } \texttt{out\_excel}_i \neq \bot \\
\texttt{SaveJSON}(J_i) \land \texttt{SaveExcel}(J_i) & \text{if both defined}
\end{cases}
$$

---

## 5. Report Aggregation with Statistical Summation

The `ReportingTool` implements a multi-stage data transformation pipeline: JSON directory → DataFrame → Column reordering → Mean calculation → Excel export.

### Code Verification
- **Source:** [reporting_tool.py](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/crew_monitor/service/reporting_tool.py)
- **Lines:** L42–L90 (`_generate_single_report`)

### Formalization

**Stage 1 — Data Extraction:** For each JSON file $f_j$ in directory $D$:

$$
\texttt{row}(f_j) = \left\{ \texttt{Feature}: f_j[\texttt{name}],\; \forall m_k \in \texttt{eval} : m_k.\texttt{metric} \mapsto m_k.\texttt{score} \right\}
$$

**Stage 2 — Mean Aggregation:** For the matrix of numeric columns:

$$
\bar{x}_c = \frac{1}{|rows|} \sum_{r=1}^{|rows|} x_{r,c} \quad \forall c \in \texttt{numeric\_cols}
$$

This is appended as a summary row at the bottom of the Excel sheet (L79–L81).

**Stage 3 — Cross-Report Combination:** The `_combine_reports` method merges multiple Excel files using a melt-pivot transformation:

$$
\texttt{Melt}(df, \texttt{id\_vars}, \texttt{value\_vars}) \xrightarrow{\texttt{pivot}} \texttt{CrossReport}[Feature \times (Source, Metric)]
$$

### Complexity
- **Time:** $O(|D| \times |evals| + |rows| \times |cols|)$ for generation; $O(|files| \times |rows|)$ for combination.
- **Space:** $O(|rows| \times |cols|)$ per DataFrame.

---

## 6. Pydantic Metrics Schema Hierarchy

The domain layer defines a typed schema for performance metrics using Pydantic.

### Code Verification
- **Source:** [schemas.py](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/crew_monitor/domain/schemas.py) (L1–L23)

### Formalization

$$
\texttt{PerformanceMetrics} = \texttt{GeneralMetrics} \times \{gpu_i \mapsto \texttt{GPUMetrics}\}
$$

$$
\texttt{GeneralMetrics} = (m_{name}^?,\; T_{total},\; T_{prompt},\; T_{comp},\; \Delta_t,\; CPU_{\%},\; \Delta_{mem},\; Mem_0,\; Mem_1)
$$

$$
\texttt{GPUMetrics} = (\texttt{Util}_{\%},\; \Delta_{vram},\; \texttt{VRAM}_0,\; \texttt{VRAM}_1)
$$

### Type Safety
- **Strict typing:** All fields have explicit types (float, int, Optional[str]).
- **Default values:** Token fields default to 0, allowing partial metrics.

---

## Algorithm Index

| # | Algorithm | Source File | Lines | Complexity |
|---|-----------|------------|-------|------------|
| 1 | Sandwich Profiler (Resource Delta) | `crew_performance_monitor.py` | L27–L123 | $O(N_{gpu})$ |
| 2 | Token Usage Parsing | `crew_performance_monitor.py` | L64–L82 | $O(1)$ |
| 3 | Feature Consensus Quantification | `contribution_analyzer.py` | L65–L79 | $O(M \times \bar{K})$ |
| 4 | Batch Job Pipeline | `contribution_analyzer.py` | L25–L61 | $O(P \times M)$ |
| 5 | Report Aggregation + Mean | `reporting_tool.py` | L42–L90 | $O(|D| \times |evals|)$ |
| 6 | Cross-Report Melt-Pivot | `reporting_tool.py` | L92–L144 | $O(|files| \times |rows|)$ |
| 7 | Pydantic Schema Validation | `schemas.py` | L1–L23 | $O(|fields|)$ |
