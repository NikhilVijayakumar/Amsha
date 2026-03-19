---
name: paper-drafter
description: DRAFTER. Converts synthesized data into a polished, Scopus-indexed level academic section, ensuring formal tone and correct formatting (LaTeX/Mermaid).
---

# Paper Drafter (Academic Section Writer)

## Purpose
The `paper-drafter` skill is the fourth stage in the 5-stage journal generation pipeline (Plan -> Analyze -> Augment -> Draft -> Review). It transforms the raw synthesized facts from the `analyzer` (or `augmenter`) into a highly polished, publication-ready academic section.

## Input
- **YAML Plan:** The `docs/paper/Amsha/drafts/plan/plan_[section_name].yaml` (for drafting instructions).
- **Analysis Document:** The `docs/paper/Amsha/drafts/details/[N]. [Section Name]/augmented_analysis_[section_name].md` (if stage 3 was executed) OR `docs/paper/Amsha/drafts/details/[N]. [Section Name]/analysis_[section_name].md` (if stage 3 was skipped).

## Output
A formally drafted markdown section saved to `docs/paper/Amsha/drafts/details/[N]. [Section Name]/draft_[section_name].md`.

## Responsibilities
1. **Academic Prose:** Convert bullet points, raw facts, and disjointed models into cohesive, formal, Scopus-indexed quality academic prose.
2. **Formatting:** Correctly embed LaTeX for mathematical equations and Mermaid.js syntax for system architecture/interaction diagrams based on the analysis file.
3. **ESWA Visual Hierarchy Rule (Mandatory for Methodology):** When drafting the "Proposed Methodology" section, you MUST format and output two distinctly separate architecture diagrams:
   - **Logical Architecture ("Brain"):** Conceptual flow, agent interactions, decision layers (strict segregation: NO infrastructure).
   - **Physical Architecture ("Body"):** Deployment structure, containers, APIs, databases (strict segregation: NO conceptual logic).
4. **Adhere to Instructions:** Follow the explicit drafting styles, structural requirements, and tonal guidelines defined in the `instructions.drafter` section of the YAML plan.
5. **Integration:** Ensure the section flows logically and is suitable for later integration into the `FINAL_JOURNAL_REPORT.md` by the orchestrator.

## Operating Principles
- **Rooted in Analysis:** The drafter must *only* write about concepts established in the analysis document. It cannot introduce new technical claims or empirical results not provided in the input.
- **Formal Tone Avoidance:** Avoid casual language, marketing speak, or colloquialisms. Use passive voice where customary in technical journals.
- **Visual Callouts:** Explicitly format diagrams or mathematical blocks so they render correctly in standard markdown parsers.

## Supporting Materials
- **Examples:** Refer to the `examples/` directory for expected input/output artifacts.
- **Resources:** Refer to the `resources/` directory for critical guidelines, constraints, and tone rules.
- **Scripts:** Refer to the `scripts/` directory for programmatic execution components.
