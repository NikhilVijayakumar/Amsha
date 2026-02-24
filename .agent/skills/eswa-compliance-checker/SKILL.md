---
name: eswa-compliance-checker
description: COMPLIANCE. Post-review skill. Validates the final concatenated journal report against strict ESWA structural benchmarks (word count, citation recency, figure density, tone). 
---

# ESWA Compliance Checker (Global Structural Validator)

## Purpose
The `eswa-compliance-checker` is invoked by Kutusan *after* all 11 sections have successfully completed the 5-stage pipeline and have been verified. Its purpose is to perform a global, document-wide audit to ensure the assembled `FINAL_JOURNAL_REPORT.md` adheres perfectly to the Expert Systems with Applications (ESWA) golden rules.

## Input
- The 11 `verified_[section_name].md` files (from within their respective section subfolders) or the concatenated `FINAL_JOURNAL_REPORT.md`.

## Output
A compliance report saved to `docs/paper/Amsha/drafts/details/eswa_compliance_report.md`. If major violations are found, Kutusan halts finalization until they are resolved.

## Responsibilities & Enforcement Benchmarks

### 1. Structural Benchmarks
- **Length:** Ensure the total paper is between 6,500 and 8,500 words.
- **Reference Count:** Verify exactly 35 to 45 references exist.
- **Citation Recency:** Verify that 60-70% of citations are in the window (2022-2026).
- **Venue Relevance:** Verify that 2-4 citations are unequivocally from the ESWA journal.
- **Figure/Table Density:** Ensure roughly 1 figure or table per 1-1.5 double-column pages (approx. 7-10 visuals total).

### 2. Mandatory Methodological Elements
- **Statistical Tests:** If empirical results show <5% improvement, verify that a formal statistical significance test (e.g., t-test, Wilcoxon, p < 0.05) is present in the Results section.
- **Complexity Analysis:** Verify the Methodology section contains explicit Time/Space Big-O complexity tables.
- **Robustness:** Verify the Results section contains sensitivity or robustness analysis (e.g., noise injection, heatmaps).

### 3. Immediate Rejection Triggers
Scan the entire document for:
- Mentions of blogs or non-peer-reviewed websites in the bibliography (excluding official software repos if strictly necessary).
- Use of forbidden, informal vocabulary: "Awesome", "Easy", "Simple", "Very", "A lot".

## Operating Principles
- **Strict Enforcement:** This agent must act like Desk Editor. Do not "soft pass" a document with 34 references or 8,600 words.
- **Actionable Reporting:** For every failure, output the exact metric (e.g., "Word count is 6,240. Below the 6,500 minimum. Expand Results discussion.").

## Supporting Materials
- **Examples:** Refer to the `examples/` directory for expected input/output artifacts.
- **Resources:** Refer to the `resources/` directory for critical guidelines, constraints, and tone rules.
- **Scripts:** Refer to the `scripts/` directory for programmatic execution components.
