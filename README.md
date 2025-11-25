# Amsha

**Version:** 1.5.3  
**Description:** Common configuration and CrewAI helper library for building AI agent applications

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Core Components](#core-components)
4. [Data Flow](#data-flow)
5. [Common Library Purpose](#common-library-purpose)
6. [Installation & Setup](#installation--setup)
7. [Technology Stack](#technology-stack)

---

## Overview

Amsha is a comprehensive Python library that provides reusable components and utilities for building AI agent applications powered by CrewAI. It abstracts away common boilerplate code and provides a structured approach to:

- **Building and orchestrating CrewAI agents** with database or file-based configuration
- **Validating AI outputs** using NLP-based guardrails and topic modeling
- **Managing LLM instances** with centralized configuration
- **Creating FastAPI services** for AI agent applications
- **Tracking data versions** using DVC with S3/MinIO
- **Processing and evaluating outputs** from AI agents

The library follows clean architecture principles with clear separation between domain models, repositories, services, and orchestration layers.

---

## Architecture

Amsha is organized into several major components within `src/nikhil/amsha/`:

```
src/nikhil/amsha/
├── toolkit/              # Main toolkit with specialized modules
│   ├── crew_forge/       # CrewAI configuration & orchestration
│   ├── crew_linter/      # AI output validation & guardrails
│   ├── llm_factory/      # LLM initialization & management
│   ├── api/              # FastAPI application factory
│   ├── mlops/            # DVC data versioning
│   └── output_process/   # Output validation & evaluation
├── crewai/               # CrewAI custom tools
├── utils/                # Common utilities (JSON, YAML, UTF-8)
├── nlp_eval_utils/       # NLP evaluation guardrails
├── preprocessing/        # Text preprocessing utilities
└── exception/            # Custom exceptions
```

### Architecture Principles

1. **Dependency Injection**: Uses `dependency-injector` for managing service dependencies
2. **Repository Pattern**: Separates data access logic from business logic
3. **Service Layer**: Encapsulates business logic in reusable services
4. **Clean Architecture**: Domain models are independent of infrastructure
5. **Protocol-Oriented Design**: Uses Python protocols for interface definitions

---

## Core Components

### 1. Crew Forge (`toolkit/crew_forge/`)

**Purpose:** Manages CrewAI agent and task configurations, providing both database-backed and file-backed approaches to building AI crews.

**Key Submodules:**

- **`domain/`**: Data models for agents, tasks, crews, and repositories
  - `models/`: Pydantic models (`AgentData`, `TaskData`, `CrewData`, `CrewConfigData`)
  - `enum/`: Repository backend types (MongoDB, File)

- **`repo/`**: Repository implementations for persistent storage
  - `interfaces/`: Repository interfaces (`IAgentRepository`, `ITaskRepository`, `ICrewConfigRepository`)
  - `adapters/mongo/`: MongoDB implementations of repositories

- **`service/`**: Business logic for building crews
  - `AtomicDbBuilderService`: Builds crews from database-stored configurations
  - `AtomicYamlBuilder`: Builds crews from YAML file configurations
  - `CrewBuilderService`: Core crew building logic

- **`orchestrator/`**: **High-level orchestration of crew execution** - This is the core abstraction that allows users to run CrewAI configurations in two different modes while maintaining a consistent interface.

  **Key Benefits:**
  - **Dual Orchestration Modes**: Choose between database-backed or file-based configuration storage
  - **Unified Interface**: Same code pattern works for both DB and file modes
  - **Reduces CrewAI Dependency**: Applications depend on Amsha's orchestrator, not directly on CrewAI
  - **Integrated LLM Management**: Automatically builds and configures LLMs via LLM Factory
  - **Input Handling**: Manages knowledge sources, input files, and other inputs consistently
  - **Common Patterns**: Provides standardized way of orchestrating crews across all projects

  **Submodules:**
  
  - `db/`: **Database-backed crew orchestration** - Store agent/task configurations in MongoDB
    - `AmshaCrewDBApplication`: Base application class for database-backed crews
      - Loads job, app, and LLM configurations from YAML
      - Initializes LLM via integrated LLM Factory
      - Manages input preparation from files or direct config
      - Provides `clean_json()` for output post-processing
    - `AtomicCrewDBManager`: Manages crew lifecycle with database repositories
    - `DbCrewOrchestrator`: Orchestrates crew execution by fetching configs from MongoDB
  
  - `file/`: **File-based crew orchestration** - Use YAML files for agent/task configurations
    - `AmshaCrewFileApplication`: Base application class for file-backed crews
      - Parses agents and tasks directly from YAML files
      - Initializes LLM via integrated LLM Factory
      - Manages input preparation from files or direct config
      - Provides `clean_json()` for output post-processing
    - `AtomicCrewFileManager`: Manages crew lifecycle with file system
    - `FileCrewOrchestrator`: Orchestrates crew execution by parsing YAML configs
  
  **Usage Pattern**: Users extend either `AmshaCrewDBApplication` or `AmshaCrewFileApplication` and call the orchestrator to execute crews. See `example/` directory for concrete examples of both approaches.

- **`seeding/`**: Database seeding utilities
  - `DatabaseSeeder`: Seeds MongoDB with agent/task configurations
  - `parser/`: Parses crew configurations from various formats

- **`sync/`**: Configuration synchronization between storage backends

- **`knowledge/`**: Knowledge source integrations (e.g., Docling for document processing)

- **`example/`**: Working examples demonstrating both orchestration modes
  - Database-backed crew examples with MongoDB
  - File-based crew examples with YAML configurations
  - Configuration sync examples
  - Complete end-to-end workflow demonstrations

### 2. Crew Linter (`toolkit/crew_linter/`)

**Purpose:** Validates AI-generated outputs using NLP techniques and topic modeling to ensure quality and relevance.

**Key Submodules:**

- **`domain/models/`**: Input/output models for linting operations
  - `BERTopicData`: BERTopic modeling data
  - `LDATopicData`: LDA topic modeling data
  - `SimilarityData`: Text similarity analysis data
  - `KeywordCoverageData`: Keyword coverage validation data
  - `NetworkXData`: Network graph analysis data

- **`guardrails/`**: Validation guardrails for AI outputs
  - `BERTopicGuardrail`: Validates topic alignment using BERTopic
  - `LDATopicGuardrail`: Validates topic alignment using LDA
  - `SimilarityGuardrail`: Checks semantic similarity
  - `KeywordCoverageGuardrail`: Ensures required keywords are present
  - `NetworkXGuardrail`: Analyzes relationship graphs

- **`analysis/topic_modelling/`**: Topic modeling implementations
  - `BaseTopicModeler`: Abstract base for topic modelers
  - `BERTopicModeler`: BERTopic implementation
  - `LDATopicModeler`: Latent Dirichlet Allocation implementation
  - `NMFTopicModeler`: Non-negative Matrix Factorization implementation

- **`preprocessing/`**: Text preprocessing for linting
  - `markdown/`: Markdown document processing
  - `preparation/`: Text preparation and vectorization

### 3. LLM Factory (`toolkit/llm_factory/`)

**Purpose:** Centralized LLM initialization and configuration management, supporting multiple LLM types and providers.

**Key Submodules:**

- **`domain/`**: LLM domain models
  - `LLMType`: Enum for LLM types (CREATIVE, EVALUATION)
  - `models`: LLM configuration models (`LLMBuildResult`)

- **`service/`**: LLM building services
  - `LLMBuilder`: Constructs LLM instances from configuration
    - `build_creative()`: Builds LLM for creative tasks
    - `build_evaluation()`: Builds LLM for evaluation tasks

- **`settings/`**: Configuration management
  - `LLMSettings`: Loads and manages LLM configuration from YAML

- **`dependency/`**: Dependency injection containers
  - `LLMContainer`: DI container for LLM services

- **`utils/`**: LLM utilities
  - `LLMUtils`: Helper functions (model name extraction, telemetry control)

### 4. API Factory (`toolkit/api/`)

**Purpose:** Provides factory functions to create FastAPI applications with pre-configured endpoints for AI agent services.

**Key Submodules:**

- **`factory/`**: API creation factories
  - `api_factory.py`: Creates FastAPI routers and apps
    - `create_bot_api()`: Creates router with utility and streaming endpoints
    - `create_fastapi_app()`: Creates complete FastAPI application

- **`protocol/`**: Protocol definitions for type safety
  - `BotManagerProtocol`: Interface for bot management
  - `TaskConfigProtocol`: Interface for task configuration

- **`streaming/`**: Streaming utilities
  - `sync_to_async`: Converts synchronous iterables to async

### 5. MLOps (`toolkit/mlops/`)

**Purpose:** Data versioning and tracking using DVC (Data Version Control) with S3/MinIO backend.

**Key Files:**

- `DVCSetup`: Automates DVC setup for S3/MinIO
  - Configures DVC remotes
  - Creates S3 buckets if needed
  - Handles data push/pull operations
  - Manages credentials

- `DVCDataTracker`: Tracks data changes and versions
  - Adds new data to DVC tracking
  - Commits changes to Git
  - Pushes data to remote storage

### 6. Output Process (`toolkit/output_process/`)

**Purpose:** Validates, evaluates, and optimizes outputs from AI agents.

**Key Submodules:**

- **`validation/`**: Output validation utilities
  - `CrewValidator`: Validates crew execution outputs
  - `JsonOutputValidator`: Validates JSON structure and content

- **`evaluation/`**: Output evaluation tools
  - `EvaluationProcessingTool`: Processes evaluation data
  - `EvaluationAggregateTool`: Aggregates evaluation results
  - `EvaluationReportTool`: Generates evaluation reports

- **`optimization/`**: Output optimization utilities
  - `JsonCleanerUtils`: Cleans and fixes malformed JSON using LLM

### 7. Common Utilities (`utils/`)

**Purpose:** Shared utility functions used across all components.

**Files:**

- `JsonUtils`: JSON file loading and saving utilities
- `YamlUtils`: YAML configuration loading utilities
- `Utf8Utils`: UTF-8 encoding utilities for text processing

### 8. CrewAI Tools (`crewai/tools/`)

**Purpose:** Custom tools for CrewAI agents.

**Files:**

- `duckduckgo_search_tool.py`: Web search capability for agents

### 9. NLP Eval Utils (`nlp_eval_utils/guardrail/`)

**Purpose:** Additional NLP-based guardrails for evaluation.

---

## Data Flow

### 1. CrewAI Application Flow (Database-Backed)

```
┌─────────────────────────────────────────────────────────────┐
│                    User Application                         │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ 1. Initialize with configs
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              AmshaCrewDBApplication                         │
│  • Loads YAML configs (job, app, llm)                       │
│  • Initializes LLM via LLMFactory                           │
│  • Creates AtomicCrewDBManager                              │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ 2. Initialize LLM
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    LLM Factory                              │
│  • LLMContainer (DI)                                        │
│  • LLMBuilder builds LLM from YAML config                   │
│  • Returns LLM instance (creative or evaluation)            │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ 3. Create Manager
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              AtomicCrewDBManager                            │
│  • Initializes MongoDB repositories                         │
│  • Creates DbCrewOrchestrator                               │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ 4. Execute crew
                     ▼
┌─────────────────────────────────────────────────────────────┐
│               DbCrewOrchestrator                            │
│  • Uses AtomicDbBuilderService                              │
│  • Fetches agents/tasks from MongoDB                        │
│  • Builds CrewAI Crew                                       │
│  • Executes crew with inputs                                │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ 5. Query repositories
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              MongoDB Repositories                           │
│  • AgentRepository: Fetch agent configs                     │
│  • TaskRepository: Fetch task configs                       │
│  • CrewConfigRepository: Fetch crew metadata                │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ 6. Returns data models
                     ▼
┌─────────────────────────────────────────────────────────────┐
│            AtomicDbBuilderService                           │
│  • add_agent(agent_id) → builds Agent                       │
│  • add_task(task_id, agent) → builds Task                   │
│  • build() → returns Crew                                   │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ 7. Execute and output
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                  CrewAI Execution                           │
│  • Runs agents and tasks                                    │
│  • Generates output files (JSON, Markdown, etc.)            │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ 8. Post-process outputs
                     ▼
┌─────────────────────────────────────────────────────────────┐
│               Output Processing                             │
│  • JsonCleanerUtils: Fix malformed JSON                     │
│  • CrewValidator: Validate outputs                          │
│  • Guardrails: Check quality (topic, similarity, keywords)  │
└─────────────────────────────────────────────────────────────┘
```

### 2. CrewAI Application Flow (File-Backed)

```
┌─────────────────────────────────────────────────────────────┐
│                    User Application                         │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ 1. Initialize with YAML file paths
                     ▼
┌─────────────────────────────────────────────────────────────┐
│             AmshaCrewFileApplication                        │
│  • Loads agent/task YAML files                              │
│  • Initializes LLM via LLMFactory                           │
│  • Creates AtomicCrewFileManager                            │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ 2. Parse YAML configs
                     ▼
┌─────────────────────────────────────────────────────────────┐
│             FileCrewOrchestrator                            │
│  • Uses AtomicYamlBuilder                                   │
│  • Parses agents/tasks from YAML                            │
│  • Builds CrewAI Crew                                       │
│  • Executes crew                                            │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ 3. Output processing
                     ▼
┌─────────────────────────────────────────────────────────────┐
│               Output Processing                             │
└─────────────────────────────────────────────────────────────┘
```

### 3. Output Validation Flow (Crew Linter)

```
┌─────────────────────────────────────────────────────────────┐
│                  AI Generated Output                        │
│              (Text, JSON, Markdown)                         │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ 1. Preprocess
                     ▼
┌─────────────────────────────────────────────────────────────┐
│               Text Preprocessing                            │
│  • MarkdownProcessor: Clean markdown                        │
│  • TextPreprocessor: Tokenize, clean, normalize             │
│  • Vectorizer: Convert to vectors                           │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ 2. Apply guardrails
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                   Guardrails                                │
│  • BERTopicGuardrail: Topic alignment check                 │
│  • LDATopicGuardrail: Topic distribution check              │
│  • SimilarityGuardrail: Semantic similarity check           │
│  • KeywordCoverageGuardrail: Required keyword check         │
│  • NetworkXGuardrail: Relationship graph validation         │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ 3. Return results
                     ▼
┌─────────────────────────────────────────────────────────────┐
│               Validation Results                            │
│  • Pass/Fail status                                         │
│  • Scores and metrics                                       │
│  • Detailed feedback                                        │
└─────────────────────────────────────────────────────────────┘
```

### 4. Data Versioning Flow (MLOps)

```
┌─────────────────────────────────────────────────────────────┐
│              Local Data Changes                             │
│         (Input data / Output data)                          │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ 1. Track changes
                     ▼
┌─────────────────────────────────────────────────────────────┐
│               DVCDataTracker                                │
│  • dvc add <data_dir>                                       │
│  • git add <data_dir>.dvc                                   │
│  • git commit                                               │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ 2. Push to remote
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              DVC Remote (S3/MinIO)                          │
│  • Stores actual data files                                 │
│  • Versioned by DVC                                         │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ 3. Pull on other machine
                     ▼
┌─────────────────────────────────────────────────────────────┐
│            DVCSetup / dvc pull                              │
│  • Fetches data from S3/MinIO                               │
│  • Restores to local directory                              │
└─────────────────────────────────────────────────────────────┘
```

### 5. API Service Flow

```
┌─────────────────────────────────────────────────────────────┐
│                 HTTP Client Request                         │
│        POST /api/run/application/stream                     │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ 1. Route to endpoint
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              FastAPI Application                            │
│  Created by: create_fastapi_app()                           │
│  • Health endpoint: /health                                 │
│  • Bot API router: /api/*                                   │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ 2. Delegate to bot manager
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              BotManagerProtocol                             │
│  • run(task_name): Synchronous execution                    │
│  • stream_run(task_name): Streaming execution               │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ 3. Execute crew
                     ▼
┌─────────────────────────────────────────────────────────────┐
│          CrewAI Orchestrator                                │
│  Executes crew and yields results                           │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ 4. Stream back via SSE
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              EventSourceResponse                            │
│  Server-Sent Events (SSE) streaming                         │
│  Format: data: <chunk>\n\n                                  │
└─────────────────────────────────────────────────────────────┘
```

---

## Common Library Purpose

### Why Amsha Exists

Amsha serves as a **common library** to eliminate code duplication and standardize patterns across multiple AI agent applications. Instead of each project implementing its own:

- CrewAI configuration management
- LLM initialization
- Output validation
- Database repositories
- API endpoints
- Data versioning

...they can simply import and configure Amsha.

### Key Benefits

1. **Reusability**: Write once, use across multiple projects
2. **Consistency**: Standardized patterns and practices
3. **Maintainability**: Fix bugs and add features in one place
4. **Testability**: Well-tested common components
5. **Flexibility**: Support both database and file-backed configurations
6. **Scalability**: Built-in patterns for growing applications
7. **Abstraction**: Applications depend on Amsha's orchestrator, not directly on CrewAI - easier to upgrade or swap underlying frameworks

### Common Use Cases

1. **Building AI Research Assistants**
   - Use `crew_forge` to configure researcher agents
   - Use `crew_linter` to validate research outputs
   - Use `mlops` to version research data

2. **Creating Content Generation Services**
   - Use `llm_factory` to manage different LLMs
   - Use `api` to expose as REST/streaming service
   - Use `output_process` to validate generated content

3. **Developing Multi-Agent Systems**
   - Use `crew_forge.orchestrator` to coordinate agents
   - Use repositories to store agent configurations
   - Use guardrails to ensure output quality

4. **Building Evaluation Pipelines**
   - Use separate LLMs for creative vs. evaluation tasks
   - Use `crew_linter` for automated quality checks
   - Use `output_process.evaluation` for metrics

---

## Installation & Setup

### Prerequisites

- Python 3.9+
- MongoDB (if using database-backed crews)
- MinIO or AWS S3 (for DVC data versioning)
- Docker (optional, for MinIO)

### Install from Source

```bash
# Clone the repository
git clone <repository-url>
cd Amsha

# Install dependencies
pip install -e .
```

### Docker Setup (MinIO for DVC)

```bash
# Start MinIO container
docker-compose up -d

# Access MinIO console at http://localhost:9001
# Default credentials: minioadmin / minioadmin
```

### Configuration

Amsha uses YAML configuration files typically stored in `config/`:

- `app_config.yaml`: Application-specific settings
- `llm_config.yaml`: LLM provider credentials and parameters
- `job_config.yaml`: Crew execution job definitions

*Note: Configuration files are gitignored for security*

---

## Technology Stack

### Core Dependencies

- **CrewAI** (0.201.1): Multi-agent orchestration framework
- **Pydantic** (2.11.9): Data validation and settings management
- **PyMongo** (4.11.3): MongoDB driver for repository pattern
- **FastAPI** (0.121.3): Modern web framework for APIs
- **SSE-Starlette** (3.0.3): Server-sent events for streaming

### NLP & ML

- **BERTopic** (0.17.0): Advanced topic modeling
- **Gensim** (4.3.3): Topic modeling and similarity
- **scikit-learn** (1.6.1): Machine learning utilities
- **NLTK** (3.9.1): Natural language processing
- **NetworkX** (3.4.2): Graph analysis

### Data & MLOps

- **DVC-S3** (3.0.1): Data version control with S3
- **Boto3** (1.34.0): AWS/MinIO S3 client
- **Pandas** (2.3.2): Data manipulation
- **Docling** (2.55.0): Document processing

### Utilities

- **Dependency-Injector** (4.48.1): Dependency injection framework
- **PyYAML** (6.0.2): YAML parsing
- **Beautiful Soup** (4.13.4): HTML/XML parsing
- **Markdown** (3.8): Markdown processing

### Development

- Project structure follows **setuptools** conventions
- Source code in `src/nikhil/amsha/`
- Examples and documentation in `docs/` and component `example/` directories

---

## Project Structure

```
Amsha/
├── src/nikhil/amsha/          # Main source code
│   ├── toolkit/               # Core toolkit modules
│   ├── crewai/                # Custom CrewAI tools
│   ├── utils/                 # Common utilities
│   ├── nlp_eval_utils/        # NLP evaluation
│   ├── preprocessing/         # Text preprocessing
│   └── exception/             # Custom exceptions
├── config/                    # Configuration files (gitignored)
├── data/                      # Data directory (tracked by DVC)
├── docs/                      # Documentation
├── knowledge/                 # Knowledge base files
├── docker-compose.yml         # MinIO setup for DVC
├── pyproject.toml             # Project metadata and dependencies
├── requirements.txt           # Dependency list
└── README.md                  # This file
```

---

## License

*License information not specified in current codebase*

---

## Contributing

*Contribution guidelines not specified in current codebase*

---

## Support

For issues, questions, or feature requests, please refer to the project repository or contact the maintainers.
