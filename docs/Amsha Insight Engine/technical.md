# Technical Requirements: Amsha Insight Engine

| | |
| :--- | :--- |
| **Version:** | 1.0 |
| **Date:** | August 2, 2025 |
| **Author:** | Nikhil / Gemini |
| **Status:** | Draft |

-----

### 1. Introduction

This document provides the technical specification for developers building or maintaining the **Amsha Insight Engine**. It outlines the technology stack, software architecture, data contracts, and testing strategy chosen to fulfill the engine's functional and non-functional requirements.

-----

### 2. Technology Stack

-   **TR-TECH-01: Language:** The library will be developed in **Python 3.12** or higher, as per `NFR-COMP-01`.
-   **TR-TECH-02: Core Dependencies:**
    * **Pydantic:** To be used for defining the strict data contracts for the input and output reports (e.g., `LinterReport`, `InsightReport`).
    * **CrewAI:** As a peer dependency, required for type hinting the `Crew` object that the client application must provide.

-----

### 3. Architectural Design

The `Amsha Insight Engine` is designed as a lightweight, stateless orchestrator service. Its sole purpose is to act as a bridge between structured validation data and a client-provided `Crew` object.

#### 3.1. Core Components

-   **`AmshaInsightEngine` (Service Class):** A single class containing the core orchestration logic. It will be stateless, meaning it will not hold data in its constructor. Its primary public method will be `generate_summary()`.
-   **Input Data Models (Pydantic):** A collection of Pydantic models that define the schema for the raw reports the engine can consume (e.g., the `LinterReport` model from the linter). These models form the public data contract for inputs.
-   **Output Data Model (Pydantic):** A simple Pydantic model (e.g., `InsightReport`) will define the structure of the final output, containing metadata and the generated summary string.

#### 3.2. Design Patterns

-   **TR-ARCH-01: Stateless Service:** The engine is implemented as a stateless service. All required data (input reports) and dependencies (the reporting crew) are passed directly as arguments to its execution method, not stored in the instance.
-   **TR-ARCH-02: Dependency Inversion:** The design adheres to the principle of dependency inversion. The engine's execution method depends on an abstract `Crew` type from the `crewai` library, not on any specific implementation of a reporting crew. The client "inverts the control" by providing the concrete `Crew` implementation at runtime.

-----

### 4. Data Flow

The technical data flow for a report generation operation is as follows:
1.  The client application gathers one or more Pydantic report objects (e.g., `LinterReport`).
2.  The client instantiates its own custom `Crew` object for reporting.
3.  The client instantiates the `AmshaInsightEngine`.
4.  The client calls the `engine.generate_summary()` method, passing the list of report objects and the crew instance.
5.  Inside the method, the engine serializes the input Pydantic report objects into a single JSON string.
6.  This JSON string is passed as the primary input to the `reporting_crew.kickoff()` method.
7.  The engine awaits the result from the crew's execution, which is expected to be the final Markdown summary string.
8.  This result string is wrapped in the `InsightReport` Pydantic model and returned to the client.

-----

### 5. Key Data Models & Contracts

-   **TR-DATA-01: Input Contracts:** The library will define and export the Pydantic models representing the structure of the raw reports it can process. This provides a clear, machine-readable schema that client applications can use to structure their data.
-   **TR-DATA-02: Output Contract:** A simple Pydantic model, `InsightReport`, will define the structure of the final output. It will contain fields like `metadata` and the final generated `summary: str`.

-----

### 6. Error Handling

-   **TR-ERR-01: Execution Error Handling:** The call to `reporting_crew.kickoff()` within the `generate_summary` method will be wrapped in a `try...except` block. Any exception raised by the `crewai` library during the crew's execution will be caught. The original exception will be wrapped in a custom, more specific exception (e.g., `ReportGenerationError`) and re-raised to provide clear context to the client, fulfilling `NFR-REL-01`.

-----

### 7. Testing Strategy

-   **TR-TEST-01: Unit Tests:** The `AmshaInsightEngine` service will be unit tested using `pytest`. The primary focus will be on verifying the orchestration logic.
-   **TR-TEST-02: Mocking Strategy:** To test the `generate_summary` method in isolation, a mock `Crew` object will be created using `unittest.mock`. Tests will:
    * Verify that the engine correctly serializes its input data models into the expected JSON string.
    * Verify that the engine calls the `kickoff()` method on the mock crew with the correct inputs.
    * Simulate the mock crew returning a result and verify that the engine correctly wraps it in the `InsightReport` object.
    * Simulate the mock crew raising an exception and verify that the engine's error handling logic is triggered correctly.
This strategy ensures the engine can be tested without making any actual, non-deterministic LLM calls, fulfilling `NFR-MAIN-02`.