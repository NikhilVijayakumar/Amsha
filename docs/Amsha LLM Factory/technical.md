# Technical Requirements: Amsha LLM Factory

| |                |
| :--- |:---------------|
| **Version:** | 1.0            |
| **Date:** | August 2, 2025 |
| **Author:** | Nikhil         |
| **Status:** | Draft          |

-----

### 1. Introduction

This document provides the technical specification for the **Amsha LLM Factory**. It outlines the technology stack, architectural design, and data models chosen to fulfill the specified requirements.

-----

### 2. Technology Stack

-   **TR-TECH-01: Language:** **Python 3.12** or higher.
-   **TR-TECH-02: Core Dependencies:**
    * **Pydantic:** To be used for modeling the YAML structure, providing robust validation and clear data contracts.
    * **PyYAML:** To be used for safely parsing the YAML configuration file.
    * **CrewAI:** As a peer dependency, required for the `LLM` object that the factory produces.

-----

### 3. Architectural Design

#### 3.1. Design Patterns

-   **TR-ARCH-01: Factory Pattern:** The core of the feature will be a class (`LLMHub`) that implements the Factory pattern. Its primary responsibility is to abstract the complex creation logic of `crewai.LLM` objects, providing a simple interface to the client.

#### 3.2. Core Components

-   **`LLMHub` (or `LLMConfig`):** The main public-facing class. It will be initialized with the path to the YAML configuration file. It will expose methods like `create_creative_instance()` and `create_evaluation_instance()`.
-   **Pydantic Models:** A set of Pydantic models will be created to strictly define the expected structure of the YAML file, including nested models for `llm`, `models`, and `llm_parameters`.
-   **`YamlUtils` (Optional):** A helper class can be used to encapsulate the logic of loading and parsing the YAML file into the Pydantic models, keeping the `LLMHub` class focused on the instantiation logic.

-----

### 4. Data Models

-   **TR-DATA-01: Configuration Schema with Pydantic:** The entire `llm_config.yaml` structure will be mapped to Pydantic models. This provides automatic validation of data types, required fields, and structure.
    * `ModelDefinition(BaseModel)`: To model a single LLM entry (`base_url`, `model`, `api_key`).
    * `UseCaseModels(BaseModel)`: To model a group like `creative`, containing a `default` string and a `models: dict[str, ModelDefinition]`.
    * `UseCaseParameters(BaseModel)`: To model a parameter set like `creative` under `llm_parameters`.
    * `RootConfig(BaseModel)`: The top-level model containing `llm: dict[str, UseCaseModels]` and `llm_parameters: dict[str, UseCaseParameters]`.

-----

### 5. Error Handling

-   **TR-ERR-01: Exception Strategy:**
    * `FileNotFoundError` will be raised if the YAML path provided is invalid.
    * `pydantic.ValidationError` will be raised if the YAML file does not conform to the defined Pydantic model structure.
    * `KeyError` or `ValueError` will be raised if a client requests a use case or model key that does not exist in the loaded configuration.

-----

### 6. Testing Strategy

-   **TR-TEST-01: Unit Tests:** Unit tests written with `pytest` will validate all functionalities. A sample `llm_config.yaml` will be included in the test assets.
-   **TR-TEST-02: Test Cases:**
    * Verify successful loading of a valid YAML file.
    * Verify correct instantiation of a default model for a use case.
    * Verify correct instantiation of a specifically requested model.
    * Verify that the correct parameters are applied to the created `LLM` object.
    * Verify that `ValidationError` is raised for a malformed YAML file.
    * Verify that `KeyError` is raised for a non-existent use case or model.
    * Verify that the telemetry disabling function works as expected.

-----