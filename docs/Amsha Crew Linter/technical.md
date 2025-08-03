# Amsha Crew Linter: Solution Design & Implementation Guide

### 1. Introduction

This document provides a practical guide on how the various components of the **Amsha** toolkit (Guardrails, Processors, Modelers) are orchestrated to fulfill the functional requirements of the **Amsha Crew Linter**. It serves as a bridge between the abstract requirements and the concrete implementation plan.

-----

### 2. Core Validation Workflow

The Linter operates on a simple, repeatable workflow for each "use case" it analyzes:

1.  **Discover & Parse:** The client application locates and parses the three key artifacts: the agent definition (`..._agent.yaml`), the task definition (`..._task.yaml`), and the requirement (`..._requirement.md`).
2.  **Orchestrate Guardrails:** The `AmshaCrewLinter` service receives the parsed data and executes a series of pre-configured "Guardrails" on it.
3.  **Generate Report:** The results from each guardrail are aggregated into a single, structured `LinterReport` object, which is then returned to the client.

-----

### 3. Component Mapping to Linter Requirements

This section details which components are used to satisfy each of the Linter's core functional requirements.

#### `FR-LINT-VC-01`: Agent-Task Synergy Validation

This requirement is about ensuring the agent is well-suited for the task.

-   **Implementing Component:** `SimilarityGuardrail`
-   **Workflow:**
    1.  The Linter extracts the `agent.goal` text and the `task.description` text.
    2.  These are passed to the `SimilarityGuardrail.execute()` method as `source_text` and `target_text`.
    3.  The guardrail calculates the cosine similarity to measure semantic alignment.
    4.  A `GuardrailResult` is returned, indicating a "PASS" if the score is above the configured threshold.

#### `FR-LINT-VC-02`: Requirement-to-Component Validation

This ensures both the agent and task align with the original business requirement. This is a multi-faceted check.

-   **Implementing Components:** `MarkdownProcessor`, `KeywordCoverageGuardrail`, `SimilarityGuardrail`, `BERTopicGuardrail`.
-   **Workflow:**
    1.  The `MarkdownProcessor.to_plaintext()` method is used to get a clean text string from the `_requirement.md` file.
    2.  **Keyword Check:** The `KeywordCoverageGuardrail` is executed to verify that critical keywords from the requirement text are present in the agent's `goal` and the task's `description`.
    3.  **Similarity Check:** The `SimilarityGuardrail` is executed to measure the semantic similarity between the full requirement text and the agent/task definitions.
    4.  **Thematic Alignment (Advanced):** The `BERTopicGuardrail` is executed to model the topics of the requirement text and the agent/task definitions separately. It then compares the topics to ensure they are thematically aligned, providing a deeper check than simple similarity.

#### `FR-LINT-VC-03`: Procedural Validation

This validates the logical flow of steps described within a task's description.

-   **Implementing Components:** A custom "Step Extraction" utility, `NetworkXGuardrail`.
-   **Workflow:**
    1.  A text parsing utility (e.g., using regular expressions or a library like spaCy) extracts an ordered list of steps from the `task.description`.
    2.  A directed graph is constructed from these steps, where an edge connects `Step N` to `Step N+1`.
    3.  This graph is passed to the `NetworkXGuardrail.execute()` method.
    4.  The guardrail analyzes the graph for structural integrity, specifically checking for **cycles** (logical impossibilities) and **isolated nodes** (orphaned steps).

#### `FR-LINT-GR-01`, `FR-LINT-RP-01`, `FR-LINT-RP-02`: Pluggable Execution and Reporting

These requirements are fulfilled by the core architecture of the linter itself.

-   **Implementing Components:** `AmshaCrewLinter` service, `IGuardrail` interface, `LinterReport` and `GuardrailResult` Pydantic models.
-   **Workflow:**
    1.  The client application creates a list of configured guardrail instances (e.g., `[SimilarityGuardrail(threshold=0.8), KeywordCoverageGuardrail(...)]`).
    2.  This list is injected into the `AmshaCrewLinter`'s constructor.
    3.  When `lint_use_case()` is called, the linter iterates through the list, executing each guardrail by calling its `execute()` method.
    4.  Each call returns a `GuardrailResult` object.
    5.  All results are collected into the final `LinterReport` object, satisfying the reporting requirements. This design makes the entire process modular and extensible.