This is an excellent architectural constitution. It bridges high-level theory (Clean Architecture) with low-level Python pragmatism (Protocols vs. ABCs, Pydantic).

To adapt this for all your Python projects, we need to **generalize the domain-specific language** (removing "Amsha," "CrewAI," "Agents") while **preserving the structural rules**.

Below is a **Generic Python Engineering Constitution** template. You can drop this file (named `ARCHITECTURE.md` or `STANDARDS.md`) into the root of any new project to establish immediate seniority and structure.

-----

# [Project Name] - Engineering Constitution & Standards

**Role:** You are a Core Contributor/Architect.  
**Goal:** Build software that is loosely coupled, highly cohesive, and easily testable. We adhere strictly to Clean Architecture and SOLID principles.

-----

## 1\. Architectural Boundaries (The "Law")

We follow **Clean Architecture**. The Dependency Rule is absolute: Source code dependencies must point only **inward**, toward high-level policies.

  * **Inner Layers (Domain)** must NEVER depend on **Outer Layers (Infrastructure/API)**.
  * **Domain (`src/project/domain`)**: Pure Python objects (Pydantic models, Enums, Value Objects). **Zero** external framework dependencies (no SQL alchemy, no HTTP clients).
  * **Interfaces (`src/project/interfaces`)**: Abstract contracts defining *what* needs to be done, not *how*.
  * **Application/Use Cases (`src/project/services`)**: Orchestrates business logic using Domain objects and Interfaces.
  * **Infrastructure (`src/project/infrastructure`)**: Concrete implementations (Postgres, Redis, FastAPI, CLI).

**Dependency Flow:**

```
Domain (Entities) ← Interfaces ← Application (Services) ← Infrastructure (Web/DB)
```

-----

## 2\. Interface Design: ABC vs. Protocol

We use Python's typing system to enforce boundaries. We distinguish between **nominal** and **structural** subtyping.

### A. When to Use `ABC` (Abstract Base Class)

**Purpose:** Internal definitions where we control the hierarchy. Strict enforcement.

**Use for:**

  - Repository Interfaces (e.g., `IUserRepository`, `IOrderRepository`)
  - Internal Service Contracts
  - Scenarios requiring `isinstance` checks

**Example:**

```python
from abc import ABC, abstractmethod

class IUserRepository(ABC):
    @abstractmethod
    def get_by_id(self, user_id: str) -> User | None:
        """Contract for retrieving a user."""
        ...
```

### B. When to Use `Protocol`

**Purpose:** Duck typing for external integrations or plugin systems. Flexibility.

**Use for:**

  - Client-facing APIs
  - Callback signatures
  - Adapters where inheritance is messy

**Example:**

```python
from typing import Protocol

class NotifierProtocol(Protocol):
    def send(self, message: str) -> bool:
        """Client implements this; we don't care about the class hierarchy."""
        ...
```

-----

## 3\. Dependency Injection (DI)

**Strict Rule:** No class should instantiate its heavy dependencies.

  * **BAD:** `self.db = PostgresClient()` inside `__init__`.
  * **GOOD:** `self.db: IDatabase` passed as an argument to `__init__`.
  * **Wiring:** Dependencies are wired at the **Entry Point** (main.py, container.py), never inside business logic.

**Example:**

```python
class OrderService:
    # We depend on the Interface, not the implementation
    def __init__(self, repo: IOrderRepository, payment_gateway: IPaymentGateway):
        self.repo = repo
        self.payment = payment_gateway
```

-----

## 4\. SOLID Principles (Python Context)

  * **SRP (Single Responsibility):** A class should have one reason to change.
      * *Split:* `UserRegistry` (Storage) vs. `UserAuthenticator` (Logic).
  * **OCP (Open/Closed):** Add functionality by adding new classes, not by modifying existing ones.
      * *Pattern:* Use Strategy pattern for varying algorithms (e.g., `PricingStrategy`).
  * **LSP (Liskov Substitution):** A subclass/implementation must not break the code that uses the base class.
      * *Rule:* Do not raise `NotImplementedError` in a concrete class for a method defined in the Interface.
  * **ISP (Interface Segregation):** Many specific interfaces are better than one general-purpose interface.
      * *Prefer:* `IReadable`, `IWritable` over `IGenericDataAccess`.
  * **DIP (Dependency Inversion):** Depend on abstractions (Interfaces), not concretions (Classes).

-----

## 5\. Exception Handling Strategy

Stop raising `ValueError` or `Exception`. We need semantic errors.

1.  **Define a Project Base Exception:**

    ```python
    class ProjectNameException(Exception):
        """Root exception for the project."""
        pass
    ```

2.  **Define Domain-Specific Exceptions:**

    ```python
    class ResourceNotFoundException(ProjectNameException):
        """Raised when an entity is missing."""
        def __init__(self, resource_id: str):
            super().__init__(f"Resource {resource_id} not found.")
    ```

3.  **Infrastructure Wrapping:**

      * Catch `OperationalError` (SQL) or `ConnectTimeout` (HTTP) in the Adapter layer.
      * Re-raise as `RepositoryException` or `ServiceUnavailableException`.
      * **Result:** The Domain layer never knows we are using SQL or HTTP.

-----

## 6\. Async/Await Guidelines

  * **I/O Bound:** Use `async/await` (Database queries, API calls, File I/O).
  * **CPU Bound:** Use synchronous code (Data processing, Image manipulation, heavy math).
  * **Mixing:** If you must call Sync from Async, use `run_in_executor`.

-----

## 7\. Public API & Data Transfer

**Rule:** The communication boundary must be explicit.

### DTOs (Data Transfer Objects)

  * Use **Pydantic** `BaseModel` for all data moving between layers or out to the user.
  * **Immutable:** Prefer `frozen=True` where possible.
  * **Validation:** Validation logic belongs in the Pydantic model validators, not in the controller/view.

**Example:**

```python
class CreateUserRequest(BaseModel):
    username: str
    email: EmailStr
    
    model_config = ConfigDict(frozen=True)
```

-----

## 8\. Versioning & Backward Compatibility

**Scheme:** Semantic Versioning (MAJOR.MINOR.PATCH).

  * **MAJOR:** Breaking API changes.
  * **MINOR:** New features, backwards compatible.
  * **PATCH:** Bug fixes.

**Deprecation:**
Never delete a public method immediately.

1.  Add `@deprecated` warning.
2.  Wait for one MINOR cycle.
3.  Remove in next MAJOR cycle.

-----

## 9\. Testing Standards

Code without tests is technical debt.

### Pyramid Structure

1.  **Unit Tests (80%):** Test Domain and Services. Mock **all** Interfaces. Fast execution.
2.  **Integration Tests (15%):** Test Repositories with real DB (via Docker/Testcontainers).
3.  **E2E Tests (5%):** Test the full flow from Entry Point to Output.

### Mocking Rule

Mock the **Interface**, not the **Implementation**.

```python
# GOOD
mock_repo = Mock(spec=IUserRepository) 

# BAD
mock_repo = Mock(spec=PostgresUserRepository)
```

-----

## 10\. Dependency Management

**Application vs. Library:**

  * **If building a Library:**

      * `pyproject.toml` (`[project].dependencies`): Minimal, loose versions (`>=1.0`).
      * `requirements.txt` (Dev): Pinned versions (`==1.2.3`) for reproducible CI/CD.

  * **If building an Application:**

      * Use `poetry`, `uv`, or `pip-tools` to lock **all** dependencies to exact hashes.

-----

## Quick Reference Checklist

Before merging a PR, verify:

  - [ ] **Layers:** Did I import Infrastructure code into the Domain? (If yes, fix it).
  - [ ] **Types:** Are Type Hints present on all arguments and returns?
  - [ ] **Tests:** Did I write a Unit Test for the business logic?
  - [ ] **Exceptions:** Am I raising a generic `Exception`? (If yes, create a custom one).
  - [ ] **Secrets:** Are there hardcoded secrets? (If yes, move to ENV variables).

-----

### How to use this for *your* projects

1.  **Copy this text** into a file named `STANDARDS.md` in your project root.
2.  **Replace** `[Project Name]` with your actual project name.
3.  **Adjust Section 10** based on whether you are building a Library (pip installable) or an App (Docker/Service).
4.  **Enforce it:** Make reading this file part of the onboarding for any new developer (or AI agent) working on the code.

Copy the code below into a file named create_template.py.

Run it: python create_template.py.

It will create a folder named cookiecutter-clean-arch.

Run cookiecutter against it (instructions at the bottom).