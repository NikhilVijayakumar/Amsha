# Research Gap Analyst (Paper Publishing)

**Role:** CRITIC - Evaluates the codebase against Scopus-indexing standards, identifying missing experiments, hyperparameter details, and validation metrics.

## Purpose
This skill critiques the project from a research perspective, identifying gaps that need to be addressed to meet academic publication standards and Scopus-indexing requirements.

## Workflow

### 1. Analyze Codebase
Comprehensive review of:
- Code implementation
- Existing documentation
- Test coverage and results
- Configuration and parameters
- Validation methodologies

### 2. Identify Gaps

Look for missing or insufficient elements:

#### Experimental Rigor
- Missing baseline comparisons
- Insufficient test scenarios
- Lack of edge case validation
- No ablation studies

#### Hyperparameter Documentation
- Undefined hyperparameters
- Hardcoded configuration values
- No justification for parameter choices
- Missing sensitivity analysis

#### Performance Validation
- Insufficient performance metrics
- Missing statistical significance tests
- No cross-validation results
- Lack of comparative benchmarks

#### Reproducibility
- Missing random seeds
- Undocumented dependencies
- No version specifications
- Incomplete experimental setup

### 3. Verify Source
**Strict verification is required:**
- Do not assume something is missing without checking the entire codebase
- Verify claims by examining code, tests, and documentation
- Cross-reference with academic standards for the field

### 4. Output

**File:** `docs/paper/analysis/gap_report.md`

**Format:** Markdown report with structured findings

**Content includes:**
- List of missing experiments
- Missing hyperparameter explanations
- Suggestions for improving scientific rigor
- Prioritized action items

## Example Output

```markdown
# Research Gap Analysis Report

## Critical Gaps (Must Address)

### 1. Missing Baseline Comparisons
**Finding:** The rotation algorithm is implemented but not compared against standard methods.

**Impact:** Reviewers cannot assess the novelty or performance advantage.

**Recommendation:** Implement benchmarks against OpenCV rotation and scikit-image transforms.

## Moderate Gaps (Should Address)

### 2. Undefined Hyperparameters
**Finding:** Rotation interpolation method is hardcoded to BILINEAR in `rotation/core.py:L23`.

**Impact:** Lacks justification and sensitivity analysis.

**Recommendation:** Make interpolation method configurable and document the trade-offs.

## Minor Gaps (Nice to Have)

### 3. Limited Performance Metrics
**Finding:** Only execution time is measured; no memory profiling.

**Impact:** Incomplete performance characterization.

**Recommendation:** Add memory usage and accuracy metrics.
```

## When to Use

Invoke Research Gap Analyst when:
- Preparing code for academic publication
- Ensuring compliance with journal standards
- Identifying weaknesses before peer review
- Part of the journal-master workflow

## Related Skills

- [Journal Master](journal-master.md) - Orchestrates Research Gap Analyst and integrates findings
- [Math Extractor](math-extractor.md) - May reveal gaps in mathematical rigor
- [Visual Generator](visual-generator.md) - May expose missing performance data
