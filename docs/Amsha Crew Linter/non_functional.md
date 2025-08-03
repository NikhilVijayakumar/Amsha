# Non-Functional Requirements: Amsha Crew Linter

| |                |
| :--- |:---------------|
| **Version:** | 1.0            |
| **Date:** | August 2, 2025 |
| **Author:** | Nikhil         |
| **Status:** | Draft          |

-----

### 1. Introduction

This document defines the non-functional requirements (NFRs) for the **Amsha Crew Linter**. It specifies the quality attributes, performance standards, and operational constraints the Linter must adhere to when performing its static analysis functions. This document complements the functional requirements by defining *how well* the system should operate.

-----

### 2. Non-Functional Requirements

#### 2.1 Performance

-   **NFR-PERF-01: Execution Time:** The Linter must be fast enough to be integrated into a standard CI/CD pipeline without causing significant delays.
    -   A linting run using baseline guardrails (e.g., keyword and similarity checks) on a typical use case should complete in **under 5 seconds**.
    -   A linting run involving computationally intensive guardrails (e.g., `BERTopicGuardrail`) should complete in a reasonable timeframe (target **< 60 seconds**).
-   **NFR-PERF-02: Resource Consumption:** The library must be resource-efficient. Memory usage should be managed effectively, especially when using large embedding models, to ensure the Linter can run on standard developer machines and typical CI/CD runners.

-----

#### 2.2 Reliability

-   **NFR-REL-01: Fault Tolerance:** The Linter must be resilient to failures in individual guardrails. An error or exception within one guardrail must not terminate the entire linting process; other configured guardrails should continue to execute.
-   **NFR-REL-02: Reporting Accuracy:** The final report must accurately reflect the outcome of all executed guardrails. Any guardrail that failed to run due to an internal error must be clearly marked as such in the report.

-----

#### 2.3 Usability (Developer Experience)

-   **NFR-USE-01: API Simplicity:** The public API for initializing the Linter and executing a validation run must be simple and intuitive, enabling a developer to get started with minimal boilerplate code.
-   **NFR-USE-02: Report Clarity:** The generated report must be easy to parse both programmatically (e.g., a standard JSON output) and by a human (e.g., via a printable summary method), as per `FR-LINT-RP-01`.
-   **NFR-USE-03: Extensibility:** The process for creating and integrating a new custom guardrail must be straightforward and clearly documented, centered around the `IGuardrail` interface.

-----

#### 2.4 Security

-   **NFR-SEC-01: No Side Effects:** The Linter must function as a pure analysis tool. It shall not modify any of the input files or objects. Its only output shall be the in-memory report object.
-   **NFR-SEC-02: Dependency Security:** The library must only depend on well-maintained packages from trusted public repositories (e.g., PyPI) and should be periodically scanned for known vulnerabilities.

-----

#### 2.5 Maintainability

-   **NFR-MAIN-01: Modularity:** The Linter's orchestration logic must remain completely separate from the individual guardrail implementations, enforcing the pluggable architecture defined in the functional requirements.
-   **NFR-MAIN-02: Testability:** The core Linter service must be highly testable in isolation. It should be possible to unit test its orchestration logic using mock or fake guardrail objects, without any dependency on actual NLP models.
-   **NFR-MAIN-03: Code Readability:** The source code must be clean, well-structured, and adhere to standard Python coding conventions (PEP 8).

-----

#### 2.6 Compatibility

-   **NFR-COMP-01: Python Version Support:** The library must be compatible with **Python 3.12** and all subsequent minor versions.
-   **NFR-COMP-02: Platform Independence:** The library must be operating system agnostic and function correctly on Windows, macOS, and Linux environments.