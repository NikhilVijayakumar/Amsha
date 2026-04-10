# Technology Stack

**Analysis Date:** 2026-04-10

## Languages

**Primary:**
- Python 3.x - Core language for all Amsha library code

**Version:**
- Amsha Version: 2.11.0 (from `pyproject.toml`)

## Package Manager

**Build System:** setuptools
- Config: `pyproject.toml`
- Package directory: `src/nikhil`

**Installation:**
```
pip install amsha
```

## Core Frameworks

**Orchestration:**
- crewai 0.201.1 - AI agent orchestration framework
- crewai-tools 0.75.0 - Tools for crewai agents

**Dependency Injection:**
- dependency-injector 4.48.2 - DI container implementation

**Data Validation:**
- pydantic 2.11.9 - Data validation using Python type hints

**Configuration:**
- PyYAML 6.0.3 - YAML configuration file parsing

## Data Processing

**Data Analysis:**
- pandas 2.3.2 - Data manipulation and analysis
- openpyxl 3.1.5 - Excel file reading/writing

**Document Conversion:**
- docling 2.53.0 - Document to markdown/JSON conversion

**System Monitoring:**
- psutil 7.1.3 - System and process utilities
- nvidia-ml-py 13.580.82 - NVIDIA GPU monitoring

**Character Detection:**
- chardet 5.2.0 - Character encoding detection

## Database

**MongoDB:**
- pymongo 4.11.3 - MongoDB Python driver

## External Dependencies

**Nibandha (via git):**
- Source: `git+https://github.com/NikhilVijayakumar/Nibandha.git@main`
- Purpose: Logging infrastructure and export utilities
- Feature flag: `[export]`

## Optional Dependencies

**Research:**
- scikit-learn >= 1.3.0 - Machine learning
- matplotlib >= 3.7.0 - Visualization
- seaborn >= 0.12.0 - Statistical graphics
- jupyter >= 1.0.0 - Jupyter notebooks

## Internal Adapters

**LLM Provider Adapter:**
- `src/nikhil/amsha/llm_factory/adapters/crewai_adapter.py`
- Wraps CrewAI LLM to implement `ILLMProvider` Protocol
- Enables swapping LLM implementations while maintaining consistent interface

**Document Knowledge Source:**
- `src/nikhil/amsha/crew_forge/knowledge/amsha_crew_docling_source.py`
- Extends CrewAI's `BaseKnowledgeSource`
- Provides document loading and chunking for RAG workflows

## Configuration

**Config Loading:**
- Uses `ConfigurationManager` class in `src/nikhil/amsha/configuration/application/configuration_manager.py`
- Supports YAML and JSON configuration files
- Strict Pydantic validation via `StrictConfigValidator`

**Config Models:**
- `amsha_app_config.py` - Application-level config
- `amsha_job_config.py` - Job configuration
- `amsha_llm_config.py` - LLM API endpoints and parameters

**Environment Variables:**
- API keys loaded from environment variable names specified in config
- Example: `api_key_env` field in `LLMModelDefinition` points to env var name

---

*Stack analysis: 2026-04-10*
