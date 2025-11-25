# Non-Functional Requirements: Amsha LLM Factory

| |                |
| :--- |:---------------|
| **Version:** | 1.0            |
| **Date:** | August 2, 2025 |
| **Author:** | Nikhil         |
| **Status:** | Draft          |

-----

### 1. Introduction

This document defines the non-functional requirements (NFRs) for the **Amsha LLM Factory **. It specifies the quality attributes and standards the library must adhere to when performing its functions.

-----

### 2. Non-Functional Requirements

#### 2.1 Performance

-   **NFR-PERF-01: Instantiation Latency:** The time taken to parse the YAML file and create an `LLM` object should be negligible (target < 50 milliseconds), as this is a one-time setup cost.
-   **NFR-PERF-02: Memory Footprint:** The library should have a minimal memory footprint, holding only the parsed configuration in memory.

#### 2.2 Reliability

-   **NFR-REL-01: Graceful Error Handling:** The library must handle errors gracefully, such as a missing configuration file, malformed YAML, or missing keys (e.g., a requested use case or model key not found in the file).
-   **NFR-REL-02: Clear Error Messages:** In case of a configuration error, the system must raise an exception with a clear, informative message indicating the nature of the problem (e.g., "Use case 'creative' not found in config file.").

#### 2.3 Usability (Developer Experience)

-   **NFR-USE-01: API Simplicity:** The public API for creating LLM instances must be simple and intuitive (e.g., `llm_hub.create_creative_instance(model_key='llama')`).
-   **NFR-USE-02: Clear Documentation:** The library must be documented with clear examples of the required YAML structure.

#### 2.4 Security

-   **NFR-SEC-01: No Secret Storage:** The library must not store, log, or otherwise persist any sensitive information (like API keys) it reads from the configuration file. All secrets are handled in-memory only for the duration of object creation.

#### 2.5 Maintainability

-   **NFR-MAIN-01: Code Readability:** The source code must be clean, well-structured, and adhere to PEP 8 conventions.
-   **NFR-MAIN-02: Test Coverage:** The core logic for parsing the configuration and creating LLM instances must have a high level of automated unit test coverage (target > 80%).

#### 2.6 Compatibility

-   **NFR-COMP-01: Python Version Support:** The library must be compatible with **Python 3.12** and all subsequent minor versions.

-----
