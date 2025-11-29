# Functional Requirements: Amsha LLM Factory

| |                |
| :--- |:---------------|
| **Version:** | 1.1            |
| **Date:** | November 28, 2025 |
| **Status:** | Active         |

-----

### 1. Introduction

This document specifies the functional requirements for the **Amsha LLM Factory**. The purpose of this library is to provide a centralized, configuration-driven system for defining and instantiating pre-configured `crewai.LLM` objects using dependency injection.

-----

### 2. Core Problem Statement

In applications utilizing multiple Large Language Models, configurations are often scattered, leading to duplication and inconsistency. **Amsha** solves this by abstracting LLM configuration into a YAML file and providing a DI container for creating consistently configured LLM instances.

-----

### 3. Goals

-   **Centralization:** All LLM definitions in a single YAML file.
-   **Dependency Injection:** Provide ready-to-use LLM instances via `LLMContainer`.
-   **Consistency:** Enforce consistent parameter usage for 'creative' vs 'evaluation' tasks.

-----

### 4. Core Features

#### 4.1. Configuration (`FR-LLM-CONF`)

-   **FR-LLM-CONF-01: YAML Source:** Load configurations from a user-provided YAML file.
-   **FR-LLM-CONF-02: Use Case Grouping:** Support distinct use cases (e.g., 'creative', 'evaluation').
-   **FR-LLM-CONF-03: Parameter Sets:** Group parameters (temperature, etc.) by use case.
-   **FR-LLM-CONF-04: Multiple Models:** Support multiple models per use case (e.g., 'phi', 'gpt').

#### 4.2. Instantiation (`FR-LLM-INST`)

-   **FR-LLM-INST-01: DI Container:** Provide `LLMContainer` with `creative_llm` and `evaluation_llm` providers.
-   **FR-LLM-INST-02: Builder Pattern:** Internally use `LLMBuilder` to construct instances based on config.
-   **FR-LLM-INST-03: Dynamic Selection:** Allow selecting specific models via key (e.g., `builder.build_creative(model_key="llama")`).

#### 4.3. Utilities (`FR-LLM-UTIL`)

-   **FR-LLM-UTIL-01: Telemetry:** Provide utility to disable CrewAI telemetry.
