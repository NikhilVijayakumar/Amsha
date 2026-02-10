# Final Paper Structure Template

Use this template when synthesizing the final research paper.

---

# [Project Title]: A [Novel Approach/Framework/System] for [Problem Domain]

**Authors:** [Name(s)]  
**Institution:** [University/Organization]  
**Date:** [YYYY-MM-DD]

---

## Abstract

[150-250 words summarizing:]
- Problem statement
- Proposed solution
- Key contributions
- Main results
- Significance

**Keywords:** keyword1, keyword2, keyword3, keyword4, keyword5

---

## 1. Introduction

### 1.1 Background
[Context and motivation for the research]

### 1.2 Problem Statement
[Clear articulation of the problem being addressed]

### 1.3 Research Objectives
[Specific goals of this work]

### 1.4 Contributions
This work makes the following contributions:
1. [Contribution 1]
2. [Contribution 2]
3. [Contribution 3]

### 1.5 Organization
The remainder of this paper is organized as follows: Section 2 reviews related work, Section 3 describes the system architecture, Sections 4-[N] detail each module, Section [N+1] presents experimental results, and Section [N+2] concludes.

---

## 2. Related Work

### 2.1 [Area 1]
[Review of related approaches]

### 2.2 [Area 2]
[Comparison with existing solutions]

### 2.3 Positioning
[How this work differs from and improves upon related work]

**Table 2.1:** Comparison with existing systems
[Insert comparison table from visual-generator]

---

## 3. System Architecture

### 3.1 Overall Design
[High-level architecture description]

**Figure 3.1:** System architecture
[Insert 3-tier diagram from visual-generator]

### 3.2 Design Principles
- **Principle 1:** [e.g., Clean Architecture, Separation of Concerns]
- **Principle 2:** [e.g., Dependency Injection, Protocol-based Design]
- **Principle 3:** [e.g., Immutability, Type Safety]

### 3.3 Technology Stack
**Table 3.1:** Technology choices
| Component | Technology | Reason |
|:----------|:-----------|:-------|
| ... | ... | ... |

---

## 4. Module Analyses

### 4.1 [Module 1 Name] - [Brief Description]

#### 4.1.1 Purpose and Functionality
[What this module does]

#### 4.1.2 Mathematical Foundations
[Insert LaTeX equations from math-extractor]

**Algorithm 4.1:** [Algorithm name]
[Formal algorithm description]

#### 4.1.3 Architecture and Design
**Figure 4.1:** [Module class diagram]
[Insert from visual-generator]

**Key Design Patterns:**
- [Pattern 1]: [Why used]
- [Pattern 2]: [Why used]

#### 4.1.4 Implementation Highlights
[Code snippets or pseudocode for key parts]

### 4.2 [Module 2 Name] - [Brief Description]
[Repeat structure from 4.1]

### 4.N [Module N Name] - [Brief Description]
[Repeat structure from 4.1]

---

## 5. Cross-Module Analysis

### 5.1 Module Interactions
**Figure 5.1:** Module interaction diagram
[Insert sequence diagram from visual-generator showing how modules cooperate]

### 5.2 Dependency Analysis
**Figure 5.2:** Module dependency graph
[Insert from cross-module analysis]

### 5.3 Architectural Patterns
[Recurring patterns identified across modules]

---

## 6. Experimental Evaluation

### 6.1 Experimental Setup
- **Hardware:** [Specifications]
- **Software:** [Python version, key libraries]
- **Dataset:** [Description, size, source]
- **Metrics:** [What was measured and why]

### 6.2 Performance Results
**Table 6.1:** Performance benchmarks
[Insert performance table from visual-generator]

**Figure 6.1:** Performance comparison
[Insert graphs if available]

### 6.3 Baseline Comparisons
[Comparison with standard methods]

**Table 6.2:** Comparison with baselines
| Method | Metric 1 | Metric 2 | Metric 3 |
|:-------|:--------:|:--------:|:--------:|
| Baseline 1 | ... | ... | ... |
| Baseline 2 | ... | ... | ... |
| **Ours** | **...** | **...** | **...** |

### 6.4 Ablation Study
[If applicable: impact of removing each component]

### 6.5 Scalability Analysis
[Performance as N increases]

---

## 7. Discussion

### 7.1 Key Findings
[Interpretation of results]

### 7.2 Advantages
1. [Advantage 1]
2. [Advantage 2]

### 7.3 Limitations
[Honest assessment of limitations]

### 7.4 Lessons Learned
[Insights from implementation]

---

## 8. Future Work

Based on the gap analysis (Appendix A), future work includes:

### 8.1 Critical Improvements
[From critical gaps in research-gap-analyst output]

### 8.2 Potential Extensions
1. [Extension 1]
2. [Extension 2]

---

## 9. Conclusion

[Summary of:]
- What was accomplished
- Key contributions
- Impact and significance
- Final thoughts

---

## References

[1] Author. "Title." Journal/Conference, Year.  
[2] ...

---

## Appendix A: Gap Analysis

[Insert comprehensive gap report from research-gap-analyst]

**Table A.1:** Summary of identified gaps
| Gap | Severity | Status |
|:----|:---------|:-------|
| ... | ... | ... |

---

## Appendix B: Complete Algorithm Index

[List all algorithms with page/section references]

1. Algorithm 4.1: [Name] - Page X
2. Algorithm 4.2: [Name] - Page Y

---

## Appendix C: Module Comparison Matrix

**Table C.1:** Detailed module metrics
[Insert module comparison table]

---

## Appendix D: Verification and Traceability

### Code-to-Math Mapping
[Table showing variable name mappings between code and mathematical notation]

### Source Code References
All claims in this paper are traceable to specific source files:
- Section 4.1: `src/path/to/module1/`
- Section 4.2: `src/path/to/module2/`

---

# Formatting Guidelines

## Equations
- Use `$$...$$` for display equations
- Number important equations: \\tag{4.1}
- Always define variables

## Figures and Tables
- Number sequentially: Figure 3.1, Table 4.2
- Always include captions
- Reference in text before showing

## Code References
- Format: `src/module/file.py:L42-L58`
- Use inline code: \`ClassName\`, \`method_name()\`
- Keep code snippets under 15 lines

## Citations
- Use [1], [2] style
- Cite related work, libraries, datasets
