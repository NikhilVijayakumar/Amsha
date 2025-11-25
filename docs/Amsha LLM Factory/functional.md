# Functional Requirements: Amsha LLM Factory

| |                |
| :--- |:---------------|
| **Version:** | 1.0            |
| **Date:** | August 2, 2025 |
| **Author:** | Nikhil         |
| **Status:** | Draft          |

-----

### 1. Introduction

This document specifies the functional requirements for the **Amsha LLM Factory **. The purpose of this feature is to provide a centralized, file-based system for defining and instantiating pre-configured `crewai.LLM` objects. This allows developers to manage all model configurations in one place, ensuring consistency and simplifying the process of using different LLMs for various tasks.

-----

### 2. Core Problem Statement

In applications utilizing multiple Large Language Models, configurations are often scattered throughout the codebase. This leads to several issues:

-   **Code Duplication:** The same LLM instantiation logic with specific parameters (temperature, API endpoints, etc.) is repeated in multiple places.
-   **Inconsistency:** Different parts of an application might use slightly different parameters for the same conceptual task (e.g., creative writing vs. evaluation), leading to unpredictable behavior.
-   **High Maintenance Cost:** Switching a model, updating an API endpoint, or tweaking a parameter requires finding and changing every instance in the code.
-   **Difficult Experimentation:** A/B testing different models or parameters for a specific task is cumbersome.

> **Amsha LLM Hub** solves these problems by abstracting LLM configuration into a single YAML file, providing a simple factory for creating consistently configured LLM instances on demand.

-----

### 3. Goals and Scope

#### 3.1. Goals

-   To centralize all LLM definitions and parameters in a single configuration file.
-   To provide a simple interface for creating `crewai.LLM` instances for different predefined use cases.
-   To enforce consistent parameter usage for specific types of tasks.
-   To allow for easy switching between different models without code changes.

#### 3.2. Scope

The scope is limited to parsing a YAML configuration file and instantiating `crewai.LLM` objects based on its contents. It does not involve hosting models, proxying API requests, or managing API key security beyond reading them from the configuration file.

-----

### 4. Core Features (Functional Requirements)

#### 4.1. Configuration (`FR-LLM-CONF`)

-   **FR-LLM-CONF-01: YAML Configuration Source:** The system must load all LLM configurations from a single, user-provided YAML file.
-   **FR-LLM-CONF-02: Use Case Grouping:** The YAML structure must support grouping model definitions under distinct 'use cases' (e.g., 'creative', 'evaluation').
-   **FR-LLM-CONF-03: Parameter Set Grouping:** The YAML structure must support grouping sets of LLM parameters (e.g., `temperature`, `top_p`) under the same 'use cases'.
-   **FR-LLM-CONF-04: Multiple Model Definitions:** Within each use case, the system must support the definition of multiple, uniquely keyed models (e.g., 'phi', 'llama').
-   **FR-LLM-CONF-05: Default Model Specification:** Each use case group in the YAML file must specify a 'default' model key, which will be used if no specific model is requested.

#### 4.2. Instantiation (`FR-LLM-INST`)

-   **FR-LLM-INST-01: Use Case-Based Creation:** The library must provide a function to create a `crewai.LLM` instance for a given use case (e.g., `create_creative_instance()`).
-   **FR-LLM-INST-02: Specific Model Selection:** The creation function must allow the user to optionally provide a key to select a specific model from the use case's list. If no key is provided, the default model for that use case must be used.
-   **FR-LLM-INST-03: Parameter Application:** When creating an LLM instance, the system must apply the parameter set corresponding to the requested use case.

#### 4.3. Telemetry Control (`FR-LLM-TELE`)

-   **FR-LLM-TELE-01: Disable Telemetry:** The library must provide a mechanism to programmatically disable the telemetry features of the `crewai` library.

-----


