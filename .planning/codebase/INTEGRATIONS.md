# External Integrations

**Analysis Date:** 2026-04-10

## LLM Providers

**Primary Integration:**
- CrewAI LLM - Core orchestration uses CrewAI's LLM abstraction
  - Adapter: `src/nikhil/amsha/llm_factory/adapters/crewai_adapter.py`
  - Wraps `crewai.LLM` to implement `ILLMProvider` Protocol

**Supported via litellm:**
- Azure OpenAI - Configured via `base_url`, `api_version`, and `model` in LLM config
- OpenAI - Via model name and API key
- Anthropic - Via model name and API key
- Google Gemini - Via model name and API key
- Any OpenAI-compatible API - Via custom base_url

**LLM Configuration:**
- Config file: YAML with structure defined in `src/nikhil/amsha/configuration/domain/models/amsha_llm_config.py`
- Parameters: temperature, top_p, max_completion_tokens, presence_penalty, frequency_penalty, stop sequences
- Supports multiple model types: `creative` and `evaluation`

## Database

**MongoDB:**
- Client: `pymongo` 4.11.3
- Implementation: `src/nikhil/amsha/crew_forge/repo/adapters/mongo/mongo_repository.py`
- Connection: Via `MongoRepository` class taking `RepoData` with `mongo_uri`, `db_name`, `collection_name`
- Operations: find_one, find_many, insert_one, insert_many, update_one, delete_one, create_unique_compound_index

**Repository Interfaces:**
- `src/nikhil/amsha/crew_forge/repo/interfaces/i_agent_repository.py`
- `src/nikhil/amsha/crew_forge/repo/interfaces/i_task_repository.py`
- `src/nikhil/amsha/crew_forge/repo/interfaces/i_crew_config_repository.py`
- `src/nikhil/amsha/crew_forge/repo/interfaces/i_repository.py`

## Document Processing

**Docling:**
- Package: `docling` 2.53.0
- Purpose: Convert PDF, DOCX, HTML, XLSX, PPTX, images to markdown/JSON
- Implementation: `src/nikhil/amsha/crew_forge/knowledge/amsha_crew_docling_source.py`
- Extends: `crewai.knowledge.source.base_knowledge_source.BaseKnowledgeSource`
- Chunking: Uses `HierarchicalChunker` from docling_core
- Supported formats: MD, ASCIIDOC, PDF, DOCX, HTML, IMAGE, XLSX, PPTX
- Also supports URLs (http/https) and local files

## Logging & Observability

**Nibandha:**
- Source: `git+https://github.com/NikhilVijayakumar/Nibandha.git@main`
- Feature flag: `[export]` (optional extra)
- Purpose: Logging infrastructure with file rotation
- Implementation: `src/nikhil/amsha/common/logger.py`

**Standard Library:**
- `logging` - Python standard library logging
- `logging.getLogger()` - Used throughout configuration and services

## Data Export

**Pandas + Openpyxl:**
- Used for Excel report generation
- `src/nikhil/amsha/crew_monitor/service/reporting_tool.py` - Uses `pandas` for analysis
- `src/nikhil/amsha/crew_monitor/service/contribution_analyzer.py` - Uses `pandas` for metrics

## System Monitoring

**psutil:**
- Process and system monitoring
- Used for resource tracking

**nvidia-ml-py:**
- NVIDIA GPU monitoring (CUDA)
- Used for GPU metrics when available

## Configuration Files

**YAML Configuration:**
- Job config: Agent/task definitions
- App config: Application settings
- LLM config: Model endpoints and parameters

**Environment Variables:**
- API keys loaded from environment by name
- Config field: `api_key_env` specifies env var name
- Supports Azure OpenAI, OpenAI, Anthropic, etc.

## Orchestration Patterns

**Dual-Mode Architecture:**
1. **Database-Backed** (`AmshaCrewDBApplication`)
   - Agent/Task configs stored in MongoDB
   - Uses `DbCrewOrchestrator`

2. **File-Backed** (`AmshaCrewFileApplication`)
   - Agent/Task configs in YAML files
   - Uses `FileCrewOrchestrator`

Both modes share the same client interface via base classes.

---

*Integration audit: 2026-04-10*
