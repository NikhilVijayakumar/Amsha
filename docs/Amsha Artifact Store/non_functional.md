# Non-Functional Requirements: Amsha Artifact Store

| |                |
| :--- |:---------------|
| **Version:** | 1.0            |
| **Date:** | August 2, 2025 |
| **Author:** | Nikhil         |
| **Status:** | Draft          |

-----

### 1. Introduction

This document defines the non-functional requirements (NFRs) for the **Amsha Artifact Store**. It specifies the quality attributes and operational standards for the library's caching functionality, complementing the functional requirements by defining *how well* the cache should perform.

-----

### 2. Non-Functional Requirements

#### 2.1 Performance

-   **NFR-PERF-01: Low Overhead:** The process of checking the cache (e.g., hashing a file and looking up the hash in a manifest) must be significantly faster than the operation it is caching. The target for a single cache check is **under 50 milliseconds**.
-   **NFR-PERF-02: Scalability:** The system must efficiently manage a cache manifest containing thousands of entries without a noticeable degradation in lookup performance.

-----

#### 2.2 Reliability

-   **NFR-REL-01: Resilience to Corruption:** The cache manager must be resilient to data corruption. If a cache entry or the manifest file is malformed or unreadable, it shall be treated as a **cache miss**, and the original operation will be re-run. The system must not crash due to a corrupted cache.
-   **NFR-REL-02: Hashing Integrity:** The content hashing algorithm used must be robust enough to reliably detect any changes to a source file.

-----

#### 2.3 Usability (Developer Experience)

-   **NFR-USE-01: Simple Configuration:** The on/off configuration for the cache must be a simple boolean flag that is easy for the developer to set when invoking a service like `Amsha Crew Forge`.
-   **NFR-USE-02: Transparent Operation:** For developers using other Amsha tools (like the Linter), the caching mechanism should operate transparently in the background without requiring any special setup.

-----

#### 2.4 Security

-   **NFR-SEC-01: Non-Sensitive Data:** The cache shall only store the non-sensitive results of operations. It must not be used to store secrets, credentials, or any personally identifiable information (PII).
-   **NFR-SEC-02: Standard File Permissions:** Files created in the `.amsha` cache directory should use standard, default user file permissions.

-----

#### 2.5 Maintainability

-   **NFR-MAIN-01: Encapsulation:** All caching logic (hashing, file I/O, manifest management) must be fully encapsulated within the `Amsha Artifact Store` module. Other modules should not contain any caching logic themselves.
-   **NFR-MAIN-02: Testability:** The cache manager must be fully testable in isolation. Unit tests should be able to simulate cache hits, misses, and corruption scenarios by operating on a temporary directory, without any dependency on other Amsha modules.

-----

#### 2.6 Compatibility

-   **NFR-COMP-01: Python Version Support:** The library must be compatible with **Python 3.12** and all subsequent minor versions.
-   **NFR-COMP-02: Platform Independence:** All file system operations, including path manipulation and hashing, must be platform-agnostic and function correctly on Windows, macOS, and Linux.