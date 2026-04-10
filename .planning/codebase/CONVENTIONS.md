# Coding Conventions

**Analysis Date:** 2026-04-10

## Naming Patterns

**Files:**
- Modules and packages: lowercase with underscores (snake_case)
  - Example: `atomic_db_builder.py`, `crew_builder_service.py`
- Test files: `test_{id}_{slug}.py` pattern (e.g., `test_ar_ut_001_extraction.py`)

**Classes:**
- PascalCase for all classes
  - Example: `AtomicDbBuilderService`, `AgentResponse`, `InMemoryStateRepository`
- Interface/Protocol prefix: `I` for ABC interfaces (e.g., `IAgentRepository`)
  - Protocol for client-facing interfaces (e.g., `BotManagerProtocol`)

**Functions:**
- snake_case for functions and methods
  - Example: `add_agent()`, `build_crew()`, `get_agent_by_id()`

**Variables:**
- snake_case for all variables
  - Example: `mock_agent_repo`, `llm_type`, `execution_status`

**Constants:**
- UPPER_CASE with underscores
  - Example: `CREW_AI_VERSION`, `DEFAULT_OUTPUT_DIR`

**Types (Pydantic Models):**
- PascalCase with suffix indicating purpose
  - Example: `AgentRequest`, `AgentResponse`, `TaskResponse`, `CrewData`

## Code Style

**Formatting:**
- Tool: `black` (not detected in project, but mentioned in AGENTS.md)
- Line length: 88 characters (black default)
- Indentation: 4 spaces

**Linting:**
- Tool: `mypy` for type checking
- Configuration: Strict mode enabled
- Zero "Any" policy - avoid `Any` unless interacting with typeless 3rd party libraries
- If `Any` is required, use `# type: ignore[misc]` with explanation

**Import Organization:**
Order (per `.agent/rules/import-standards.md`):
1. Standard library imports
2. Third-party imports
3. Local/absolute imports from package

**Absolute Import Rule:**
- NEVER use relative imports (`from . import`, `from ..utils import`)
- ALWAYS use absolute imports starting from package name `amsha`
- Example: `from amsha.crew_forge.domain.models.agent_data import AgentResponse`

## Type Hints

**Mandatory:**
- All function parameters must have type hints
- All return values must have type annotations (`-> None`, `-> int`, etc.)
- Use `Optional`, `Union`, `List` from `typing` module

**Pydantic Over Dicts:**
- Never pass raw dictionaries (`Dict[str, Any]`) between layers
- Always define Pydantic models with `frozen=True` for structured data
- Example: `class AgentRequest(BaseModel)`

**Protocols for Interfaces:**
- Do not type-hint concrete classes
- Use Protocol definitions for abstraction
- Example: `def fn(repo: IAgentRepository)` (interface), NOT concrete implementation

## Dependency Injection

**Strict Rule:**
- NEVER instantiate complex classes manually inside services
- BAD: `self.repo = MongoAgentRepository()`
- GOOD: `self.repo: IAgentRepository` (injected via `__init__`)

**Container Pattern:**
- All wiring happens in `dependency/containers.py` using `dependency-injector` library
- Use Factory Providers for runtime objects (like LLM instances)

**Example:**
```python
class AtomicDbBuilderService:
    def __init__(self, agent_repo: IAgentRepository, task_repo: ITaskRepository):
        self.agent_repo = agent_repo  # Injected, not created
        self.task_repo = task_repo
```

## Exception Handling Strategy

**Custom Exception Hierarchy:**
- Base exception: `AmshaException(Exception)`
- Domain-specific: `RepositoryException(AmshaException)`, `AgentNotFoundException(RepositoryException)`
- Located in component `exceptions/` directories
  - Example: `src/nikhil/amsha/crew_forge/exceptions/agent_not_found_exception.py`

**Anti-Patterns to Avoid:**
- NEVER raise generic `Exception` or `ValueError` for domain logic
- Use custom exceptions from component directory

**Exception Wrapping:**
- Use `wrap_external_exception()` to wrap external errors
- Include component context in error messages

## Docstrings

**Required For:**
- All public classes and methods
- All Protocol/ABC definitions
- Complex algorithms or business logic

**Format (Google Style):**
```python
def build_crew(self, process: Process = Process.sequential) -> Crew:
    """
    Builds a CrewAI Crew from configured agents and tasks.
    
    Args:
        process: Execution process (sequential or hierarchical)
        
    Returns:
        Configured Crew instance ready for execution
        
    Raises:
        InvalidCrewConfigException: If required agents/tasks are missing
    """
```

## Module Design

**Exports:**
- Use `__all__` in `__init__.py` to define public API
- Only expose public APIs through `__init__.py` exports
- Do not expose internal implementation details

**Barrel Files:**
- Use `__init__.py` to re-export from submodules
- Example: `from .service.atomic_db_builder import AtomicDbBuilderService` in `crew_forge/service/__init__.py`

## Architectural Principles (Clean Architecture)

**Layer Dependencies (Inner → Outer):**
```
Domain (Models) ← Service/Application ← Orchestrator ← Infrastructure (Adapters/API)
```

**Rules:**
- Domain layer NEVER depends on outer layers
- Domain: Pure Python objects (Pydantic models), NO external framework dependencies
- Repository interfaces: Abstract contracts only, NO implementation details
- Application/Service: Business logic, depends ONLY on domain models and repository interfaces
- Infrastructure: Concrete implementations (MongoDB)

**SOLID Principles:**
- SRP: Single responsibility - split services if doing multiple things
- OCP: Open/closed - add new features via new classes, NOT branching
- LSP: Any interface implementation must be swappable
- ISP: Keep interfaces focused
- DIP: High-level modules depend on abstractions, never concrete implementations

## File Location Guidelines

**New Feature:**
- Implementation: `src/nikhil/amsha/{module}/service/`
- Domain models: `src/nikhil/amsha/{module}/domain/models/`

**New Component:**
- Implementation: In appropriate module directory
- Tests: `tests/unit/{module}/`

**Utilities:**
- Shared helpers: `src/nikhil/amsha/utils/`

---

*Convention analysis: 2026-04-10*