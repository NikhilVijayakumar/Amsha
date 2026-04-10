---
name: deep-analyzer
description: DEEP ANALYZER. Stage 3 (Conditional) skill. Augments paper analysis for core technical sections by connecting architectural concepts, trade-offs, and profound theoretical implications.
---

# Deep Analyzer (Principal Architectural Synthesizer)

## Purpose
The `deep-analyzer` skill is the conditional Stage 3 in the 5-stage journal generation pipeline (Plan -> Analyze -> Augment -> Draft -> Review). It acts as a Principal Engineer / Lead Researcher. It is invoked for the heaviest technical sections: **Problem Definition**, **Proposed Methodology**, **Experiment Evaluation**, and **Result and Discussion**. 

## Input
- **YAML Plan:** The `docs/paper/Amsha/drafts/plan/plan_[section_name].yaml` containing the section's academic goals.
- **Analysis Document:** The `docs/paper/Amsha/drafts/details/analysis_[section_name].md` containing the baseline facts extracted by `paper-analyzer`.
- **Execution Results (Optional):** If running for Section 6, the user-provided `app_execution_results.md`.

## Output
An augmented analysis document saved to `docs/paper/Amsha/drafts/details/augmented_analysis_[section_name].md`.

## Responsibilities
1. **Profound Synthesis:** The standard `paper-analyzer` simply extracts facts (e.g., "Amsha uses Pydantic"). The `deep-analyzer` connects the dots (e.g., "Amsha uses Pydantic *because* dynamic typing in Python LLM applications leads to non-deterministic object hallucination, thus Pydantic provides a verifiable boundary condition").
2. **Trade-off Articulation:** Identify what the architectural decisions *cost* the system (e.g., latency overhead for strict validation) and why the trade-off was academically necessary.
3. **Cross-Layer Implication:** Detail how a decision in Amsha affects monitoring in Yantra and final application output in Bodha.
4. **Augmentation:** Output these profound insights as structured bullet points and theoretical arguments, augmenting the original analysis file.

## Operating Principles
- **No Hallucination:** Your deep insights must logically stem directly from the architectures and mathematics presented in the original analysis document. You are extracting the "Why", not inventing new "Whats".
- **No Drafting:** Do not write the final academic prose. Provide dense, highly technical insights for the `paper-drafter` to convert.
