# Functional Documentation: Amsha Crew Forge

| |                |
| :--- |:---------------|
| **Version:** | 1.0            |
| **Date:** | August 2, 2025 |
| **Author:** | Nikhil         |
| **Status:** | Draft          |

-----

### 1. Introduction

This document outlines the functional requirements for **Amsha Crew Forge**. This project is a specialized utility library designed to provide a "Configuration as Code" workflow for managing CrewAI components (Agents, Tasks, and Crews). The primary goal of the Forge is to automate the synchronization between a version-controlled file system and a persistent database, enabling robust, consistent, and traceable management of AI agent configurations.

The intended audience for this document includes project stakeholders, software architects, and the developers who will use this library to build their applications.

-----

### 2. Core Problem Statement

As CrewAI applications scale, managing the definitions of numerous agents, tasks, and their relationships becomes increasingly complex. Storing these configurations directly in a database or in scattered files leads to several challenges:

-   **Configuration Drift:** It is difficult to keep configurations consistent across different environments (development, staging, production).
-   **Lack of Versioning:** There is no straightforward way to version-control changes to an agent's persona, a task's description, or the composition of a crew. Reverting to a previous setup is manual and error-prone.
-   **High Maintenance Overhead:** Adding or modifying agent definitions requires manual database operations or custom scripts, which slows down the development lifecycle.
-   **Poor Traceability:** It is hard to track who changed what configuration and when, leading to a lack of accountability and difficult debugging.

> **Amsha Crew Forge** aims to solve these problems by establishing the file system as the single source of truth, enabling developers to manage their CrewAI configurations with the same rigor and tooling (e.g., Git) as their application code.

-----

### 3. Goals and Scope

#### 3.1. Goals

-   To provide a fully automated, one-way synchronization from a local directory to a database.
-   To enable developers to manage CrewAI configurations using a "Configuration as Code" paradigm.
-   To ensure consistency and eliminate configuration drift across all environments.
-   To provide clear traceability and versioning for all configuration entities via Git.
-   To simplify the process of creating, updating, and deleting CrewAI configurations.

#### 3.2. Scope

The scope of **Amsha Crew Forge** is strictly limited to the management of configuration *definitions*. The core functionality involves reading a structured directory of YAML files and synchronizing their state with a persistent database.

-----

### 4. Core Features (Functional Requirements)

The library will expose its functionality through a single, cohesive service interface, here represented as `IConfigSyncService`.

#### 4.1. Directory Structure and Naming (`FR-STRUCT`)

-   **FR-STRUCT-01: Use Case Directory:** The system must operate on a root directory containing one or more subdirectories. Each subdirectory represents a unique **'use case'**.
-   **FR-STRUCT-02: Component Subdirectories:** Each 'use case' directory must contain exactly two subdirectories named `agents` and `tasks`.
-   **FR-STRUCT-03: Agent File Convention:** Agent definitions must be contained in YAML files located within the `agents` subdirectory. All agent YAML filenames must end with the suffix `_agent.yaml`.
-   **FR-STRUCT-04: Task File Convention:** Task definitions must be contained in YAML files located within the `tasks` subdirectory. All task YAML filenames must end with the suffix `_task.yaml`.

#### 4.2. Synchronization Logic (`FR-SYNC`)

-   **FR-SYNC-01: Entity Creation:** The system must create a new entity (agent or task) in persistent storage if a corresponding YAML file exists in the source directory but no matching entity (keyed by its name/role and use case) exists in storage.
-   **FR-SYNC-02: Entity Update:** The system must update an existing entity in storage if the content of its corresponding YAML file has been modified.
-   **FR-SYNC-03: Unchanged Entity Handling:** The system must not perform any write operations for an entity if its corresponding YAML file exists and its content is unchanged.
-   **FR-SYNC-04: Entity Pruning:** The system must delete an entity from persistent storage if its corresponding YAML file is removed from the source directory.

#### 4.3. Crew Assembly (`FR-CREW`)

-   **FR-CREW-01: Automatic Crew Creation:** The system must automatically create and maintain a single 'Crew' configuration in persistent storage for each 'use case' directory.
-   **FR-CREW-02: Crew Composition:** The 'Crew' configuration must be linked to the complete set of agent and task entities defined within its corresponding 'use case' directory.

#### 4.4. Operational Constraints (`FR-OP`)

-   **FR-OP-01: Stateless Operation:** The library must be stateless and must not persist any data or state between invocations.
-   **FR-OP-02: No Embedded Secrets:** The library's source code must not contain any hardcoded secrets, credentials, or environment-specific configurations.
-   **FR-OP-03: Externalized Configuration:** The library must receive all required configuration, such as database credentials and file paths, from the consuming application at runtime.

#### 4.5. Extensibility (`FR-EXT`)

-   **FR-EXT-01: Pluggable Storage Backend:** The library must be architected to support various persistent storage providers (e.g., different NoSQL databases, in-memory stores for testing) through a common interface. The core services of the library must not be directly coupled to any single database technology, allowing the consuming application to choose and provide a specific implementation.

-----

### 5. User Roles and Personas

-   **AI/Application Developer:** The primary user of the library. This developer is building applications using CrewAI and will use the Forge to manage agent/task definitions within their project's codebase.

-----

### 6. Assumptions and Dependencies

-   The consuming application is responsible for providing all necessary runtime configurations (e.g., database connection string, root path for domain files).
-   The environment where the library is executed has network access to the target database.
-   All YAML files defining agents and tasks are well-formed and contain the required fields.

-----

### 7. Out of Scope

-   **Providing Infrastructure:** The library will not provide a database instance or any other infrastructure component. It only provides the tools to connect to them.
-   **Crew Execution:** The library is exclusively for managing configuration *definitions*. It is not responsible for instantiating or executing CrewAI processes.
-   **User Interface (UI):** The library is a backend utility and does not include any UI components.

-----