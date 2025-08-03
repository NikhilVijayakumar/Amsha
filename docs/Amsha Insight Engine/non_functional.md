# Non-Functional Requirements: Amsha Insight Engine

| |                |
| :--- |:---------------|
| **Version:** | 1.0            |
| **Date:** | August 2, 2025 |
| **Author:** | Nikhil         |
| **Status:** | Draft          |

-----

### 1. Introduction

This document defines the non-functional requirements (NFRs) for the **Amsha Insight Engine**. It specifies the quality attributes, performance expectations, and operational constraints that the library must adhere to. This document complements the functional requirements by defining the standards for the engine's operation.

-----

### 2. Non-Functional Requirements

#### 2.1 Performance

-   **NFR-PERF-01: Execution Overhead:** The internal processing overhead of the `Amsha Insight Engine` (the logic for preparing inputs and invoking the client's crew) shall be negligible (target < 1 second).
-   **NFR-PERF-02: Dependency on Client Crew:** The overall execution time and performance of the report generation process are primarily dependent on the efficiency of the client-provided reporting crew and its configured LLM. These factors are outside the performance scope of this library.
-   **NFR-PERF-03: Scalability:** The library must be capable of handling large, structured input reports (e.g., aggregating results from hundreds of individual tests) without excessive memory consumption relative to the input data size.

-----

#### 2.2 Reliability

-   **NFR-REL-01: Graceful Failure Handling:** The library must gracefully handle exceptions or failures that occur during the execution of the client-provided reporting crew. It must not crash but should instead capture and report the error clearly to the client application.
-   **NFR-REL-02: Data Immutability:** The library must treat all input report data as immutable. It shall not modify the source data in any way during its operation.

-----

#### 2.3 Usability (Developer Experience)

-   **NFR-USE-01: API Simplicity:** The public API for invoking the Insight Engine must be minimal and intuitive, requiring the developer to simply provide the input data and their instantiated reporting crew object.
-   **NFR-USE-02: Clear Data Contracts:** The library must provide clear and well-documented data contracts (via Pydantic models) for the expected format of the input reports. This ensures developers can easily structure their validation data for consumption by the engine.

-----

#### 2.4 Security

-   **NFR-SEC-01: No Secret Handling:** The `Amsha Insight Engine` library must not handle, store, or require direct access to any secrets, such as LLM API keys. The responsibility for securely configuring the client-provided reporting crew lies entirely with the client application.
-   **NFR-SEC-02: Dependency Security:** The library must only depend on well-maintained packages from trusted public repositories (e.g., PyPI) and should be periodically scanned for known vulnerabilities.

-----

#### 2.5 Maintainability

-   **NFR-MAIN-01: Modularity:** The core orchestration logic must be self-contained and fully decoupled from any specific LLM, prompt structure, or reporting content.
-   **NFR-MAIN-02: Testability:** The Insight Engine's orchestration logic must be highly testable in isolation. It must be possible to unit test the engine by injecting a mock `Crew` object to simulate success, failure, and exception scenarios without making actual LLM calls.
-   **NFR-MAIN-03: Code Readability:** The source code must adhere to standard Python coding conventions (PEP 8) to ensure it is clean and easy for others to understand and contribute to.

-----

#### 2.6 Compatibility

-   **NFR-COMP-01: Python Version Support:** The library must be compatible with **Python 3.12** and all subsequent minor versions.
-   **NFR-COMP-02: Platform Independence:** The library must be operating system agnostic and function correctly on Windows, macOS, and Linux environments.