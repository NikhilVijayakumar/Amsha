# Example: Research Paper Tables for Amsha Project

Collection of real-world table examples for academic publication.

---

## Table 1: Module Metrics Summary

| S.No | Module | LOC | Files | Complexity Score | Test Coverage (%) | Grade | Priority |
|:----:|:-------|----:|------:|:----------------:|------------------:|:-----:|:--------:|
| 1 | crew_forge | 450 | 6 | 12.3 (Medium) | 95 | A | Critical |
| 2 | output_process | 320 | 4 | 15.7 (High) | 92 | A | Critical |
| 3 | crew_monitor | 280 | 5 | 8.4 (Low) | 88 | B | High |
| 4 | crew_gen | 210 | 4 | 10.1 (Medium) | 85 | B | High |
| 5 | llm_factory | 150 | 3 | 6.2 (Low) | 90 | A | Medium |
| 6 | utils | 95 | 2 | 4.5 (Low) | 78 | C | Low |
| | **Total** | **1,505** | **24** | **9.5 (Low)** † | **88.0** | **B+** | - |

**Table 3.1:** Code complexity and quality metrics for each module. LOC = Lines of Code (excluding comments and tests). Complexity score based on cyclomatic complexity (radon). Coverage measured via pytest-cov. † Weighted average by LOC.

**Source:** Static analysis on commit `abc123`, 2026-02-10

---

## Table 2: Performance Benchmarks

| Operation | Execution Time (ms) | Memory Usage (MB) | CPU Load (%) | Disk I/O (KB) |
|:----------|--------------------:|------------------:|-------------:|--------------:|
| Crew Creation | 12.3 ± 1.2 | 4.2 ± 0.3 | 15 | 0.5 |
| Agent Initialization | 45.2 ± 5.6 | 12.1 ± 1.8 | 20 | 2.3 |
| Task Execution (avg) | 234.7 ± 45.3 | 156.3 ± 22.1 | 75 | 45.2 |
| Result Evaluation | 8.1 ± 0.9 | 2.7 ± 0.4 | 10 | 0.1 |
| Repository Save | 15.4 ± 2.1 | 3.5 ± 0.6 | 8 | 125.7 |
| **Total Pipeline** | **315.7 ± 48.2** | **178.8 ± 23.7** | **~60** † | **173.8** |

**Table 5.1:** Performance benchmarks measured on test dataset (N=100 runs). Values shown as mean ± standard deviation. Test environment: AMD Ryzen 7 5800H, 16GB DDR4, Ubuntu 22.04, Python 3.11.5. † Average CPU load across operations.

**Source:** `crew_monitor` performance logs, `tests/performance/benchmark_results.json`

---

## Table 3: Feature Comparison with Related Systems

| Feature | Amsha | LangChain | Semantic Kernel | AutoGPT | CrewAI |
|:--------|:-----:|:---------:|:---------------:|:-------:|:------:|
| Repository Pattern | ✅ | ❌ | ❌ | ❌ | ❌ |
| Clean Architecture | ✅ | ❌ | ⚠️ Partial | ❌ | ❌ |
| Protocol-based DI | ✅ | ❌ | ❌ | ❌ | ❌ |
| Pydantic Validation | ✅ | ✅ | ❌ | ⚠️ Partial | ✅ |
| Performance Monitoring | ✅ | ⚠️ Basic | ❌ | ❌ | ⚠️ Basic |
| Immutable Models | ✅ | ❌ | ❌ | ❌ | ❌ |
| MongoDB Support | ✅ | ✅ | ✅ | ❌ | ❌ |
| Test Coverage >80% | ✅ | ⚠️ Partial | ⚠️ Partial | ❌ | ⚠️ Partial |
| **Feature Score** | **8/8** | **2.5/8** | **1.5/8** | **0.5/8** | **2.5/8** |

**Table 2.1:** Feature comparison between Amsha and related agent orchestration frameworks. ✅ = Full support, ⚠️ = Partial support, ❌ = Not supported. Analysis based on official documentation and source code review as of February 2026.

---

## Table 4: Experimental Results - Baseline Comparison

| Method | Avg Score (%) | Std Dev | Min | Max | Processing Time (ms) | Grade Distribution |
|:-------|-------------:|--------:|----:|----:|---------------------:|:-------------------|
| Simple Mean | 72.3 | 8.2 | 52 | 95 | 5.2 ± 0.4 | D:15%, C:25%, B:35%, A:25% |
| Median-Based | 75.8 | 7.1 | 58 | 96 | 4.8 ± 0.3 | D:12%, C:20%, B:38%, A:30% |
| Standard Curve | 78.4 | 6.5 | 60 | 98 | 9.1 ± 1.2 | D:8%, C:18%, B:40%, A:34% |
| **Ours (Weighted)** | **82.6** | **5.9** | **65** | **99** | **8.3 ± 0.9** | **D:5%, C:12%, B:38%, A:45%** |

**Table 6.1:** Comparison of grading methods on benchmark dataset (N=500 students, 10 assignments). Values are mean across all students. Bold indicates best performance. Our weighted method achieves significantly higher average scores (p < 0.001, paired t-test vs. all baselines) while maintaining fairness (lowest std dev among top methods).

**Source:** Synthetic student data generated via `tests/fixtures/student_generator.py`

---

## Table 5: Ablation Study

| Configuration | Accuracy (%) | Precision (%) | Recall (%) | F1 Score | Δ Accuracy |
|:--------------|-------------:|--------------:|-----------:|---------:|:-----------|
| Full Model (All Weights) | 82.6 | 81.3 | 80.9 | 0.811 | - |
| - Without Stage 1 Weight | 78.3 | 76.8 | 77.1 | 0.770 | -4.3 ⬇️ |
| - Without Stage 2 Weight | 80.1 | 79.2 | 78.8 | 0.790 | -2.5 ⬇️ |
| - Without Stage 3 Weight | 81.2 | 80.5 | 79.7 | 0.801 | -1.4 ⬇️ |
| - Without Normalization | 75.8 | 74.2 | 73.9 | 0.740 | -6.8 ⬇️ |
| All Weights Equal (1.0) | 76.5 | 75.1 | 74.8 | 0.750 | -6.1 ⬇️ |

**Table 6.2:** Ablation study showing contribution of each component to final performance. Δ Accuracy = change from full model. Results show that normalization has the largest impact (-6.8%), followed by Stage 1 weighting (-4.3%). All degradations are statistically significant (p < 0.01, paired t-test).

---

## Table 6: Hyperparameter Configuration

| Parameter | Value | Range Tested | Search Method | Justification |
|:----------|:------|:-------------|:--------------|:--------------|
| `stage_1_weight` | 0.30 | [0.1, 0.5] | Grid Search | Best validation accuracy |
| `stage_2_weight` | 0.50 | [0.3, 0.7] | Grid Search | Emphasizes core evaluation |
| `stage_3_weight` | 0.20 | [0.1, 0.4] | Grid Search | Fine-tuning contribution |
| `normalization_method` | "min-max" | {z-score, min-max, robust} | Manual | Handles outliers well |
| `score_threshold` | 0.75 | [0.5, 0.9] | Binary Search | Optimal precision-recall |
| `batch_size` | 32 | {16, 32, 64, 128} | Manual | Memory-performance tradeoff |

**Table 4.1:** Hyperparameter values used in experiments. All continuous parameters tuned via grid search (step=0.1) on validation set. Final configuration achieves 82.6% accuracy on held-out test set.

---

## Table 7: Dataset Statistics

| Split | Samples | Features | Avg Score | Std Dev | Class Balance |
|:------|--------:|---------:|----------:|--------:|:--------------|
| Training | 8,000 | 10 | 76.8 | 12.3 | 1:1.1:1.2:0.9 |
| Validation | 1,000 | 10 | 77.2 | 11.9 | 1:1.0:1.1:1.0 |
| Test | 1,000 | 10 | 76.5 | 12.5 | 1:1.2:1.0:0.9 |
| **Total** | **10,000** | **10** | **76.8** | **12.3** | **1:1.1:1.1:0.9** |

**Table 5.1:** Dataset statistics for grading experiments. Features = number of assignment scores per student. Class balance = D:C:B:A ratio. Data split with random seed 42 for reproducibility.

---

## Table 8: Error Analysis

| Error Type | Count | Percentage | Severity | Example | Mitigation |
|:-----------|------:|-----------:|:---------|:--------|:-----------|
| Timeout (>30s) | 23 | 46% | High | LLM response delay | Retry with backoff |
| Invalid JSON | 15 | 30% | Medium | Malformed LLM output | Pydantic validation |
| Rate Limit | 8 | 16% | Low | API quota exceeded | Exponential backoff |
| Network Error | 4 | 8% | High | Connection refused | Circuit breaker |
| **Total Errors** | **50** | **100%** | - | - | - |

**Table 7.1:** Error distribution across 500 test runs (10% failure rate). Most common errors are timeouts (46%) and JSON parsing failures (30%). High-severity errors trigger automatic retry with exponential backoff.

**Source:** Error logs from `crew_monitor`, `logs/execution_errors.json`

---

## Table 9: Code Distribution

| Module | LOC | Percentage | Type |
|:-------|----:|-----------:|:-----|
| crew_forge | 450 | 29.9% | Core Repository |
| output_process | 320 | 21.3% | Evaluation Logic |
| crew_monitor | 280 | 18.6% | Performance Tracking |
| crew_gen | 210 | 14.0% | Generation |
| llm_factory | 150 | 10.0% | Provider Abstraction |
| utils | 95 | 6.3% | Utilities |
| **Total** | **1,505** | **100%** | - |

**Table 3.2:** Source code distribution across modules (excluding tests and comments). Core repository (crew_forge) and evaluation logic (output_process) comprise 51.2% of the codebase, reflecting system's focus on clean architecture and sophisticated grading.

---

## Table 10: Time Complexity Analysis

| Operation | Best Case | Average Case | Worst Case | Space | Notes |
|:----------|:---------:|:------------:|:----------:|:-----:|:------|
| Create Crew | Ω(n) | Θ(n) | O(n) | O(n) | n = agents |
| Execute Task | Ω(m) | Θ(m·k) | O(m·k²) | O(m) | m = tasks, k = iterations |
| Evaluate | Ω(n) | Θ(n·log n) | O(n²) | O(1) | Sorting needed |
| Save DB | Ω(1) | Θ(1) | O(n) | O(n) | MongoDB insert |

**Table 4.2:** Computational complexity of key operations. Best/average/worst case time complexities and space complexity shown. Worst case for evaluation occurs with highly imbalanced data requiring multiple comparison passes.

---

## Formatting Consistency Check

✅ **This example demonstrates:**
- Serial numbers (S.No) for readability
- Right-aligned numbers
- Left-aligned text
- Center-aligned symbols
- Bold totals/aggregates
- Error bars (±) for measurements
- Units in headers
- Descriptive captions
- Source citations
- Symbols for quick scanning (✅❌⚠️⬇️⬆️)
- Consistent decimal places (1-2)
- Table numbering (Section.Number)
- Abbreviation definitions
