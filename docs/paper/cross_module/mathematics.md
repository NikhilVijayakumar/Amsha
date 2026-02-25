# Cross-Module Mathematical Models

This document formalizes the **system-wide mathematical models** that emerge from cross-module interactions in the Amsha framework. Unlike per-module mathematics (which focus on internal algorithms), this document captures the **compositional mathematics** — how algorithms from different modules combine to produce system-level properties and emergent behavior.

---

## 1. End-to-End Execution Pipeline: Compositional Model

The complete Amsha execution pipeline composes algorithms from 4 modules into a single formally-definable system function. This section models the full lifecycle from configuration to evaluated output.

### Code Verification
- **crew_forge orchestrator:** [db_crew_orchestrator.py:L22–L38](file:///e:/Python/Amsha/src/nikhil/amsha/crew_forge/orchestrator/db/db_crew_orchestrator.py#L22-L38)
- **llm_factory builder:** [llm_builder.py:L15–L48](file:///e:/Python/Amsha/src/nikhil/amsha/llm_factory/service/llm_builder.py#L15-L48)
- **crew_monitor profiler:** [crew_performance_monitor.py:L27–L50](file:///e:/Python/Amsha/src/nikhil/amsha/crew_monitor/service/crew_performance_monitor.py#L27-L50)
- **output_process evaluator:** [evaluation_processing_tool.py](file:///e:/Python/Amsha/src/nikhil/amsha/output_process/evaluation/evaluation_processing_tool.py)

### Formalization

Let the system function $\Phi$ be defined as the composition of four module-level transformations:

$$
\Phi(config, inputs) = \texttt{Evaluate} \circ \texttt{Monitor} \circ \texttt{Execute} \circ \texttt{Provision}(config, inputs)
$$

Expanding each stage:

**Stage 1 — LLM Provisioning** ($\texttt{Provision}: \texttt{Config} \to \texttt{LLM}$):

$$
\texttt{Provision}(config) = \mathcal{I}\left(\mathcal{R}(u, k_{opt}), \mathcal{P}(u)\right)
$$

Where $\mathcal{R}$ is the hierarchical config resolution from `llm_factory` (see `llm_factory/mathematics.md §1`) and $\mathcal{I}$ is the conditional instantiation (see `llm_factory/mathematics.md §2`).

**Stage 2 — Crew Execution** ($\texttt{Execute}: \texttt{LLM} \times \texttt{Blueprint} \times \texttt{Inputs} \to \texttt{RawOutput}$):

$$
\texttt{Execute}(\ell, \mathcal{B}, I) = \texttt{Crew}\left(\mathcal{M}(\mathcal{B}, \ell)\right).\texttt{kickoff}(I)
$$

Where $\mathcal{M}$ is the Blueprint Materialization from `crew_forge` (see `crew_forge/mathematics.md §3`).

**Stage 3 — Monitored Execution** ($\texttt{Monitor}: \texttt{Execution} \to \texttt{Output} \times \texttt{Metrics}$):

$$
\texttt{Monitor}(\texttt{exec}) = \left( \texttt{exec}(), \; S(t_1) - S(t_0) \right)
$$

Where $S(t) = \left(\texttt{CPU}_\%(t), \texttt{RAM}(t), \texttt{VRAM}(t), \texttt{GPU}_\%(t)\right)$ is the system state vector from `crew_monitor` (see `crew_monitor/mathematics.md §1`).

**Stage 4 — Post-Processing** ($\texttt{Evaluate}: \texttt{RawOutput} \to \texttt{GradedReport}$):

$$
\texttt{Evaluate}(R) = \texttt{Grade}\left(\texttt{Score}\left(\texttt{Clean}(R)\right)\right)
$$

Where $\texttt{Clean}$ is the 3-stage cascade parser, $\texttt{Score}$ is rubric-weighted scoring, and $\texttt{Grade}$ is Z-score relative grading from `output_process` (see `output_process/mathematics.md §1–3`).

### Full System Composition

$$
\Phi(config, I) = \texttt{Grade}\left(\texttt{Score}\left(\texttt{Clean}\left(\pi_1\left(\texttt{Monitor}\left(\lambda.\; \texttt{Crew}\left(\mathcal{M}(\mathcal{B}, \mathcal{I}(\mathcal{R}(u), \mathcal{P}(u)))\right).\texttt{kickoff}(I)\right)\right)\right)\right)\right)
$$

Where $\pi_1$ extracts the output component from the monitored result tuple.

### Complexity Analysis
- **End-to-End Time:** $O(T_{LLM\_init}) + O(|steps| \times T_{agent\_create}) + O(T_{crew\_exec}) + O(|C| + n \log n)$
- **End-to-End Space:** $O(|config|) + O(|A| + |T|) + O(|S|) + O(|R|)$

---

## 2. Privacy-Guarded Execution Invariant

The system enforces a **privacy invariant** across the execution lifecycle: no telemetry data is transmitted at any point during provisioning, execution, or monitoring.

### Code Verification
- **Telemetry disabling:** [llm_utils.py:L10–L24](file:///e:/Python/Amsha/src/nikhil/amsha/llm_factory/utils/llm_utils.py#L10-L24)
- **Pre-factory guard:** [llm_builder.py:L20](file:///e:/Python/Amsha/src/nikhil/amsha/llm_factory/service/llm_builder.py#L20)
- **Orchestrator integration:** [db_crew_orchestrator.py:L22–L38](file:///e:/Python/Amsha/src/nikhil/amsha/crew_forge/orchestrator/db/db_crew_orchestrator.py#L22-L38)

### Formalization

Define the **Privacy Predicate** $\mathcal{P}_{priv}$ as:

$$
\mathcal{P}_{priv}(\Phi) \iff \forall t \in [t_0, t_1] : \texttt{Telemetry}(t) = \bot
$$

This is guaranteed by the composition of two mechanisms:

**Layer 1 — Environment Variable:**

$$
\texttt{env}[\texttt{OTEL\_SDK\_DISABLED}] = \texttt{true} \implies \nexists \; \texttt{OTel.export}(t)
$$

**Layer 2 — Reflective Neutralization:**

$$
\forall m \in \texttt{Callable}(\texttt{Telemetry}) \setminus \texttt{Dunder} : m \leftarrow \lambda \texttt{*args}: \bot
$$

The composition ensures defense-in-depth:

$$
\mathcal{P}_{priv} = \mathcal{P}_{env} \lor \mathcal{P}_{reflect}
$$

**System-Level Implication:** The entire execution pipeline — from `LLMBuilder.build_creative()` through `crew.kickoff()` to `monitor.get_metrics()` — operates under the privacy guarantee, producing a property that no individual module enforces alone.

---

## 3. Cross-Module Data Flow Algebra

The data transformations across module boundaries form a typed algebra. Each cross-module call has a formally definable input/output type contract.

### Code Verification
- **crew_forge → llm_factory:** [amsha_crew_db_application.py:L31–L41](file:///e:/Python/Amsha/src/nikhil/amsha/crew_forge/orchestrator/db/amsha_crew_db_application.py#L31-L41)
- **crew_forge → crew_monitor:** [db_crew_orchestrator.py:L22–L28](file:///e:/Python/Amsha/src/nikhil/amsha/crew_forge/orchestrator/db/db_crew_orchestrator.py#L22-L28)
- **output_process → crew_forge:** [crew_validator.py:L7](file:///e:/Python/Amsha/src/nikhil/amsha/output_process/validation/crew_validator.py#L7)

### Formalization

Define the **Module Interface Types**:

$$
\tau_{LLM} = \texttt{LLMBuildResult} = \texttt{LLM} \times \texttt{str}
$$

$$
\tau_{Monitor} = \texttt{PerformanceMetrics} = \left\{ \texttt{general}: \texttt{GeneralMetrics}, \; \texttt{gpu}: \texttt{GPUMetrics} \right\}
$$

$$
\tau_{Parse} = \texttt{AgentRequest} \cup \texttt{TaskRequest}
$$

The **Cross-Module Function Signatures**:

| Boundary | Function | Type Signature |
|:---|:---|:---|
| `crew_forge` → `llm_factory` | `LLMContainer.build_creative()` | $\texttt{YAMLPath} \to \tau_{LLM}$ |
| `crew_forge` → `crew_monitor` | `CrewPerformanceMonitor(model)` | $\texttt{str} \to \texttt{Monitor}$ |
| `crew_monitor` → `crew_forge` | `monitor.get_metrics()` | $\texttt{void} \to \tau_{Monitor}$ |
| `output_process` → `crew_forge` | `CrewParser.parse_agent()` | $\texttt{FilePath} \to \tau_{Parse}$ |

### Data Flow Conservation Law

The system satisfies a data conservation property at each boundary — no information is created or destroyed at cross-module boundaries, only transformed:

$$
\forall (M_i \to M_j) : \texttt{Schema}(\texttt{out}(M_i)) \subseteq \texttt{Schema}(\texttt{in}(M_j))
$$

Verified instances:
- `llm_factory` outputs `LLMBuildResult(llm, model_name)` → `crew_forge` consumes both fields
- `crew_monitor` outputs `metrics{general, gpu}` → `crew_forge` consumes via `get_metrics()`
- `crew_forge` outputs `CrewParser` → `output_process` uses `parse_agent()` and `parse_task()`

---

## 4. Configuration Universality Theorem

All 4 modules use YAML-based configuration through a common utility layer (`amsha.utils`). This creates a mathematical property: the entire system behavior is parameterizable through declarative configuration.

### Code Verification
- **crew_forge:** [crew_parser.py](file:///e:/Python/Amsha/src/nikhil/amsha/crew_forge/seeding/parser/crew_parser.py) — `YamlUtils.yaml_safe_load()`
- **llm_factory:** [llm_settings.py](file:///e:/Python/Amsha/src/nikhil/amsha/llm_factory/settings/llm_settings.py) — `YamlUtils.yaml_safe_load()`
- **crew_monitor:** [contribution_analyzer.py:L18](file:///e:/Python/Amsha/src/nikhil/amsha/crew_monitor/service/contribution_analyzer.py#L18) — `YamlUtils.yaml_safe_load()`
- **output_process:** [evaluation_processing_tool.py:L14](file:///e:/Python/Amsha/src/nikhil/amsha/output_process/evaluation/evaluation_processing_tool.py#L14) — `YamlUtils.yaml_safe_load()`

### Formalization

Let $\mathcal{Y}$ be the shared YAML parsing function provided by `amsha.utils.YamlUtils`:

$$
\mathcal{Y}: \texttt{FilePath} \to \texttt{Dict}[\texttt{str}, \texttt{Any}]
$$

The **system state** $\Sigma$ is fully determined by the YAML configuration space $\mathcal{C}$:

$$
\Sigma = \mathcal{Y}(c_{llm}) \times \mathcal{Y}(c_{crew}) \times \mathcal{Y}(c_{monitor}) \times \mathcal{Y}(c_{eval})
$$

Where:
- $c_{llm}$: `llm_config.yaml` — LLM provider selection and parameters
- $c_{crew}$: Agent/Task YAML files — Crew topology
- $c_{monitor}$: Analysis job YAML — Contribution analysis configuration
- $c_{eval}$: Evaluation job YAML — Scoring and grading configuration

**Determinism Property:**

$$
\forall c_1, c_2 \in \mathcal{C}: c_1 = c_2 \implies \Phi(c_1, I) = \Phi(c_2, I) \quad \text{(modulo LLM non-determinism)}
$$

**Zero-Code Reconfiguration:** Changing any element of $\mathcal{C}$ alters system behavior without modifying source code:

$$
\Delta(\Sigma) = \mathcal{Y}(\Delta c) \quad \text{(no recompilation required)}
$$

---

## 5. Dual-Backend Behavioral Equivalence

The system maintains behavioral equivalence across two implementations of the orchestration layer (File-backed and DB-backed), ensuring that mathematical outcomes are independent of the storage backend.

### Code Verification
- **DB orchestrator:** [db_crew_orchestrator.py:L22–L38](file:///e:/Python/Amsha/src/nikhil/amsha/crew_forge/orchestrator/db/db_crew_orchestrator.py#L22-L38)
- **File orchestrator:** [file_crew_orchestrator.py:L22–L38](file:///e:/Python/Amsha/src/nikhil/amsha/crew_forge/orchestrator/file/file_crew_orchestrator.py#L22-L38)
- **Shared builder:** [crew_builder_service.py](file:///e:/Python/Amsha/src/nikhil/amsha/crew_forge/service/crew_builder_service.py)

### Formalization

Let $\Phi_{DB}$ and $\Phi_{YAML}$ be the system functions for the DB-backed and File-backed pipelines respectively.

**Backend Equivalence Theorem:**

$$
\forall \mathcal{B}, I : \rho_{DB}(\mathcal{B}) \cong \rho_{YAML}(\mathcal{B}) \implies \Phi_{DB}(\mathcal{B}, I) \sim \Phi_{YAML}(\mathcal{B}, I)
$$

Where $\sim$ denotes behavioral equivalence (same LLM outputs, same monitoring metrics, same evaluation grades) and $\rho$ are the resolution functions defined in `crew_forge/mathematics.md §2`.

**Proof Sketch:**
1. Both orchestrators invoke identical `CrewPerformanceMonitor(model_name)` constructor
2. Both call `monitor.start_monitoring()` → `crew.kickoff(inputs)` → `monitor.stop_monitoring()` → `monitor.log_usage(result)` in the same sequence
3. The `CrewBuilderService.build()` receives identical `AgentRequest`/`TaskRequest` objects from either backend
4. Therefore, the constructed Crew is structurally identical, producing equivalent behavior

### Code Evidence

Both orchestrators share identical `run_crew()` method structure:

```python
# Identical in both db_crew_orchestrator.py and file_crew_orchestrator.py
self.last_monitor = CrewPerformanceMonitor(model_name=self.manager.model_name)
self.last_monitor.start_monitoring()
result = crew_to_run.kickoff(inputs=inputs)
self.last_monitor.stop_monitoring()
self.last_monitor.log_usage(result)
```

---

## 6. Monitoring Overhead Bound

The cross-module integration of `crew_monitor` into `crew_forge` adds measurable overhead. This section formalizes the overhead bound.

### Code Verification
- **Monitor lifecycle:** [db_crew_orchestrator.py:L22–L38](file:///e:/Python/Amsha/src/nikhil/amsha/crew_forge/orchestrator/db/db_crew_orchestrator.py#L22-L38)
- **Resource capture:** [crew_performance_monitor.py:L27–L60](file:///e:/Python/Amsha/src/nikhil/amsha/crew_monitor/service/crew_performance_monitor.py#L27-L60)

### Formalization

Let $T_{exec}$ be the raw crew execution time and $T_{total}$ be the total monitored time.

**Monitor Overhead** $\omega$:

$$
\omega = T_{total} - T_{exec} = T_{start\_monitor} + T_{stop\_monitor} + T_{log\_usage}
$$

Each monitoring operation involves:

$$
T_{start\_monitor} = T_{time.time()} + T_{psutil.cpu} + T_{psutil.mem} + \sum_{i=0}^{G-1} T_{nvml\_query}
$$

$$
T_{stop\_monitor} = T_{time.time()} + T_{psutil.cpu} + T_{psutil.mem} + \sum_{i=0}^{G-1} (T_{nvml\_mem} + T_{nvml\_util}) + T_{nvml\_shutdown}
$$

$$
T_{log\_usage} = O(1) \quad \text{(attribute access only)}
$$

**Overhead Bound:**

$$
\omega \leq 2 \times (T_{psutil} + G \times T_{nvml}) + T_{nvml\_init} + T_{nvml\_shutdown}
$$

Where typically: $T_{psutil} \approx 1\text{ms}$, $T_{nvml} \approx 0.5\text{ms}$, $G$ = number of GPUs.

For a typical single-GPU setup: $\omega \leq 5\text{ms}$, which is negligible relative to $T_{exec}$ (typically 10–300 seconds for LLM inference).

$$
\frac{\omega}{T_{exec}} \leq \frac{5\text{ms}}{10,000\text{ms}} = 0.05\%
$$

---

## 7. Circular Dependency Impact Analysis

The single architectural violation (`output_process` → `crew_forge` via `CrewParser` import) creates a mathematical dependency that can be formally analyzed.

### Code Verification
- **Violation:** [crew_validator.py:L7](file:///e:/Python/Amsha/src/nikhil/amsha/output_process/validation/crew_validator.py#L7)

### Formalization

The module dependency graph $G = (V, E)$ has a cycle:

$$
V = \{\texttt{crew\_forge}, \texttt{llm\_factory}, \texttt{crew\_monitor}, \texttt{output\_process}, \texttt{utils}\}
$$

$$
E = \{(CF \to LLM), (CF \to MON), (OUT \to CF), (CF \to U), (LLM \to U), (MON \to U), (OUT \to U)\}
$$

The **Strongly Connected Component** containing the cycle:

$$
SCC = \{CF, OUT\} \quad \text{(bidirectional dependency)}
$$

**Impact on Instability Metrics** (see also `dependencies.md §2`):

Without the violation: $I_{OUT} = \frac{0}{0 + 0}$ — undefined (isolated consumer).

With the violation: $I_{OUT} = \frac{1}{1 + 0} = 1.0$ — maximally unstable.

**Proposed Fix — Formal Model:**

Extract `CrewParser` to a shared module $\texttt{common}$, transforming the dependency:

$$
E' = (E \setminus \{(OUT \to CF)\}) \cup \{(OUT \to \texttt{common}), (CF \to \texttt{common})\}
$$

This eliminates the cycle: $SCC' = \emptyset$.

---

## 8. Global Complexity Summary

### End-to-End Pipeline Complexity

| Phase | Module(s) | Time Complexity | Space Complexity |
|:---|:---|:---|:---|
| LLM Provisioning | `llm_factory` | $O(1) + O(T_{LLM})$ | $O(|config|)$ |
| Crew Assembly | `crew_forge` | $O(|steps| \times T_{lookup})$ | $O(|A| + |T|)$ |
| Monitored Execution | `crew_forge` + `crew_monitor` | $O(T_{exec}) + O(G)$ | $O(|S|)$ |
| JSON Sanitization | `output_process` | $O(|C|)$ | $O(|C|)$ |
| Rubric Scoring | `output_process` | $O(|E| \times |R|)$ | $O(|E|)$ |
| Z-Score Grading | `output_process` | $O(n)$ | $O(n)$ |
| Pivot Consolidation | `output_process` | $O(|files| \times |evals|)$ | $O(|G| \times |E|)$ |

### Aggregate Algorithm Count

| Module | Local Algorithms | Cross-Module Algorithms | Total |
|:---|:---:|:---:|:---:|
| crew_forge | 8 | 3 (provisioning, monitoring, validation) | 11 |
| llm_factory | 6 | 1 (privacy guard composition) | 7 |
| crew_monitor | 7 | 1 (sandwich profiler integration) | 8 |
| output_process | 7 | 1 (parser reuse) | 8 |
| **System Total** | **28** | **6** | **34** |

---

## Cross-Module Algorithm Index

| # | Algorithm | Modules Involved | Source Files | Complexity |
|---|:---|:---|:---|:---|
| 1 | End-to-End Execution Pipeline | All 4 | `amsha_crew_db_application.py`, `db_crew_orchestrator.py` | $O(T_{LLM} + T_{exec})$ |
| 2 | Privacy-Guarded Execution | `llm_factory` + `crew_forge` | `llm_utils.py`, `llm_builder.py` | $O(|\texttt{Attr}(T)|)$ |
| 3 | Cross-Module Data Flow | `crew_forge` ↔ all | `amsha_crew_db_application.py` | $O(1)$ per boundary |
| 4 | Configuration Universality | All 4 + `utils` | All config loaders | $O(|config|)$ |
| 5 | Dual-Backend Equivalence | `crew_forge` (dual) | Both orchestrators | $O(|A| + |T|)$ |
| 6 | Monitoring Overhead | `crew_forge` + `crew_monitor` | `db_crew_orchestrator.py`, `crew_performance_monitor.py` | $O(G)$ |
