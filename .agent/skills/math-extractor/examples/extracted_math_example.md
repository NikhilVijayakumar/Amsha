# Example: Extracted Mathematics from output_process Module

This example shows how math-extractor converts Python code to formal LaTeX.

## Source Code Location
`src/nikhil/amsha/output_process/evaluator.py:L23-L45`

---

## Algorithm 1: Weighted Score Calculation

### Code Implementation
```python
def calculate_weighted_score(
    raw_scores: List[float],
    weights: List[float]
) -> float:
    """Calculate weighted average of scores."""
    total_weight = sum(weights)
    weighted_sum = sum(score * weight 
                       for score, weight in zip(raw_scores, weights))
    return weighted_sum / total_weight
```

### Mathematical Formalization

The weighted score is computed as:

$$
Score_w = \frac{\sum_{i=1}^{n} (w_i \cdot s_i)}{\sum_{i=1}^{n} w_i}
$$

**Where:**
- $Score_w$ = Final weighted score (`return value`)
- $n$ = Number of score components (`len(raw_scores)`)
- $s_i$ = Individual raw score (`raw_scores[i]`)
- $w_i$ = Weight for score component $i$ (`weights[i]`)

**Complexity:**
- Time: $O(n)$ - Single pass through scores
- Space: $O(1)$ - Constant memory usage

---

## Algorithm 2: Relative Grading (Curve)

### Code Implementation
```python
def apply_curve(scores: List[float], mean_target: float = 75.0) -> List[float]:
    """Apply grade curve to normalize scores."""
    current_mean = sum(scores) / len(scores)
    adjustment = mean_target - current_mean
    return [min(100, score + adjustment) for score in scores]
```

### Mathematical Formalization

The curved score for each student is:

$$
s'_i = \min(100, s_i + \Delta)
$$

Where the adjustment factor is:

$$
\Delta = \mu_{target} - \mu_{current}
$$

And the current mean is:

$$
\mu_{current} = \frac{1}{n} \sum_{i=1}^{n} s_i
$$

**Variable Mapping:**
- $s_i$ = Original score (`scores[i]`)
- $s'_i$ = Curved score (`return[i]`)
- $\Delta$ = Grade adjustment (`adjustment`)
- $\mu_{target}$ = Target mean score (`mean_target`)
- $\mu_{current}$ = Current mean (`current_mean`)
- $n$ = Number of students (`len(scores)`)

**Constraints:**
- $s'_i \leq 100$ (capped at maximum)
- $s_i \in [0, 100]$ (valid score range)

**Complexity:**
- Time: $O(n)$ for mean calculation + $O(n)$ for adjustment = $O(n)$
- Space: $O(n)$ for output list

---

## Algorithm 3: Letter Grade Assignment

### Code Implementation
```python
def assign_grade(score: float) -> str:
    """Assign letter grade based on score."""
    if score >= 90:
        return 'A'
    elif score >= 80:
        return 'B'
    elif score >= 70:
        return 'C'
    elif score >= 60:
        return 'D'
    else:
        return 'F'
```

### Mathematical Formalization

$$
Grade(s) = \begin{cases}
A & \text{if } s \geq 90 \\
B & \text{if } 80 \leq s < 90 \\
C & \text{if } 70 \leq s < 80 \\
D & \text{if } 60 \leq s < 70 \\
F & \text{if } s < 60
\end{cases}
$$

**Where:**
- $s$ = Numerical score (`score` parameter)
- $Grade(s)$ = Letter grade (`return value`)

**Complexity:**
- Time: $O(1)$ - Constant comparison operations
- Space: $O(1)$ - Single character return

---

## Verification

✅ All equations verified against source code  
✅ Variable names mapped correctly  
✅ Complexity analysis included  
✅ Code references provided
