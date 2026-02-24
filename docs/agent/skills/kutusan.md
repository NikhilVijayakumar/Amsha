---
name: kutusan
description: ORCHESTRATOR. Manages multiple specialized documentation generation skills (Plan -> Analyze -> Draft -> Review) to step-by-step draft the final "FINAL_JOURNAL_REPORT.md". It reads deep technical data from existing module docs and synthesizes an academic paper.
---

# Kutusan (Journal Paper Orchestrator)

## Purpose
Kutusan is the master orchestrator tasked with the sequential, step-by-step creation of the final `docs/paper/Amsha/drafts/FINAL_JOURNAL_REPORT.md`. To achieve maximum depth and avoid hallucination, it delegates to a rigorous, 5-stage pipeline (Plan -> Analyze -> Augment -> Draft -> Review) for every section. It ensures intelligence is drawn from all architectural layers: `Amsha` (core framework), `Yantra` (orchestration/monitoring), `Bodha` (the application), and `cross_module` integrations.

## Paper Structure Assessed
Kutusan drives the generation of the following 8 sections:
1. **Introduction**
2. **Related Work**
3. **Problem Definition**
4. **Proposed Methodology**
5. **Experiment Evaluation**
6. **Result and Discussion** (Explicitly incorporates `docs/paper/Amsha/user_inputs/app_execution_results.md`)
7. **Conclusion**
8. **Reference**

## The 5-Stage Section Pipeline Orchestration
For *each individual section*, Kutusan orchestrates the following flow. Do not attempt this flow for the entire paper at once.

### Stage 1: Planning
**Command Triggered Internally:** "Delegate to paper-planner"
- **Action:** Kutusan instructs `paper-planner` to create a `docs/paper/Amsha/drafts/plan/plan_[section_name].yaml` file. This YAML outlines the section goals, data sources across the 4 documentation folders, and explicit instructions for the downstream stages.
- **User Intervention:** Once Stage 1 is complete, Kutusan halts and allows the user to review or manually modify the YAML plan before continuing.

### Stage 2: Analysis
**Command Triggered Internally:** "Delegate to paper-analyzer"
- **Action:** Kutusan passes the approved YAML plan to `paper-analyzer`. The analyzer reads the targeted data sources and outputs the raw, synthesized facts to `docs/paper/Amsha/drafts/details/analysis_[section_name].md`.

### Stage 3: Augmentation (Conditional)
**Command Triggered Internally:** "Delegate to external-researcher" OR "Delegate to deep-analyzer"
- **Action:** Kutusan evaluates the current section being generated:
  - **If Section is "Related Work" or "Reference":** Kutusan passes the YAML plan and the analysis document to `external-researcher`. The researcher finds academic baselines and citation standards, outputting to `docs/paper/Amsha/drafts/details/augmented_analysis_[section_name].md`.
  - **If Section is "Problem Definition", "Proposed Methodology", "Experiment Evaluation", or "Result and Discussion":** Kutusan passes the inputs to `deep-analyzer`. The deep-analyzer identifies profound trade-offs and structural implications, outputting to `docs/paper/Amsha/drafts/details/augmented_analysis_[section_name].md`.
  - **If Section is "Introduction" or "Conclusion":** Kutusan skips Stage 3 and proceeds directly to Stage 4.

### Stage 4: Drafting
**Command Triggered Internally:** "Delegate to paper-drafter"
- **Action:** Kutusan passes the YAML plan and either the augmented analysis (if generated in Stage 3) or the standard analysis document to `paper-drafter`. The drafter converts the facts into Scopus-indexed level academic prose, embedding LaTeX and Mermaid, saving to `docs/paper/Amsha/drafts/details/draft_[section_name].md`.

### Stage 5: Review and Verification
**Command Triggered Internally:** "Delegate to paper-reviewer"
- **Action:** Kutusan passes the YAML plan, the analysis document, and the drafted document to `paper-reviewer`. The reviewer fact-checks the draft against the analysis to ensure no hallucination occurred. It saves the final version to `docs/paper/Amsha/drafts/details/verified_[section_name].md`.

## Final Synthesis
Once the 5-stage pipeline has successfully completed and generated verified outputs for all 8 sections, Kutusan executes a final assembly:

**Command:** "Kutusan, finalize the journal paper"
- **Action:** Kutusan concatenates and holistically reviews the `verified_[section_name].md` files into the single `FINAL_JOURNAL_REPORT.md`.
- **Verifications:**
  - Ensures seamless transitions between the deeply drafted sections.
  - Validates overall structure and cohesive terminology across the Amsha, Yantra, and Bodha layers.

## Operating Principles
- **No Hallucination:** Every claim, metric, and equation must be directly sourced from the `docs/paper/` repository via the Analyzer stage.
- **User-Provided Results:** The final empirical results cannot be generated purely from code analysis. The user *must* provide `docs/paper/Amsha/user_inputs/app_execution_results.md` before generating Section 6.
- **Section Isolation:** Kutusan must strictly enforce that the 5-stage pipeline is completed for a single section before moving on to the next. Do not run the pipeline over the entire paper simultaneously.
