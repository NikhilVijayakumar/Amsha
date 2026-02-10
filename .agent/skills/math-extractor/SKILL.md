---
name: math-extractor
description: Scans the codebase for logic and algorithms. It must output formal LaTeX equations to docs/paper/mathematics/math_logic.md.
---

# Math Extractor Skill

## Purpose
This skill scans the codebase to identify mathematical logic, algorithms, and formulas. It translates these findings into formal LaTeX equations suitable for a research paper.

## Instructions
1.  **Scan Codebase**: specificially looking for algorithmic logic, mathematical computations, and data transformations.
2.  **Verify Source**: strict verification against the actual source code is required. Do not hallicinate equations. Ensure variable names in the LaTeX match the code or are clearly mapped.
3.  **Output**:
    -   File: `docs/paper/mathematics/math_logic.md`
    -   Format: Markdown with LaTeX equations (using `$...$` or `$$...$$`).
    -   Content:
        -   Description of the algorithm/logic.
        -   Formal LaTeX representation.
        -   Reference to the source code file and line numbers.

## Verification
-   Before writing the output, verify that every equation strictly corresponds to the implemented logic in the code.
-   Check that variable definitions are consistent between the code and the LaTeX.

## Supporting Materials

### Resources
- **[latex_templates.md](resources/latex_templates.md)** - LaTeX equation templates for common patterns (statistical calculations, grading formulas, complexity notation, variable naming conventions)

### Examples
- **[extracted_math_example.md](examples/extracted_math_example.md)** - Complete example showing algorithms extracted from the output_process module with proper LaTeX formalization and variable mapping

## Quality Indicators

When using these materials:
- **Templates:** Match your algorithm to the closest template (statistics, grading, performance metrics)
- **Variable Mapping:** Always include a table mapping code variables to LaTeX symbols
- **Complexity Analysis:** Include time/space complexity for all algorithms
- **Source References:** Every equation must cite file path and line numbers
