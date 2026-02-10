# Markdown Table Best Practices for Research Papers

Comprehensive guide for creating high-quality tables in academic publications.

---

## Table Types for Research Papers

### 1. Performance Metrics Table

**Use For:** Benchmark results, timing data, resource usage

```markdown
| Operation | Time (ms) | Memory (MB) | CPU (%) | Accuracy (%) |
|:----------|----------:|------------:|--------:|-------------:|
| Crew Creation | 12.3 ± 1.2 | 4.2 | 15 | N/A |
| Task Execution | 234.7 ± 45.3 | 156.3 | 75 | 98.5 |
| Result Evaluation | 8.1 ± 0.9 | 2.7 | 10 | 99.1 |
| Repository Save | 15.4 ± 2.1 | 3.5 | 8 | N/A |

**Table X.Y:** Performance benchmarks measured on test dataset (N=100 runs). Values shown as mean ± standard deviation. Test environment: AMD Ryzen 7, 16GB RAM, Ubuntu 22.04.
```

**Best Practices:**
- Include error bars (±) or confidence intervals
- Right-align numerical columns (`:---:|` or `---:`)
- Left-align text columns (`:---`)
- Always include units in headers
- Add sample size (N=...) in caption
- Specify test environment in caption

---

### 2. Module/Component Comparison Table

**Use For:** Comparing features, metrics across modules

```markdown
| Module | LOC | Files | Complexity | Coverage (%) | Grade | Priority |
|:-------|----:|------:|:-----------|-------------:|:-----:|:--------:|
| crew_forge | 450 | 6 | Medium | 95 | A | Critical |
| output_process | 320 | 4 | High | 92 | A | Critical |
| crew_monitor | 280 | 5 | Low | 88 | B | High |
| llm_factory | 150 | 3 | Low | 90 | A | Medium |
| crew_gen | 210 | 4 | Medium | 85 | B | High |
| utils | 95 | 2 | Low | 78 | C | Low |
| **Total** | **1,505** | **24** | - | **88.0** | **B+** | - |

**Table X.Y:** Code metrics for each module. LOC = Lines of Code (excluding comments/tests). Complexity based on cyclomatic complexity. Coverage from pytest-cov.
```

**Best Practices:**
- Add totals/averages row (bold with `**...**`)
- Use center alignment for categorical data (`:---:`)
- Include S.No column for readability if >5 rows
- Define abbreviations in caption (LOC, SLOC, etc.)

---

### 3. Comparison with Baselines/Related Work

**Use For:** Comparing your approach with existing methods

```markdown
| Feature | Amsha | LangChain | Semantic Kernel | AutoGPT |
|:--------|:-----:|:---------:|:---------------:|:-------:|
| Repository Pattern | ✅ | ❌ | ❌ | ❌ |
| Clean Architecture | ✅ | ❌ | ⚠️ Partial | ❌ |
| Protocol-based DI | ✅ | ❌ | ❌ | ❌ |
| Performance Monitoring | ✅ | ⚠️ Basic | ❌ | ❌ |
| Pydantic Validation | ✅ | ✅ | ❌ | ⚠️ Partial |
| Modular Design | ✅ | ✅ | ✅ | ❌ |
| **Total Features** | **6/6** | **2/6** | **1/6** | **0/6** |

**Table X.Y:** Feature comparison between Amsha and related agent orchestration frameworks. ✅ = Full support, ⚠️ = Partial support, ❌ = Not supported.
```

**Best Practices:**
- Use symbols (✅❌⚠️) for quick visual comparison
- Center-align comparison columns
- Bold your system's column for emphasis
- Add totals row for quantitative comparison
- Define symbols in caption

---

### 4. Experimental Results Table

**Use For:** ML/algorithm results, accuracy metrics, statistical tests

```markdown
| Method | Accuracy (%) | Precision (%) | Recall (%) | F1-Score | Time (s) |
|:-------|-------------:|--------------:|-----------:|---------:|---------:|
| Baseline (Mean) | 72.3 ± 2.1 | 68.5 ± 3.2 | 71.2 ± 2.8 | 0.698 | 0.12 |
| Baseline (Median) | 75.8 ± 1.9 | 74.1 ± 2.5 | 73.6 ± 2.2 | 0.738 | 0.09 |
| Standard Curve | 78.4 ± 2.3 | 76.8 ± 3.1 | 77.2 ± 2.6 | 0.770 | 0.15 |
| **Ours (Weighted)** | **82.6 ± 1.7** | **81.3 ± 2.2** | **80.9 ± 2.0** | **0.811** | **0.14** |

**Table X.Y:** Experimental results on test dataset (N=500). Values are mean ± std over 10 runs. Bold indicates best performance. All improvements over best baseline are statistically significant (p < 0.05, paired t-test).
```

**Best Practices:**
- Bold the best values in each column
- Include statistical significance testing in caption
- Report mean ± std or confidence intervals
- Specify number of runs/samples
- Right-align all numerical values

---

### 5. Ablation Study Table

**Use For:** Showing impact of removing components

```markdown
| Configuration | Accuracy (%) | Δ from Full |
|:--------------|-------------:|:------------|
| Full Model | 82.6 | - |
| - Without Weight 1 | 78.3 | -4.3 ⬇️ |
| - Without Weight 2 | 80.1 | -2.5 ⬇️ |
| - Without Weight 3 | 81.2 | -1.4 ⬇️ |
| - Without Normalization | 75.8 | -6.8 ⬇️ |
| All Weights Equal | 76.5 | -6.1 ⬇️ |

**Table X.Y:** Ablation study showing contribution of each component. Δ = change from full model. All degradations are significant (p < 0.01).
```

**Best Practices:**
- Show full model first
- Use minus sign (-) for component removal
- Include delta (Δ) column with directional arrows
- Highlight most important components

---

### 6. Hyperparameter Table

**Use For:** Documenting configuration values

```markdown
| Parameter | Value | Range Tested | Justification |
|:----------|:------|:-------------|:--------------|
| Learning Rate | 0.001 | [0.0001, 0.01] | Best validation loss |
| Batch Size | 32 | [16, 64, 128] | Memory-performance tradeoff |
| Weight Decay | 0.0001 | [0, 0.001] | Prevents overfitting |
| Dropout | 0.3 | [0, 0.5] | Optimal regularization |
| Hidden Dim | 256 | [128, 512] | Best accuracy |

**Table X.Y:** Hyperparameter values used in experiments. Range tested shows explored values via grid search. Final values chosen based on validation set performance.
```

**Best Practices:**
- Document all tunable parameters
- Show explored ranges
- Justify final choices
- Essential for reproducibility

---

### 7. Dataset Statistics Table

**Use For:** Describing experimental data

```markdown
| Split | Samples | Features | Classes | Imbalance Ratio |
|:------|--------:|---------:|--------:|:---------------:|
| Train | 8,000 | 256 | 10 | 1:1.2 |
| Validation | 1,000 | 256 | 10 | 1:1.3 |
| Test | 1,000 | 256 | 10 | 1:1.1 |
| **Total** | **10,000** | **256** | **10** | **1:1.2** |

**Table X.Y:** Dataset statistics. Imbalance ratio = minority:majority class ratio. Random seed: 42 for reproducibility.
```

---

### 8. Time Complexity Table

**Use For:** Algorithm complexity analysis

```markdown
| Operation | Time Complexity | Space Complexity | Notes |
|:----------|:---------------:|:----------------:|:------|
| Create Crew | O(n) | O(n) | n = number of agents |
| Execute Task | O(m × k) | O(m) | m = tasks, k = avg iterations |
| Evaluate Results | O(n) | O(1) | Linear scan |
| Save Repository | O(1) | O(n) | MongoDB insert |

**Table X.Y:** Computational complexity of key operations. Best/average/worst case complexities are identical unless noted.
```

---

### 9. Error Analysis Table

**Use For:** Categorizing errors or failure modes

```markdown
| Error Type | Count | Percentage | Example |
|:-----------|------:|-----------:|:----------|
| Timeout | 23 | 46% | LLM response >30s |
| Invalid JSON | 15 | 30% | Malformed output |
| Rate Limit | 8 | 16% | API quota exceeded |
| Network Error | 4 | 8% | Connection refused |
| **Total** | **50** | **100%** | - |

**Table X.Y:** Error distribution across 500 test runs. Most common errors are timeouts (46%) and JSON parsing failures (30%).
```

---

## Formatting Rules

### Alignment

```markdown
| Left | Center | Right |
|:-----|:------:|------:|
| Text | Mixed | 123.45 |
```

- **Left (`:---`)**: Text, categories, labels
- **Center (`:---:`)**: Symbols, short codes, categorical data
- **Right (`---:`)**: Numbers, percentages, measurements

### Caption Format

```markdown
**Table X.Y:** Brief description. Explanation of values, units, statistics. Sample size, environment, or source information.
```

**Elements:**
1. **Table number** (X.Y = Section.Table)
2. **Brief title** (what the table shows)
3. **Details** (units, statistics, definitions)
4. **Context** (sample size, environment, source)

### Best Practices

1. **Headers:**
   - Use descriptive names
   - Include units: `Time (ms)`, `Memory (MB)`
   - Avoid abbreviations unless defined in caption

2. **Numbers:**
   - Consistent decimal places (2-3 max)
   - Use commas for thousands: `1,505` not `1505`
   - Include ± for uncertainty
   - Bold best values

3. **Symbols:**
   - ✅ Checkmark (supported)
   - ❌ Cross (not supported)
   - ⚠️ Warning (partial/limited)
   - ⬆️ Increase
   - ⬇️ Decrease
   - → Arrow (leads to)

4. **Totals/Aggregates:**
   - Use bold: `**Total**`
   - Place at bottom or top
   - Use horizontal rule if needed: `---`

5. **Readability:**
   - Maximum 6-7 columns for readability
   - Add S.No for >5 rows
   - Use abbreviations sparingly
   - Group related columns with subheaders if needed

---

## Common Mistakes to Avoid

❌ **DON'T:**
- Mix alignment (pick one per column)
- Forget units in headers
- Use >2 decimal places unless necessary
- Skip the caption
- Create tables wider than 7 columns
- Forget to define abbreviations

✅ **DO:**
- Consistent decimal places
- Include error bars (±)
- Bold your system/best values
- Define all abbreviations
- Use symbols for visual clarity
- Include source/sample size in caption
- Right-align numbers

---

## Table Numbering

```markdown
Table 1.1: System architecture summary
Table 3.1: Module complexity metrics
Table 3.2: Performance benchmarks
Table 4.1: Comparison with baselines
Table 6.1: Experimental results
Table 6.2: Ablation study
```

**Format:** `Table X.Y` where:
- X = Section number
- Y = Table number within section

Start Y from 1 in each section.

---

## Source References

Always cite data sources:

```markdown
**Table X.Y:** ... Source: `crew_monitor` logs, `tests/performance/results.json`
```

Or:

```markdown
**Table X.Y:** ... † Values measured using pytest-cov on commit abc123.
```

---

## Accessibility

For screen readers and accessibility:
- Use descriptive headers
- Avoid pure symbol tables
- Include caption text descriptions
- Define abbreviations
