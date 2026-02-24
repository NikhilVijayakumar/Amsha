---
name: paper-planner
description: PLANNER. Generates a detailed, editable YAML execution plan for a specific journal section, outlining data sources (Amsha, Yantra, Bodha, cross_module) and pipeline instructions.
---

# Paper Planner (Journal Section Execution Planner)

## Purpose
The `paper-planner` skill is the first stage in the 4-stage journal generation pipeline (Plan -> Analyze -> Draft -> Review). Its purpose is to create a detailed, executable, and reviewable YAML document for a specific section of the final research paper (e.g., Introduction, Methodology). 

## Input
- **Target Section:** The specific section of the paper to plan (e.g., "Proposed Methodology").
- **Overall Paper Goal:** Context about the paper being generated.

## Output
A YAML file saved to `docs/paper/Amsha/drafts/plan/plan_[section_name].yaml`.

## Responsibilities
1. **Identify Required Data Locations:** Determine exactly *where* the data required for this section lives across the documentation structure:
   - `Amsha` (Core framework details)
   - `Yantra` (Orchestration and monitoring details)
   - `Bodha` (Application-level usage/results)
   - `cross_module` (System-level interactions, diagrams, and mathematical models)
2. **Define Section Requirements:** Outline the specific academic points, formalisms, and arguments that must be present in the final section.
3. **Formulate Instructions for Pipeline Stages:** Provide explicit, targeted instructions for the subsequent `analyzer`, `drafter`, and `reviewer` stages.

## YAML Plan Structure Template
```yaml
section: "[Section Name]"
goal: "[Brief description of what this section must achieve]"
data_sources:
  amsha:
    - path: "[Relative path to Amsha doc]"
      extract: "[Focus data to extract]"
  yantra:
    - path: "[Relative path to Yantra doc]"
      extract: "[Focus data to extract]"
  bodha:
    - path: "[Relative path to Bodha doc]"
      extract: "[Focus data to extract]"
  cross_module:
    - path: "[Relative path to cross-module doc]"
      extract: "[Focus data to extract]"
instructions:
  analyzer:
    - "[Specific instruction on how to synthesize the data sources]"
  augmenter:
    - "[Specific instruction for deep-analyzer or external-researcher, e.g., 'Enforce referencing only Q1 Scopus indexed journals' or 'Detail architectural trade-offs']"
  drafter:
    - "[Specific instruction on tone, formatting (LaTeX/Mermaid), and structure]"
  reviewer:
    - "[Specific verification criteria to ensure accuracy and academic rigor]"
```

## Operating Principles
- **No Drafting:** This skill only plans; it does not synthesize data or write the final prose.
- **Traceability:** Paths in the YAML must accurately reflect the structure of `docs/paper/Amsha`.
- **Reviewability:** The YAML output is presented to the user for optional review and modification before the next stage begins.
