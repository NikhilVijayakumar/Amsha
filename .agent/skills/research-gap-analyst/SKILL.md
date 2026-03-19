---
name: research-gap-analyst
description: Evaluates the codebase against Scopus-indexing standards. It should identify missing experiments, hyperparameter details, or validation metrics. Save to docs/paper/analysis/gap_report.md.
---

# Research Gap Analyst Skill

## Purpose
This skill critiques the project from a research perspective, identifying gaps that need to be addressed to meet Scopus-indexing standards.

## Instructions
1.  **Analyze Codebase**: Review the code, documentation, and existing results.
2.  **Identify Gaps**: Look for:
    -   Missing experiments or validation scenarios.
    -   Undefined or hardcoded hyperparameters.
    -   Lack of baseline comparisons.
    -   Insufficient performance metrics.
3.  **Verify Source**: strict verification against the actual source code is required. Do not assume something is missing without checking the entire codebase.
4.  **Output**:
    -   File: `docs/paper/analysis/gap_report.md`
    -   Format: Markdown report.
    -   Content:
        -   List of missing experiments.
        -   Details on missing hyperparameter explanations.
        -   Suggestions for improving the "scientific rigor" of the project.

## Verification
-   Double-check that identified "missing" features are indeed strictly absent from the codebase.

## Supporting Materials

### Resources
- **[gap_checklist.md](resources/gap_checklist.md)** - Comprehensive checklist covering experimental rigor, hyperparameter documentation, performance validation, reproducibility, code quality, and academic standards with gap severity classification

### Examples
- **[gap_analysis_example.md](examples/gap_analysis_example.md)** - Complete gap analysis for the Amsha project showing critical, moderate, and minor gaps with specific file locations, impact assessments, recommendations, and effort estimates

## Quality Indicators

When using these materials:
- **Checklist:** Use all 6 sections systematically (experimental, hyperparameters, performance, reproducibility, code quality, academic)
- **Severity:** Critical = blocks publication, Moderate = weakens paper, Minor = nice-to-have
- **Recommendations:** Must be specific and actionable with effort estimates
- **Verification:** Every gap must reference actual code location (file:line)
