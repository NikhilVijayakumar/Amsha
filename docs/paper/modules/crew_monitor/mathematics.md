# Crew Monitor: Mathematical Foundations

## 1. Resource Usage Delta Calculation

The `CrewPerformanceMonitor` captures the computational cost of an agent execution window by measuring the state change of system resources between two temporal checkpoints, $t_{start}$ and $t_{end}$.

### Code Verification
- **Source:** `src/nikhil/amsha/crew_monitor/service/crew_performance_monitor.py`
- **Lines:** 89-102 (General metrics), 112-120 (GPU metrics)

### Formalization

Let $S(t)$ be the system state vector at time $t$:

$$
S(t) = \langle Mem(t), CPU(t), GPU_{mem}(t) \rangle
$$

The resource consumption $\Delta R$ for an execution interval $[t_{start}, t_{end}]$ is defined as:

$$
\Delta_{mem} = Mem(t_{end}) - Mem(t_{start})
$$

$$
\Delta_{time} = t_{end} - t_{start}
$$

The CPU usage is captured as instantaneous snapshots, while token usage is an aggregation sum:

$$
Tokens_{total} = \sum_{req \in Requests} (T_{prompt} + T_{completion})
$$

### Complexity
- **Time:** $O(1)$ - Constant time system calls (psutil/nvml).
- **Space:** $O(G)$ where $G$ is the number of GPUs tracking state.

---

## 2. Feature Contribution Consensus

The `ContributionAnalyzer` algorithm quantifies the consensus level or "contribution weight" of a specific feature across a population of Large Language Models (LLMs). This metric helps identify high-confidence features in multi-agent outputs.

### Code Verification
- **Source:** `src/nikhil/amsha/crew_monitor/service/contribution_analyzer.py`
- **Lines:** 66-79 (`_calculate_feature_contribution`)

### Formalization

Let $\mathcal{L}$ be the set of all participating LLMs, such that $|\mathcal{L}| = N_{total}$.
Let $F$ be a specific feature extracted from the aggregated output.
Let $C_f \subseteq \mathcal{L}$ be the subset of LLMs that contributed to or validated feature $F$.

The **Contribution Percentage** $P(F)$ is calculated as:

$$
P(F) = \left( \frac{|C_f|}{N_{total}} \right) \times 100
$$

Where:
- $|C_f|$ is the cardinality of the contributing actors set (`feature.contributingFeatures`).
- $N_{total}$ is the total number of LLMs (`job_config.total_llms`).

### Metric Interpretation
- $P(F) = 1N_{total}0\%$ implies unanimous consensus.
- $P(F) < 50\%$ implies a minority or outlier feature.

### Complexity
- **Time:** $O(M \cdot K)$ where $M$ is the number of features and $K$ is the average number of contributors per feature.
- **Space:** $O(1)$ (in-place modification of dictionary).
