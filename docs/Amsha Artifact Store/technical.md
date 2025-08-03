# Technical Requirements: Amsha Artifact Store

| |                |
| :--- |:---------------|
| **Version:** | 1.0            |
| **Date:** | August 2, 2025 |
| **Author:** | Nikhil         |
| **Status:** | Draft          |

-----

### 1\. Introduction

This document provides the technical specification for the **Amsha Artifact Store**. It is intended for software developers and outlines the technology, architecture, and implementation details for the library's file-system-based caching mechanism, designed to fulfill the specified functional and non-functional requirements.

-----

### 2\. Technology Stack

  - **TR-TECH-01: Language:** The library will be developed in **Python 3.12** or higher.
  - **TR-TECH-02: Core Dependencies:** The implementation will rely primarily on the Python standard library:
      * **`hashlib`:** For generating SHA256 hashes of input content to create cache keys.
      * **`os` / `pathlib`:** For all file system interactions (creating directories, reading/writing files).
      * **`json`:** For serializing and deserializing the cache manifest and cached objects.
  - **TR-TECH-03: Testing Framework:** **pytest** will be used for all unit tests, utilizing fixtures like `tmp_path` for file system operations.

-----

### 3\. Architectural Design

The `Amsha Artifact Store` is designed as a self-contained, stateless utility service that encapsulates all caching logic.

#### 3.1. High-Level Architecture

The component will operate on a designated directory within the client project's file system (defaulting to `.amsha/cache/`). Its architecture consists of a primary `CacheManager` class that interacts with a central `manifest.json` file and a directory of cached result files. Other Amsha modules (like the Linter) will interact with this `CacheManager` to handle cache operations, but they will remain completely decoupled from the file system implementation details.

#### 3.2. Core Components

  - **`CacheManager`:** A central class that provides the public API for all cache operations (e.g., `get`, `set`, `check`). It will be initialized with the root path of the cache directory.
  - **`manifest.json`:** A JSON file located at the root of the cache directory. This file will serve as the cache index, storing a dictionary that maps content-based cache keys to metadata about the stored result, such as the path to the result file and a creation timestamp.

-----

### 4\. Cache Workflow and Data Flow

1.  A service (e.g., `AmshaCrewLinter`) needs to perform an expensive operation on some input data.
2.  It generates a unique **cache key** by creating a SHA256 hash of the input data's content.
3.  It calls the `cache_manager.get(cache_key)` method.
4.  The `CacheManager` reads its `manifest.json` file to look for the provided `cache_key`.
5.  **Cache Hit:** If the key exists in the manifest, the `CacheManager` reads the corresponding result file (e.g., `.amsha/cache/results/<cache_key>.json`), deserializes the content, and returns the data object.
6.  **Cache Miss:** If the key does not exist, the `CacheManager` returns `None`.
7.  The calling service, upon receiving `None`, executes the expensive operation to generate a new result.
8.  The service then calls `cache_manager.set(cache_key, new_result)`.
9.  The `CacheManager` serializes the `new_result` object to JSON, saves it to a file in the cache results directory, and updates the `manifest.json` with the new key and file path.

-----

### 5\. Key Class and Data Structures

  - **TR-DATA-01: `CacheManager` Class:** The class will expose a simple interface:
      * `__init__(self, cache_root_path: str, is_enabled: bool = True)`: Initializes the manager with the path and the on/off switch.
      * `get(self, key: str) -> Any | None`: Retrieves an item from the cache.
      * `set(self, key: str, value: Any) -> None`: Adds an item to the cache.
  - **TR-DATA-02: `manifest.json` Structure:** The manifest will be a JSON object with the following structure:
    ```json
    {
      "sha256_hash_of_input_A": {
        "cache_filepath": "results/sha256_hash_of_input_A.json",
        "created_at_utc": "2025-08-02T17:00:00Z"
      },
      "sha256_hash_of_input_B": { ... }
    }
    ```

-----

### 6\. Error Handling

  - **TR-ERR-01: File I/O and Deserialization Errors:** All file system read/write operations and JSON parsing will be wrapped in `try...except` blocks to handle `IOError`, `PermissionError`, and `json.JSONDecodeError`. In the event of any such error, the operation will fail silently, and the system will proceed as if it were a **cache miss**, ensuring fulfillment of `NFR-REL-01`.

-----

### 7\. Testing Strategy

  - **TR-TEST-01: Unit Tests:** The `CacheManager` will be unit tested using `pytest`. A temporary directory provided by `pytest`'s `tmp_path` fixture will be used as the cache root to avoid side effects.
  - **TR-TEST-02: Test Scenarios:** Tests will cover all core scenarios:
      * A successful cache `set` followed by a `get` (cache hit).
      * A `get` for a non-existent key (cache miss).
      * The system's behavior when the `manifest.json` file is missing or corrupted.
      * The system's behavior when a cached result file is missing or corrupted.
      * Verification that no operations are performed if the cache is disabled via the `is_enabled` flag.