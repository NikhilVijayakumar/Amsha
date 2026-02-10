# Math Extractor (Paper Publishing)

**Role:** ANALYZER - Scans the codebase for mathematical logic and algorithms, converting them to formal LaTeX equations for research papers.

## Purpose
This skill identifies mathematical computations, algorithms, and data transformations in the codebase and translates them into formal LaTeX equations suitable for academic publication.

## Workflow

### 1. Scan Codebase
Systematically search the project for:
- Algorithmic logic
- Mathematical computations
- Data transformations
- Statistical operations
- Optimization algorithms

### 2. Verify Source
**Strict verification is required** - Do not hallucinate equations:
- Every equation must correspond to actual code
- Variable names in LaTeX must match the code or be clearly mapped
- Line numbers must be referenced for traceability

### 3. Output

**File:** `docs/paper/mathematics/math_logic.md`

**Format:** Markdown with LaTeX equations (using `$...$` or `$$...$$`)

**Content includes:**
- Description of the algorithm/logic
- Formal LaTeX representation
- Reference to source code file and line numbers
- Variable mapping (code → mathematical notation)

## Example Output

```markdown
## Algorithm: Rotation Angle Calculation

**Source:** `src/amsha/rotation/core.py:L45-L52`

The rotation angle is computed using the arctangent of the normalized displacement:

$$
\theta = \arctan\left(\frac{\Delta y}{\Delta x}\right) \times \frac{180}{\pi}
$$

Where:
- $\theta$ = rotation angle in degrees (`angle` in code)
- $\Delta y$ = vertical displacement (`delta_y` in code)
- $\Delta x$ = horizontal displacement (`delta_x` in code)
```

## Verification Checklist

Before finalizing the output:
- [ ] Every equation corresponds to implemented logic
- [ ] Variable definitions are consistent between code and LaTeX
- [ ] Source code references include file paths and line numbers
- [ ] No assumptions or theoretical equations not present in code

## When to Use

Invoke Math Extractor when:
- Preparing a research paper from the codebase
- Documenting complex algorithms for publication
- Creating mathematical specifications for peer review
- Part of the journal-master workflow

## Related Skills

- [Journal Master](journal-master.md) - Orchestrates Math Extractor along with other paper-publishing skills
- [Visual Generator](visual-generator.md) - Creates architectural diagrams for the paper
- [Research Gap Analyst](research-gap-analyst.md) - Identifies missing experimental details
