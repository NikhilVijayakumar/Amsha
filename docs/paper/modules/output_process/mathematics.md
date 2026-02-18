# Output Process: Mathematical Foundations

## 1. Relative Grading Algorithm

The `EvaluationAggregationTool` implements a statistical grading system based on the Normal Distribution (Gaussian Bell Curve) of the population scores. This ensures that grades are assigned relative to peer performance rather than absolute thresholds.

### Code Verification
- **Source:** `src/nikhil/amsha/output_process/evaluation/evaluation_aggregate_tool.py`
- **Lines:** 89-111 (`_apply_relative_grading`)

### Formalization

Let $S = \{s_1, s_2, \dots, s_n\}$ be the set of final score percentages for $n$ evaluations.

First, calculate the population parameters:
$$
\mu = \frac{1}{n} \sum_{i=1}^n s_i \quad (\text{Mean})
$$

$$
\sigma = \sqrt{\frac{1}{n} \sum_{i=1}^n (s_i - \mu)^2} \quad (\text{Standard Deviation})
$$

The Grade $G(s_i)$ for a score $s_i$ is determined by its Z-score interval:

$$
G(s_i) = \begin{cases}
A & \text{if } s_i > \mu + \sigma \\
B & \text{if } \mu < s_i \le \mu + \sigma \\
C & \text{if } \mu - \sigma < s_i \le \mu \\
D & \text{if } s_i \le \mu - \sigma
\end{cases}
$$

The Final Score $F(s_i)$ incorporates the grade point weight $W(G(s_i))$:

$$
F(s_i) = s_i \times W(G(s_i))
$$

### Complexity
- **Time:** $O(n)$ - Linear pass to calculate mean/std, linear pass to assign grades.
- **Space:** $O(n)$ - Storing the dataframe.

---

## 2. Configuration Validation Logic

The `CrewConfigValidator` applies a boolean verification logic over the hierarchical structure of Agents and Tasks within the file system.

### Code Verification
- **Source:** `src/nikhil/amsha/output_process/validation/crew_validator.py`
- **Lines:** 105-130 (`_generate_summary`)

### Formalization

Let $U$ be the set of Use Cases. For each use case $u \in U$, let $A_u$ be the set of Agent files and $T_u$ be the set of Task files.

The validation function $V(f)$ for a file $f$ returns true if the parser succeeds, false otherwise.

The global validity $V_{global}$ is defined as:

$$
V_{global} = \left( \bigwedge_{u \in U} \bigwedge_{f \in A_u} V(f) \right) \land \left( \bigwedge_{u \in U} \bigwedge_{f \in T_u} V(f) \right)
$$

### Metric Formalization
- **Total Files:** $N_{total} = \sum_{u \in U} (|A_u| + |T_u|)$
- **Valid Files:** $N_{valid} = \sum_{f} [V(f) = \text{True}]$
- **Invalid Files:** $N_{invalid} = N_{total} - N_{valid}$

### Complexity
- **Time:** $O(N \cdot P)$ where $N$ is total files and $P$ is parsing cost.
- **Space:** $O(N)$ for the report structure.
