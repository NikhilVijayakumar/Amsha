# Output Process: Mathematical Foundations

This document formalizes the algorithms within the `output_process` module, covering rubric-weighted scoring, Z-score relative grading, LLM output sanitization, configuration validation, directory set-difference comparison, and multi-model pivot consolidation.

---

## 1. Rubric-Weighted Evaluation Scoring

The `EvaluationProcessingTool` implements a weighted scoring algorithm that maps raw LLM evaluation scores to a normalized percentage using a configurable rubric.

### Code Verification
- **Source:** [evaluation_processing_tool.py](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/output_process/evaluation/evaluation_processing_tool.py)
- **Lines:** L32–L79 (`_calculate_evaluation_score`)

### Formalization

Let $\mathcal{M} = \{m_1, m_2, \dots, m_K\}$ be the set of evaluation metrics defined in the rubric. Each metric $m_k$ has:
- $w_k$ = weight
- $[l_k, h_k]$ = scoring range
- $r_k$ = raw score from the LLM judge

The **Weighted Score** for metric $m_k$:

$$
S_w(m_k) = r_k \times w_k
$$

The **Maximum Possible Score**:

$$
S_{max} = \sum_{k=1}^{K} h_k \times w_k
$$

The **Final Percentage**:

$$
F\% = \frac{\sum_{k=1}^{K} S_w(m_k)}{S_{max}} \times 100 \quad \text{(guarded: } S_{max} > 0\text{)}
$$

### Tier Classification

The final percentage is mapped to a descriptive tier:

$$
\texttt{Tier}(F\%) = \begin{cases}
\texttt{Excellent} & \text{if } 91.0 \leq F\% \leq 100.0 \\
\texttt{Strong} & \text{if } 75.0 \leq F\% < 91.0 \\
\texttt{Moderate} & \text{if } 65.0 \leq F\% < 75.0 \\
\texttt{Weak} & \text{if } 0.0 \leq F\% < 65.0
\end{cases}
$$

### Variable Mapping

| LaTeX Symbol | Code Variable | File | Line |
| :--- | :--- | :--- | :--- |
| $w_k$ | `weight` | `evaluation_processing_tool.py` | L52 |
| $r_k$ | `raw_score` | `evaluation_processing_tool.py` | L50 |
| $S_w$ | `item['weightedScore']` | `evaluation_processing_tool.py` | L53 |
| $S_{max}$ | `max_possible_score` | `evaluation_processing_tool.py` | L43 |
| $F\%$ | `final_percentage` | `evaluation_processing_tool.py` | L60 |

### Complexity
- **Time:** $O(K)$ per evaluation — Linear in number of rubric metrics.
- **Space:** $O(K)$ for updated evaluation list.

---

## 2. Z-Score Relative Grading (Gaussian Normalization)

The `EvaluationAggregationTool` applies **psychometric-inspired** relative grading where grades are assigned based on each score's position relative to the population mean using standard deviations.

### Code Verification
- **Source:** [evaluation_aggregate_tool.py](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/output_process/evaluation/evaluation_aggregate_tool.py)
- **Lines:** L89–L111 (`_apply_relative_grading`)

### Formalization

Let $S = \{s_1, s_2, \dots, s_n\}$ be the set of `finalScorePercentage` values.

**Population Parameters:**

$$
\mu = \frac{1}{n} \sum_{i=1}^{n} s_i \qquad \sigma = \sqrt{\frac{1}{n} \sum_{i=1}^{n} (s_i - \mu)^2}
$$

**Grade Assignment** based on Z-score intervals:

$$
G(s_i) = \begin{cases}
A & \text{if } s_i > \mu + \sigma \\
B & \text{if } \mu < s_i \leq \mu + \sigma \\
C & \text{if } \mu - \sigma < s_i \leq \mu \\
D & \text{if } s_i \leq \mu - \sigma
\end{cases}
$$

**Grade Point Mapping** $W: \{A, B, C, D\} \to \mathbb{R}$ (configurable via `grading_scale`):

$$
W = \{A \mapsto 4.0,\; B \mapsto 3.0,\; C \mapsto 2.0,\; D \mapsto 1.0\}
$$

**Final Score** incorporating grade weight:

$$
F(s_i) = W(G(s_i)) \times s_i
$$

**CGPA** (Cumulative Grade Point Average):

$$
\texttt{CGPA} = \frac{1}{n} \sum_{i=1}^{n} W(G(s_i))
$$

### Properties
- **Population-Relative:** Grades depend on peer performance, not absolute thresholds.
- **Robust to Grader Bias:** If a strict judge gives low scores to all, relative ordering is preserved.
- **Normal Distribution Assumption:** Works best when $n \geq 10$ and scores approximately follow $\mathcal{N}(\mu, \sigma^2)$.

### Complexity
- **Time:** $O(n)$ — Two linear passes (compute $\mu/\sigma$, assign grades).
- **Space:** $O(n)$ for DataFrame storage.

---

## 3. Multi-Pass LLM Output Sanitization

The `JsonCleanerUtils` implements a **3-stage cascading parser** for extracting valid JSON from raw LLM text output, handling markdown fences, concatenated objects, and quote errors.

### Code Verification
- **Source:** [json_cleaner_utils.py](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/output_process/optimization/json_cleaner_utils.py)
- **Lines:** L73–L119 (`_clean_and_parse_string`)

### Formalization

Let $C$ be the raw LLM output string. The sanitization pipeline applies cascading transformations:

**Stage 1 — Fence Extraction:**

$$
C_1 = \begin{cases}
\texttt{split}(C, \texttt{```json})[1] & \text{if } \texttt{```json} \in C \\
\texttt{split}(C, \texttt{```})[1] & \text{if } \texttt{```} \in C \\
C & \text{otherwise}
\end{cases}
$$

Then strip residual fences: $C_1' = \texttt{re.sub}(\texttt{```}, \texttt{""}, C_1)$

**Stage 2 — Direct Parse Attempt:**

$$
\texttt{Parse}_1(C_1') = \begin{cases}
\texttt{json.loads}(C_1') & \text{if valid JSON} \\
\bot & \text{otherwise (proceed to Stage 3)}
\end{cases}
$$

**Stage 3 — Concatenated Object Extraction:**

$$
\texttt{Parse}_2(C_1') = \texttt{findall}(\texttt{r"\{.*?\}"}, C_1') \xrightarrow{\text{parse each}} \begin{cases}
J_0 & \text{if } |matches| = 1 \\
[J_0, J_1, \dots] & \text{if } |matches| > 1
\end{cases}
$$

**Stage 4 — Quote Repair:**

$$
\texttt{Parse}_3(C_1') = \texttt{json.loads}(\texttt{re.sub}(\texttt{r'"\\s*[\'"]'}, \texttt{'"'}, C_1'))
$$

The full pipeline is a short-circuit cascade:

$$
\texttt{Clean}(C) = \texttt{Parse}_1(C_1') \lor \texttt{Parse}_2(C_1') \lor \texttt{Parse}_3(C_1') \lor \bot
$$

### Complexity
- **Time:** $O(|C|)$ per stage — Each regex pass is linear.
- **Space:** $O(|C|)$ for intermediate strings.

---

## 4. Output Path Derivation with Uniqueness Guarantee

The `JsonCleanerUtils` derives output paths with automatic deduplication.

### Code Verification
- **Source:** [json_cleaner_utils.py](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/output_process/optimization/json_cleaner_utils.py)
- **Lines:** L30–L67 (`_derive_output_path`, `_get_unique_filepath`)

### Formalization

**Path Derivation:** $\texttt{derive}: Path \to Path$

$$
\texttt{derive}(p) = \texttt{filter}(\texttt{replace}(p, \texttt{"intermediate"} \to \texttt{"final"}),\; \neg\texttt{match}(\texttt{r"output\_\\d+"}))
$$

**Uniqueness:** $\texttt{unique}: Path \to Path$

$$
\texttt{unique}(p) = \begin{cases}
p & \text{if } \neg\exists\, p \\
p_k & \text{where } p_k = \texttt{stem}(p) + \texttt{"\_"} + k + \texttt{ext}(p),\; k = \min\{i \geq 1 : \neg\exists\, p_i\}
\end{cases}
$$

### Complexity
- **Time:** $O(k)$ where $k$ = number of existing duplicates (typically $k < 10$).

---

## 5. Configuration Validation (Boolean Algebra)

The `CrewConfigValidator` applies boolean verification over YAML agent/task configurations.

### Code Verification
- **Source:** [crew_validator.py](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/output_process/validation/crew_validator.py)
- **Lines:** L64–L103 (`_collect_files_to_validate`, `_process_and_validate_files`), L105–L130 (`_generate_summary`)

### Formalization

Let $U$ be the set of use cases. For $u \in U$, $A_u$ = agent files, $T_u$ = task files.

The validation predicate $V(f)$:

$$
V(f) = \begin{cases}
\texttt{True} & \text{if } \texttt{CrewParser.parse}(f) \text{ succeeds} \\
\texttt{False} & \text{if exception raised}
\end{cases}
$$

**Global Validity:**

$$
V_{global} = \underbrace{\left( \bigwedge_{u \in U} \bigwedge_{f \in A_u} V(f) \right)}_{\texttt{all\_agents\_valid}} \land \underbrace{\left( \bigwedge_{u \in U} \bigwedge_{f \in T_u} V(f) \right)}_{\texttt{all\_tasks\_valid}}
$$

**Summary Metrics:**

$$
N_{total} = \sum_{u \in U} (|A_u| + |T_u|) \qquad N_{valid} = \sum_f \mathbb{1}[V(f)] \qquad N_{invalid} = N_{total} - N_{valid}
$$

### Complexity
- **Time:** $O(N \times P)$ where $N$ = files, $P$ = parsing cost per file.
- **Space:** $O(N)$ for the report structure.

---

## 6. Directory Set-Difference Comparison

The `JSONOutputManager` identifies files present in an intermediate directory but not in a final directory — a set-difference operation.

### Code Verification
- **Source:** [json_output_validator.py](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/output_process/validation/json_output_validator.py)
- **Lines:** L32–L36 (`_find_unique_files`), L52–L72 (`run_comparison`)

### Formalization

Let $I$ = set of JSON filenames in intermediate directory, $F$ = set in final directory.

$$
\texttt{Unique} = I \setminus F = \{ f \in I \mid f.\texttt{name} \notin \{g.\texttt{name} \mid g \in F\} \}
$$

This identifies **unprocessed files** that failed the cleaning pipeline.

### Complexity
- **Time:** $O(|I| + |F|)$ — Set construction + lookup.
- **Space:** $O(|F|)$ for the comparison name set.

---

## 7. Multi-Model Pivot Consolidation

The `EvaluationReportTool` combines evaluations from multiple evaluator models (Gemini, GPT, Llama, Qwen) into a cross-model comparison matrix using pivot-table transformation.

### Code Verification
- **Source:** [evaluation_report_tool.py](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/output_process/evaluation/evaluation_report_tool.py)
- **Lines:** L115–L167 (pivot + grading)

### Formalization

**Step 1 — Model Name Extraction** via regex:

$$
\texttt{gen\_model}(filename) = \texttt{regex}(filename, \texttt{r"[^\_]+\_(.+)\\.json\$"})
$$

$$
\texttt{eval\_model}(filename) = \texttt{replace}(basename, \texttt{"aggregated\_results\_"} \to \texttt{""})
$$

**Step 2 — Pivot Transformation:**

$$
\texttt{Pivot}: (\texttt{gen\_model}, \texttt{plotTitle}) \times \texttt{eval\_model} \to \texttt{finalScore}
$$

**Step 3 — Cross-Model Total:**

$$
\texttt{totalFinalScore}(g) = \sum_{e \in \texttt{eval\_models}} \texttt{Pivot}[g, e]
$$

**Step 4 — Re-apply Relative Grading** on `totalFinalScore` (see §2).

### Complexity
- **Time:** $O(|files| \times |evals|)$ for loading + $O(|rows| \times |cols|)$ for pivot.
- **Space:** $O(|gen\_models| \times |eval\_models|)$ for pivot table.

---

## Algorithm Index

| # | Algorithm | Source File | Lines | Complexity |
|---|-----------|------------|-------|------------|
| 1 | Rubric-Weighted Scoring | `evaluation_processing_tool.py` | L32–L79 | $O(K)$ |
| 2 | Z-Score Relative Grading | `evaluation_aggregate_tool.py` | L89–L111 | $O(n)$ |
| 3 | Multi-Pass JSON Sanitization | `json_cleaner_utils.py` | L73–L119 | $O(|C|)$ |
| 4 | Output Path Uniqueness | `json_cleaner_utils.py` | L30–L67 | $O(k)$ |
| 5 | Configuration Validation | `crew_validator.py` | L64–L130 | $O(N \times P)$ |
| 6 | Directory Set-Difference | `json_output_validator.py` | L32–L72 | $O(|I| + |F|)$ |
| 7 | Multi-Model Pivot Consolidation | `evaluation_report_tool.py` | L115–L167 | $O(|files| \times |evals|)$ |
