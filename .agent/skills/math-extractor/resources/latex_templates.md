# LaTeX Equation Template

Use these templates when extracting mathematical logic from code.

## Algorithm Complexity

```latex
% Time Complexity
T(n) = O(n \log n)

% Space Complexity
S(n) = O(n)
```

## Statistical Calculations

```latex
% Mean/Average
\bar{x} = \frac{1}{n} \sum_{i=1}^{n} x_i

% Weighted Mean
\bar{x}_w = \frac{\sum_{i=1}^{n} (w_i \cdot x_i)}{\sum_{i=1}^{n} w_i}

% Standard Deviation
\sigma = \sqrt{\frac{1}{n} \sum_{i=1}^{n} (x_i - \bar{x})^2}

% Variance
\sigma^2 = \frac{1}{n} \sum_{i=1}^{n} (x_i - \bar{x})^2
```

## Grading/Scoring Formulas

```latex
% Linear normalization
score_{norm} = \frac{score - score_{min}}{score_{max} - score_{min}} \times 100

% Weighted score
Score_{final} = \sum_{i=1}^{n} (w_i \cdot score_i) \quad \text{where} \sum w_i = 1

% Grade assignment
Grade = \begin{cases}
A & \text{if } score \geq 90 \\
B & \text{if } 80 \leq score < 90 \\
C & \text{if } 70 \leq score < 80 \\
D & \text{if } 60 \leq score < 70 \\
F & \text{if } score < 60
\end{cases}
```

## Performance Metrics

```latex
% Accuracy
Accuracy = \frac{TP + TN}{TP + TN + FP + FN}

% Precision
Precision = \frac{TP}{TP + FP}

% Recall
Recall = \frac{TP}{TP + FN}

% F1 Score
F1 = 2 \cdot \frac{Precision \cdot Recall}{Precision + Recall}
```

## Repository/Database Operations

```latex
% CRUD complexity
\begin{aligned}
&\text{Create:} \quad O(1) \\
&\text{Read:} \quad O(n) \\
&\text{Update:} \quad O(1) \\
&\text{Delete:} \quad O(1)
\end{aligned}
```

## Variable Naming Conventions

When translating code variables to mathematical notation:

| Code Variable | LaTeX Symbol | Description |
|:--------------|:-------------|:------------|
| `score` | $s$ | Score value |
| `weight` | $w$ | Weight factor |
| `count` | $n$ | Number of items |
| `total` | $T$ | Total/sum |
| `average` | $\bar{x}$ | Mean value |
| `std_dev` | $\sigma$ | Standard deviation |
| `threshold` | $\theta$ | Threshold value |
| `alpha`, `beta` | $\alpha$, $\beta$ | Greek parameters |
| `delta` | $\Delta$ | Change/difference |
| `min_value` | $x_{min}$ | Minimum value |
| `max_value` | $x_{max}$ | Maximum value |

## Code-to-LaTeX Example

**Python Code:**
```python
def weighted_average(scores: List[float], weights: List[float]) -> float:
    return sum(s * w for s, w in zip(scores, weights)) / sum(weights)
```

**LaTeX Representation:**
```latex
\bar{x}_w = \frac{\sum_{i=1}^{n} (w_i \cdot s_i)}{\sum_{i=1}^{n} w_i}
```

**With Variable Mapping:**
- `scores` → $s_i$ where $i \in \{1, \ldots, n\}$
- `weights` → $w_i$ where $i \in \{1, \ldots, n\}$
- Return value → $\bar{x}_w$ (weighted mean)

## Format Requirements

1. **Inline equations**: Use `$...$` for simple expressions  
   Example: The average is $\bar{x} = 42$

2. **Display equations**: Use `$$...$$` for important formulas  
   Example:
   ```
   $$
   Score = \frac{\sum_{i=1}^{n} x_i}{n}
   $$
   ```

3. **Aligned equations**: Use `\begin{aligned}...\end{aligned}`  
   Example:
   ```latex
   \begin{aligned}
   Score_{raw} &= \sum_{i=1}^{n} x_i \\
   Score_{norm} &= \frac{Score_{raw}}{n}
   \end{aligned}
   ```

4. **Always include**:
   - Source file reference: `src/path/to/file.py:L42-L48`
   - Variable mapping table
   - Complexity analysis if applicable
