# System Dependency Analysis

## 1. Dependency Graph (Code-Verified)

Every edge verified against actual Python imports. The system has **5 modules** (4 analyzed + `crew_gen`) plus a **shared utility layer**.

```mermaid
%%{init: {'theme': 'base'}}%%
flowchart TD
    classDef core fill:#ff9999,stroke:#333,stroke-width:2px;
    classDef support fill:#99ccff,stroke:#333,stroke-width:2px;
    classDef shared fill:#ffffcc,stroke:#333,stroke-width:2px;
    classDef external fill:#ddd,stroke:#666,stroke-width:1px;

    subgraph "Core Layer (High Efferent Coupling)"
        CF["crew_forge<br/>56 files | Ce=3"]:::core
    end

    subgraph "Support Layer (Low/Zero Efferent Coupling)"
        LLM["llm_factory<br/>14 files | Ce=0 | Ca=2"]:::support
        MON["crew_monitor<br/>7 files | Ce=0 | Ca=1"]:::support
        OUT["output_process<br/>10 files | Ce=1 ⚠️ | Ca=0"]:::support
    end

    subgraph "Consumer Layer"
        GEN["crew_gen<br/>Ce=1"]:::support
    end

    subgraph "Shared Foundation Layer"
        Utils["amsha.utils<br/>(YamlUtils, JsonUtils, Utf8Utils)<br/>Ca=4"]:::shared
    end

    subgraph "External Dependencies"
        CrewAI["crewai"]:::external
        PSUtil["psutil"]:::external
        PyNVML["pynvml"]:::external
        Pandas["pandas"]:::external
        NumPy["numpy"]:::external
        Pydantic["pydantic"]:::external
        DI["dependency-injector"]:::external
        MongoDB["pymongo"]:::external
        Docling["docling"]:::external
    end

    CF -->|"LLMContainer, LLMType<br/>(4 imports)"| LLM
    CF -->|"CrewPerformanceMonitor<br/>(2 imports)"| MON
    GEN -->|"LLMType<br/>(2 imports)"| LLM
    OUT -.->|"CrewParser ⚠️<br/>(1 import, CIRCULAR)"| CF

    CF --> Utils
    LLM --> Utils
    MON --> Utils
    OUT --> Utils

    CF --> CrewAI
    CF --> MongoDB
    CF --> Docling
    CF --> Pydantic
    CF --> DI
    LLM --> CrewAI
    LLM --> Pydantic
    LLM --> DI
    MON --> PSUtil
    MON --> PyNVML
    MON --> Pandas
    OUT --> NumPy
    OUT --> Pandas
```

---

## 2. Coupling Metrics

### 2.1 Instability Analysis

Using Robert Martin's Instability metric: $I = \frac{C_e}{C_a + C_e}$ where:
- $C_e$ = Efferent coupling (outgoing dependencies)
- $C_a$ = Afferent coupling (incoming dependencies)
- $I = 0$ = maximally stable (depended upon); $I = 1$ = maximally unstable (depends on others)

| Module | $C_e$ | $C_a$ | $I$ | Classification |
|:---|:---:|:---:|:---:|:---|
| `crew_forge` | 3 | 1 | 0.75 | **Unstable** — Main consumer, changes propagate |
| `llm_factory` | 0 | 2 | 0.00 | **Maximally Stable** — Pure provider |
| `crew_monitor` | 0 | 1 | 0.00 | **Maximally Stable** — Pure provider |
| `output_process` | 1 | 0 | 1.00 | **Maximally Unstable** — Consumer only |
| `amsha.utils` | 0 | 4 | 0.00 | **Maximally Stable** — Foundation |

### 2.2 Dependency Direction Analysis

```mermaid
%%{init: {'theme': 'base'}}%%
quadrantChart
    title Module Stability vs Abstractness
    x-axis "Concrete" --> "Abstract"
    y-axis "Unstable" --> "Stable"
    quadrant-1 Zone of Uselessness
    quadrant-2 Zone of Stability
    quadrant-3 Zone of Pain
    quadrant-4 Main Sequence
    amsha.utils: [0.8, 0.95]
    llm_factory: [0.4, 0.95]
    crew_monitor: [0.3, 0.95]
    crew_forge: [0.2, 0.25]
    output_process: [0.1, 0.05]
```

---

## 3. Circular Dependency Analysis

### The output_process → crew_forge Cycle

```mermaid
%%{init: {'theme': 'base'}}%%
flowchart LR
    classDef problem fill:#ffcccc,stroke:#f00;

    CF_Orch["crew_forge<br/>Orchestrator Layer"]
    CF_Parser["crew_forge<br/>CrewParser"]:::problem
    OUT_Val["output_process<br/>CrewConfigValidator"]:::problem

    CF_Orch -->|"uses for validation"| OUT_Val
    OUT_Val -->|"imports CrewParser ⚠️"| CF_Parser
```

**Violation:** `output_process` (support layer) imports from `crew_forge` (core layer), creating a **bidirectional dependency**. Support modules should never depend upward on the core.

**Evidence:** [crew_validator.py:L7](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/output_process/validation/crew_validator.py#L7):
```python
from amsha.crew_forge.seeding.parser.crew_parser import CrewParser
```

**Impact:**
- Cannot deploy `output_process` independently without `crew_forge`
- Testing `CrewConfigValidator` requires the entire `crew_forge` module on the import path
- Violates the Dependency Inversion Principle

**Recommended Fix:** Extract `CrewParser` to `amsha.utils.crew_parser` or create a `amsha.common.parsing` module that both can import from.

---

## 4. Architectural Validation Matrix

| Relationship | Expected | Actual | Status | Evidence |
|:---|:---|:---|:---|:---|
| crew_forge → llm_factory | ↓ Downward | ↓ Downward | ✅ Valid | 4 imports in orchestrator layer |
| crew_forge → crew_monitor | ↓ Downward | ↓ Downward | ✅ Valid | 2 imports in orchestrator layer |
| crew_forge → amsha.utils | ↓ Downward | ↓ Downward | ✅ Valid | 6 import sites |
| llm_factory → amsha.utils | ↓ Downward | ↓ Downward | ✅ Valid | 1 import site |
| crew_monitor → amsha.utils | ↓ Downward | ↓ Downward | ✅ Valid | 2 import sites |
| output_process → amsha.utils | ↓ Downward | ↓ Downward | ✅ Valid | 3 import sites |
| output_process → crew_forge | ✗ Forbidden | ↑ **Upward** | ❌ **Violation** | 1 import (CrewParser) |
| crew_gen → llm_factory | ↓ Downward | ↓ Downward | ✅ Valid | 2 imports (LLMType enum only) |

**Result:** 7/8 relationships are architecturally valid. **1 violation** detected.

---

## 5. External Dependency Inventory

| External Library | Used By | Purpose | Version Risk |
|:---|:---|:---|:---|
| `crewai` | crew_forge, llm_factory | Core AI agent framework | High (API changes) |
| `pymongo` | crew_forge | MongoDB repository backend | Low |
| `pydantic` | crew_forge, llm_factory | Data validation & modeling | Medium |
| `dependency-injector` | crew_forge, llm_factory | DI container framework | Low |
| `docling` | crew_forge | Document processing (knowledge) | Medium |
| `psutil` | crew_monitor | CPU/RAM profiling | Low |
| `pynvml` | crew_monitor | NVIDIA GPU profiling | Low (optional) |
| `pandas` | crew_monitor, output_process | Data manipulation & Excel | Low |
| `numpy` | output_process | Statistical calculations | Low |
| `openpyxl` | crew_monitor, output_process | Excel file generation | Low |

**External Dependency Count:** 10 unique libraries across 4 modules.

---

## 6. Recommendations

1. **Break Circular Dependency (P0):** Move `CrewParser` to `amsha.utils.parsing` or `amsha.common.parser`.
2. **Formalize amsha.utils as Foundation Layer:** Document it as the explicit shared dependency layer.
3. **Consider Protocol-Based Decoupling:** Use Python Protocols for `crew_forge` → `crew_monitor` to enable mock-based testing.
4. **Pin External Versions:** `crewai` is highest-risk external dependency (API surface changes frequently).
