import os
import json

# Name of the template directory to be created
TEMPLATE_DIR = "cookiecutter-clean-arch"
SLUG = "{{cookiecutter.project_slug}}"

def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip())
    print(f"Created: {path}")

# ==========================================
# 1. Cookiecutter Configuration (cookiecutter.json)
# ==========================================
cookiecutter_json = json.dumps({
    "project_name": "My Clean Project",
    "project_slug": "{{ cookiecutter.project_name.lower().replace(' ', '_').replace('-', '_') }}",
    "project_description": "A clean architecture Python project.",
    "author_name": "Your Name",
    "python_version": "3.11",
    "version": "0.1.0"
}, indent=4)

# ==========================================
# 2. The Standards Constitution (STANDARDS.md)
# ==========================================
standards_md = """
# {{cookiecutter.project_name}} - Engineering Constitution & Standards

**Goal:** Maintain strict adherence to Clean Architecture, SOLID principles, and separation of concerns.

---

## 1. Architectural Boundaries (The "Law")

* **Domain (`src/{{cookiecutter.project_slug}}/domain`)**: Pure Python objects. NO external dependencies.
* **Interfaces (`src/{{cookiecutter.project_slug}}/interfaces`)**: Abstract contracts only.
* **Application (`src/{{cookiecutter.project_slug}}/application`)**: Business logic. Depends ONLY on domain and interfaces.
* **Infrastructure (`src/{{cookiecutter.project_slug}}/infrastructure`)**: Concrete implementations (DB, API, IO).

**Dependency Rule (Inner → Outer):**
`Domain` ← `Interfaces` ← `Application` ← `Infrastructure`

---

## 2. Interface Design

* **Internal Repositories:** Use `ABC` (Abstract Base Class).
* **External/Client APIs:** Use `Protocol` (Duck Typing).

---

## 3. Dependency Injection

* **Strict Rule:** Never instantiate complex classes inside services.
* **Wiring:** All wiring happens in `infrastructure/container.py` or `main.py`.

---

## 4. Exception Handling

* **Never** raise generic `ValueError` or `Exception` for business logic.
* Use custom exceptions defined in `domain/exceptions.py`.
* Infrastructure adapters must catch external errors (e.g., SQL, HTTP) and re-raise domain exceptions.

---

## 5. Testing

* **Unit:** Mock interfaces. Test logic in isolation.
* **Integration:** Test repositories with real resources (Docker).
"""

# ==========================================
# 3. Project Structure & Code Files
# ==========================================

# pyproject.toml
pyproject_toml = """
[project]
name = "{{cookiecutter.project_slug}}"
version = "{{cookiecutter.version}}"
description = "{{cookiecutter.project_description}}"
authors = [{name = "{{cookiecutter.author_name}}"}]
requires-python = ">={{cookiecutter.python_version}}"
dependencies = [
    "pydantic>=2.0.0",
    "dependency-injector>=4.41.0",  # Optional, but recommended
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "mypy>=1.0",
    "ruff>=0.1.0",
    "pre-commit>=3.0"
]

[tool.pytest.ini_options]
pythonpath = ["src"]
testpaths = ["tests"]

[tool.mypy]
python_version = "{{cookiecutter.python_version}}"
strict = true
ignore_missing_imports = true

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
"""

# README.md
readme_md = """
# {{cookiecutter.project_name}}

{{cookiecutter.project_description}}

## Architecture
This project follows strictly enforced Clean Architecture standards.
Please read **[STANDARDS.md](STANDARDS.md)** before contributing.

## Setup
```bash
pip install -e .[dev]
pytest
"""

src/init.py
init_py = """

Version {{cookiecutter.version}}
"""
=======================================
4. Generator Execution
==========================================
def main(): base = TEMPLATE_DIR

# Root Files
create_file(f"{base}/cookiecutter.json", cookiecutter_json)
create_file(f"{base}/{SLUG}/STANDARDS.md", standards_md)
create_file(f"{base}/{SLUG}/pyproject.toml", pyproject_toml)
create_file(f"{base}/{SLUG}/README.md", readme_md)
create_file(f"{base}/{SLUG}/.gitignore", "__pycache__/\n*.pyc\n.env\n.pytest_cache/\n.mypy_cache/")

# Source Code Structure
src_base = f"{base}/{SLUG}/src/{SLUG}"

# __init__
create_file(f"{src_base}/__init__.py", init_py)

# Domain Layer
create_file(f"{src_base}/domain/__init__.py", "")
create_file(f"{src_base}/domain/models.py", domain_models_py)
create_file(f"{src_base}/domain/exceptions.py", domain_exceptions_py)

# Interface Layer
create_file(f"{src_base}/interfaces/__init__.py", "")
create_file(f"{src_base}/interfaces/repository.py", interfaces_repo_py)

# Application Layer
create_file(f"{src_base}/application/__init__.py", "")
create_file(f"{src_base}/application/services.py", app_services_py)

# Infrastructure Layer
create_file(f"{src_base}/infrastructure/__init__.py", "")
create_file(f"{src_base}/infrastructure/adapters/__init__.py", "")
create_file(f"{src_base}/infrastructure/adapters/memory_repo.py", infra_repo_py)

# Tests
create_file(f"{base}/{SLUG}/tests/__init__.py", "")
create_file(f"{base}/{SLUG}/tests/unit/__init__.py", "")
create_file(f"{base}/{SLUG}/tests/unit/test_service.py", test_service_py)
create_file(f"{base}/{SLUG}/tests/integration/__init__.py", "")

print(f"\n✅ Template generated in: {os.path.abspath(TEMPLATE_DIR)}")
print("Next steps:")
print("1. pip install cookiecutter")
print(f"2. cookiecutter {TEMPLATE_DIR}")
This is a Python script that acts as a "Meta-Generator."

Running this script will generate a fully functional Cookiecutter template directory on your machine. You can then use that template to spawn as many Clean Architecture projects as you need, all of which will inherently follow your "Constitution."

Instructions
Copy the code below into a file named create_template.py.

Run it: python create_template.py.

It will create a folder named cookiecutter-clean-arch.

Run cookiecutter against it (instructions at the bottom).

Python

import os
import json

# Name of the template directory to be created
TEMPLATE_DIR = "cookiecutter-clean-arch"
SLUG = "{{cookiecutter.project_slug}}"

def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip())
    print(f"Created: {path}")

# ==========================================
# 1. Cookiecutter Configuration (cookiecutter.json)
# ==========================================
cookiecutter_json = json.dumps({
    "project_name": "My Clean Project",
    "project_slug": "{{ cookiecutter.project_name.lower().replace(' ', '_').replace('-', '_') }}",
    "project_description": "A clean architecture Python project.",
    "author_name": "Your Name",
    "python_version": "3.11",
    "version": "0.1.0"
}, indent=4)

# ==========================================
# 2. The Standards Constitution (STANDARDS.md)
# ==========================================
standards_md = """
# {{cookiecutter.project_name}} - Engineering Constitution & Standards

**Goal:** Maintain strict adherence to Clean Architecture, SOLID principles, and separation of concerns.

---

## 1. Architectural Boundaries (The "Law")

* **Domain (`src/{{cookiecutter.project_slug}}/domain`)**: Pure Python objects. NO external dependencies.
* **Interfaces (`src/{{cookiecutter.project_slug}}/interfaces`)**: Abstract contracts only.
* **Application (`src/{{cookiecutter.project_slug}}/application`)**: Business logic. Depends ONLY on domain and interfaces.
* **Infrastructure (`src/{{cookiecutter.project_slug}}/infrastructure`)**: Concrete implementations (DB, API, IO).

**Dependency Rule (Inner → Outer):**
`Domain` ← `Interfaces` ← `Application` ← `Infrastructure`

---

## 2. Interface Design

* **Internal Repositories:** Use `ABC` (Abstract Base Class).
* **External/Client APIs:** Use `Protocol` (Duck Typing).

---

## 3. Dependency Injection

* **Strict Rule:** Never instantiate complex classes inside services.
* **Wiring:** All wiring happens in `infrastructure/container.py` or `main.py`.

---

## 4. Exception Handling

* **Never** raise generic `ValueError` or `Exception` for business logic.
* Use custom exceptions defined in `domain/exceptions.py`.
* Infrastructure adapters must catch external errors (e.g., SQL, HTTP) and re-raise domain exceptions.

---

## 5. Testing

* **Unit:** Mock interfaces. Test logic in isolation.
* **Integration:** Test repositories with real resources (Docker).
"""

# ==========================================
# 3. Project Structure & Code Files
# ==========================================

# pyproject.toml
pyproject_toml = """
[project]
name = "{{cookiecutter.project_slug}}"
version = "{{cookiecutter.version}}"
description = "{{cookiecutter.project_description}}"
authors = [{name = "{{cookiecutter.author_name}}"}]
requires-python = ">={{cookiecutter.python_version}}"
dependencies = [
    "pydantic>=2.0.0",
    "dependency-injector>=4.41.0",  # Optional, but recommended
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "mypy>=1.0",
    "ruff>=0.1.0",
    "pre-commit>=3.0"
]

[tool.pytest.ini_options]
pythonpath = ["src"]
testpaths = ["tests"]

[tool.mypy]
python_version = "{{cookiecutter.python_version}}"
strict = true
ignore_missing_imports = true

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
"""

# README.md
readme_md = """
# {{cookiecutter.project_name}}

{{cookiecutter.project_description}}

## Architecture
This project follows strictly enforced Clean Architecture standards.
Please read **[STANDARDS.md](STANDARDS.md)** before contributing.

## Setup
```bash
pip install -e .[dev]
pytest
"""

src/init.py
init_py = """

Version {{cookiecutter.version}}
"""

src/domain/exceptions.py
domain_exceptions_py = """ class AppBaseException(Exception): """Base exception for the application.""" pass

class ResourceNotFoundException(AppBaseException): """Raised when a requested resource is not found.""" def init(self, resource_type: str, resource_id: str): super().init(f"{resource_type} with ID {resource_id} not found.") """

src/domain/models.py
domain_models_py = """ from pydantic import BaseModel, ConfigDict from datetime import datetime from typing import Optional

class BaseEntity(BaseModel): model_config = ConfigDict(frozen=True)

class ExampleEntity(BaseEntity): """A pure domain entity.""" id: str created_at: datetime name: str """

src/interfaces/repository.py
interfaces_repo_py = """ from abc import ABC, abstractmethod from typing import Optional from ..domain.models import ExampleEntity

class IExampleRepository(ABC): """Interface for Example Repository. Must be implemented by Infrastructure."""

@abstractmethod
def get_by_id(self, entity_id: str) -> Optional[ExampleEntity]:
    pass

@abstractmethod
def save(self, entity: ExampleEntity) -> None:
    pass
"""

src/application/services.py
app_services_py = """ from ..domain.models import ExampleEntity from ..domain.exceptions import ResourceNotFoundException from ..interfaces.repository import IExampleRepository

class ExampleService: """ Orchestrates domain logic. Notice: Dependencies are injected via init. """ def init(self, repo: IExampleRepository): self.repo = repo

def get_example(self, entity_id: str) -> ExampleEntity:
    entity = self.repo.get_by_id(entity_id)
    if not entity:
        raise ResourceNotFoundException("ExampleEntity", entity_id)
    return entity
"""

src/infrastructure/adapters/memory_repo.py
infra_repo_py = """ from typing import Optional, Dict from ...domain.models import ExampleEntity from ...interfaces.repository import IExampleRepository

class InMemoryExampleRepository(IExampleRepository): """ Concrete implementation of the repository. This could be replaced by SqlAlchemyRepository or MongoRepository without changing the Service layer. """ def init(self): self._store: Dict[str, ExampleEntity] = {}

def get_by_id(self, entity_id: str) -> Optional[ExampleEntity]:
    return self._store.get(entity_id)

def save(self, entity: ExampleEntity) -> None:
    self._store[entity.id] = entity
"""

tests/unit/test_service.py
test_service_py = """ import pytest from unittest.mock import Mock from {{cookiecutter.project_slug}}.application.services import ExampleService from {{cookiecutter.project_slug}}.interfaces.repository import IExampleRepository from {{cookiecutter.project_slug}}.domain.models import ExampleEntity from {{cookiecutter.project_slug}}.domain.exceptions import ResourceNotFoundException from datetime import datetime

def test_get_example_success(): # Arrange mock_repo = Mock(spec=IExampleRepository) entity = ExampleEntity(id="123", name="Test", created_at=datetime.now()) mock_repo.get_by_id.return_value = entity

service = ExampleService(repo=mock_repo)

# Act
result = service.get_example("123")

# Assert
assert result == entity
mock_repo.get_by_id.assert_called_once_with("123")
def test_get_example_not_found(): # Arrange mock_repo = Mock(spec=IExampleRepository) mock_repo.get_by_id.return_value = None service = ExampleService(repo=mock_repo)

# Act & Assert
with pytest.raises(ResourceNotFoundException):
    service.get_example("999")
"""

==========================================
4. Generator Execution
==========================================
def main(): base = TEMPLATE_DIR

# Root Files
create_file(f"{base}/cookiecutter.json", cookiecutter_json)
create_file(f"{base}/{SLUG}/STANDARDS.md", standards_md)
create_file(f"{base}/{SLUG}/pyproject.toml", pyproject_toml)
create_file(f"{base}/{SLUG}/README.md", readme_md)
create_file(f"{base}/{SLUG}/.gitignore", "__pycache__/\n*.pyc\n.env\n.pytest_cache/\n.mypy_cache/")

# Source Code Structure
src_base = f"{base}/{SLUG}/src/{SLUG}"

# __init__
create_file(f"{src_base}/__init__.py", init_py)

# Domain Layer
create_file(f"{src_base}/domain/__init__.py", "")
create_file(f"{src_base}/domain/models.py", domain_models_py)
create_file(f"{src_base}/domain/exceptions.py", domain_exceptions_py)

# Interface Layer
create_file(f"{src_base}/interfaces/__init__.py", "")
create_file(f"{src_base}/interfaces/repository.py", interfaces_repo_py)

# Application Layer
create_file(f"{src_base}/application/__init__.py", "")
create_file(f"{src_base}/application/services.py", app_services_py)

# Infrastructure Layer
create_file(f"{src_base}/infrastructure/__init__.py", "")
create_file(f"{src_base}/infrastructure/adapters/__init__.py", "")
create_file(f"{src_base}/infrastructure/adapters/memory_repo.py", infra_repo_py)

# Tests
create_file(f"{base}/{SLUG}/tests/__init__.py", "")
create_file(f"{base}/{SLUG}/tests/unit/__init__.py", "")
create_file(f"{base}/{SLUG}/tests/unit/test_service.py", test_service_py)
create_file(f"{base}/{SLUG}/tests/integration/__init__.py", "")

print(f"\n✅ Template generated in: {os.path.abspath(TEMPLATE_DIR)}")
print("Next steps:")
print("1. pip install cookiecutter")
print(f"2. cookiecutter {TEMPLATE_DIR}")
if name == "main": main()


### How to use this

1.  **Generate the Template:**
    Run the python script above. It will create a folder named `cookiecutter-clean-arch`.

2.  **Install Cookiecutter:**
    ```bash
    pip install cookiecutter
    ```

3.  **Create a New Project:**
    Run the command below. It will ask you for a project name and then generate your new project structure based on your strict standards.
    ```bash
    cookiecutter cookiecutter-clean-arch
    ```

### Why this is powerful
* **Instant Onboarding:** New engineers just run this. They don't need to ask "where do I put business logic?"
* **Standards Enforced:** The `STANDARDS.md` is embedded in every new project root.
* **Pre-wired Testing:** The generated project includes unit tests that mock the interface, imme