# Module Priority Decision Matrix

Use this matrix to determine module priority when auto-detection is ambiguous.

## Priority Levels

### Critical (Must Include)
Modules containing core business logic, novel algorithms, or primary research contributions.

**Indicators:**
- Contains domain models (Pydantic)
- Implements core algorithms
- Central to project's purpose
- Files: `core.py`, `engine.py`, `repository.py`, `model.py`

**Examples:**
- Evaluation engine
- Repository pattern implementation
- Detection algorithms
- Core orchestration

---

### High (Should Include)
Modules with significant functionality or orchestration logic.

**Indicators:**
- Business logic implementation
- Orchestration/coordination
- Processing pipelines
- Files: `manager.py`, `processor.py`, `service.py`, `orchestrator.py`

**Examples:**
- Performance monitoring
- Crew generation
- Data processing pipelines

---

### Medium (Consider Including)
Supporting modules with architectural patterns worth documenting.

**Indicators:**
- Factory/Builder patterns
- Adapter implementations
- Configuration management
- Files: `factory.py`, `builder.py`, `adapter.py`, `config.py`

**Examples:**
- LLM factory
- Configuration builders
- Protocol adapters

---

### Low (Usually Exclude)
Pure utility modules without research value.

**Indicators:**
- Helper functions
- Common utilities
- Simple wrappers
- Files: `utils.py`, `helpers.py`, `common.py`, `constants.py`

**Examples:**
- YAML parsers
- String helpers
- Math utilities

---

## Decision Flowchart

```
Does module contain novel algorithms?
├── Yes → CRITICAL
└── No
    ├── Does it orchestrate other modules?
    │   ├── Yes → HIGH
    │   └── No
    │       ├── Does it implement design patterns?
    │       │   ├── Yes → MEDIUM
    │       │   └── No → LOW
```

## Special Cases

| Scenario | Priority | Rationale |
|:---------|:---------|:----------|
| Module with 1 critical file + utils | CRITICAL | Based on highest value file |
| Pure data models (no logic) | HIGH | Models define system architecture |
| Complex factory (>100 LOC) | HIGH | Complexity indicates research value |
| Simple factory (<50 LOC) | MEDIUM | Standard pattern |
| Test helpers | LOW | Never include in paper |
| Example code | LOW | Never include in paper |

## Focus Area Detection

| Pattern Found | Focus Area Tag |
|:--------------|:---------------|
| `class *Repository` | `repository_pattern` |
| `Protocol` classes | `clean_architecture` |
| `*Factory` classes | `factory_pattern` |
| `*Builder` classes | `builder_pattern` |
| MongoDB/Database code | `database_integration` |
| Performance metrics | `performance_monitoring` |
| Statistical functions | `evaluation_algorithms` |
| Weighted calculations | `statistical_grading` |
