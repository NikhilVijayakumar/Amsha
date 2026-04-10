# Testing Patterns

**Analysis Date:** 2026-04-10

## Test Framework

**Runner:**
- unittest (Python standard library)
- Also supports pytest (not configured with pytest.ini)

**Assertion Library:**
- unittest (assertEqual, assertRaises, etc.)

**Run Commands:**
```bash
python -m unittest discover -s tests/unit              # Run all unit tests
python -m pytest tests/unit/                           # Run with pytest (if installed)
python -m pytest tests/unit/ -v                        # Verbose mode
python -m pytest tests/unit/ --coverage                 # Coverage (if pytest-cov installed)
```

## Test File Organization

**Location:**
- Base: `tests/`
- Structure: `tests/unit/<module>/<component>/test_{id}_{slug}.py`

**Directory Structure:**
```
tests/
├── unit/                           # Isolated domain/service tests
│   ├── crew_forge/
│   │   ├── service/
│   │   │   └── test_atomic_builders.py
│   │   ├── exceptions/
│   │   │   └── test_crew_forge_exceptions.py
│   │   ├── domain/
│   │   │   └── test_domain.py
│   │   └── orchestrator/
│   │       └── test_amsha_db_orchestrator.py
│   ├── llm_factory/
│   │   ├── service/
│   │   └── utils/
│   ├── utils/
│   ├── execution_state/
│   ├── execution_runtime/
│   ├── output_process/
│   └── crew_monitor/
├── property/                       # Property-based tests
│   └── test_alignment_properties.py
└── test_crew_performance_monitor.py  # Standalone tests
```

**Naming Convention:**
- Test files: `test_{id}_{slug}.py`
- Test classes: `Test{ClassName}`
- Test methods: `test_{method_name}_{scenario}`

**Example:**
```
test_atomic_builders.py
├── class TestAtomicDbBuilderService(unittest.TestCase)
│   ├── test_add_agent()
│   ├── test_add_task()
│   └── test_build()
└── class TestAtomicYamlBuilderService(unittest.TestCase)
    └── ...
```

## Test Structure

**Basic Pattern:**
```python
import unittest
from unittest.mock import MagicMock, patch

class TestAtomicDbBuilderService(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        self.mock_data = MagicMock(spec=CrewData)
        self.mock_agent_repo = MagicMock(spec=IAgentRepository)
        self.mock_task_repo = MagicMock(spec=ITaskRepository)
        with patch('amsha.crew_forge.service.crew_builder_service.CrewBuilderService') as mock_builder_class:
            self.service = AtomicDbBuilderService(self.mock_data, self.mock_agent_repo, self.mock_task_repo)
            self.service.builder = mock_builder_class.return_value

    def test_add_agent(self):
        """Test adding agent by ID."""
        # Arrange
        self.mock_agent_repo.get_agent_by_id.return_value = AgentResponse(_id="1", role="R", goal="G", backstory="B")
        
        # Act
        self.service.add_agent("1")
        
        # Assert
        self.service.builder.add_agent.assert_called()

    def test_add_agent_not_found(self):
        """Test adding non-existent agent raises error."""
        self.mock_agent_repo.get_agent_by_id.return_value = None
        
        with self.assertRaises(ValueError):
            self.service.add_agent("invalid")
```

## Mocking

**Framework:** `unittest.mock` (MagicMock, Mock, patch)

**Patterns:**

1. **Mock Interface:**
```python
mock_agent_repo = MagicMock(spec=IAgentRepository)
mock_agent_repo.get_agent_by_id.return_value = AgentResponse(...)
```

2. **Mock Class with patch:**
```python
with patch('amsha.crew_forge.service.atomic_db_builder.AtomicDbBuilderService') as mock_class:
    mock_class.return_value.method.return_value = expected_value
```

3. **Spec-Based Mocking:**
```python
mock_agent = MagicMock(spec=Agent)
```

**What to Mock:**
- Repository interfaces (`IAgentRepository`, `ITaskRepository`)
- External services (LLM APIs, databases)
- File system operations (use `tmp_path` fixture)

**What NOT to Mock:**
- Internal domain logic being tested
- Pydantic model construction

## Fixtures and Test Data

**setUp Method:**
```python
def setUp(self):
    self.mock_data = MagicMock(spec=CrewData)
    self.mock_data.llm = MagicMock()
    self.mock_data.module_name = "test_module"
    self.mock_data.output_dir_path = "/tmp"
```

**Test Data Patterns:**
- Use real Pydantic models when testing domain logic
- Use MagicMock for infrastructure dependencies
- Example: `AgentResponse(_id="1", role="R", goal="G", backstory="B")`

## Exception Testing

**Pattern:**
```python
def test_add_agent_not_found(self):
    self.mock_agent_repo.get_agent_by_id.return_value = None
    
    with self.assertRaises(ValueError):
        self.service.add_agent("invalid")
```

**Test Coverage Requirements:**
- Happy path: Verify function works with valid input
- Corner cases: Edge cases (empty lists, None, max values)
- Validation: Verify raises expected exceptions for invalid input
- Error paths: All exception paths must be tested

## Coverage

**Target:**
- Aim for 80%+ coverage on service layer
- 100% coverage on public API methods

**No Formal Configuration:**
- No pytest.ini or coverage configuration detected
- Manual coverage estimation via code review

## Test Types

**Unit Tests:**
- Test domain logic in isolation
- Mock all repository dependencies
- Located in `tests/unit/{module}/`

**Integration Tests:**
- Test against real infrastructure (MongoDB, MinIO)
- Use Docker containers for test databases
- Clean up after each test
- Located in `tests/integration/` (not yet present in codebase)

**Property-Based Tests:**
- Located in `tests/property/`
- Example: `test_alignment_properties.py`

## Test Isolation

**Rules:**
- No test should depend on another test
- Use `setUp()` method for common setup
- Mock external services (LLM APIs, external APIs)

**File System:**
- Use `tmp_path` fixture for file operations
- Never write to real project root

## Test Execution

**Run All Tests:**
```bash
python -m unittest discover -s tests -p "test_*.py"
```

**Run Specific Module:**
```bash
python -m unittest tests.unit.crew_forge.service.test_atomic_builders -v
```

**Run Single Test Class:**
```bash
python -m unittest tests.unit.crew_forge.service.test_atomic_builders.TestAtomicDbBuilderService -v
```

## Common Patterns in Codebase

**1. Service Testing:**
```python
# tests/unit/crew_forge/service/test_atomic_builders.py
from amsha.crew_forge.service.atomic_db_builder import AtomicDbBuilderService

class TestAtomicDbBuilderService(unittest.TestCase):
    def setUp(self):
        mock_data = MagicMock(spec=CrewData)
        mock_agent_repo = MagicMock(spec=IAgentRepository)
        mock_task_repo = MagicMock(spec=ITaskRepository)
        with patch('amsha.crew_forge.service.crew_builder_service.CrewBuilderService') as mock_builder_class:
            self.service = AtomicDbBuilderService(mock_data, mock_agent_repo, mock_task_repo)
            self.service.builder = mock_builder_class.return_value
```

**2. Exception Testing:**
```python
# tests/unit/crew_forge/exceptions/test_crew_forge_exceptions.py
from amsha.crew_forge.exceptions.crew_forge_exception import CrewForgeException

class TestCrewForgeExceptions(unittest.TestCase):
    def test_crew_forge_exception_str(self):
        exc = CrewForgeException("Base error", "Some details")
        self.assertEqual(str(exc), "Base error: Some details")
```

**3. State Repository Testing:**
```python
# tests/unit/execution_state/service/test_state_manager.py
class TestInMemoryStateRepository(unittest.TestCase):
    def setUp(self):
        self.repo = InMemoryStateRepository()
        
    def test_save_and_get(self):
        state = ExecutionState(inputs={"test": "data"})
        self.repo.save(state)
        retrieved = self.repo.get(state.execution_id)
        self.assertEqual(retrieved, state)
```

---

*Testing analysis: 2026-04-10*