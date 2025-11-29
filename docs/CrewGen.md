This is the fully updated **Master Technical Specification** for **CrewGen v1.1.0**.

It incorporates the **Atomic Flow Architecture**, replacing the monolithic internal crew with the modular `Designer` -\> `Generator` -\> `Optimizer` pattern we established.

-----

# 🧬 CrewGen: Technical Design Specification

**Module:** `nikhil.amsha.crew_gen`
**Version:** 1.1.0 (Atomic Flow Architecture)
**Dependencies:** `Vak` (Configuration/DI), `Amsha Core` (Orchestration)

## 1\. Executive Summary

**CrewGen** is the meta-programming engine within the Amsha framework. It functions as an automated "Factory" that manufactures other AI Agents.

Unlike a monolithic generator, CrewGen utilizes a **Micro-Agent Flow Architecture**. It is composed of three atomic, isolated crews (Designer, Generator, Optimizer) orchestrated by a state-aware Flow engine.

Its core philosophy is **"Twin Generation & Self-Correction"**:

1.  **Twin Generation:** It creates two distinct crews for every feature: a **Feature Crew** (The Doer) and an **Evaluation Crew** (The Judge).
2.  **Atomic Isolation:** The design phase is decoupled from the coding phase, allowing for blueprint inspection and manual overrides before code generation.
3.  **Agentic Optimization:** It includes a self-healing loop where the "Judge" critiques the "Doer," and an Optimizer Agent refines the configuration without touching the runtime code.

-----

## 2\. System Architecture

CrewGen sits parallel to the runtime `crew_forge`. It uses `AmshaCrewFileApplication` to run its own internal units but orchestrates them via a dedicated Flow Controller.

### 2.1 Package Directory Structure

The structure is reorganized to support atomic units.

```text
src/nikhil/amsha/crew_gen/
├── __init__.py
├── interface.py            # Public Entry Point
├── domain/
│   └── state.py            # The Pydantic State Protocol
├── flow/
│   └── main_flow.py        # The Flow Orchestrator
├── knowledge/              # Shared "Golden Standards" (Markdown)
├── tools/                  # Shared File System Tools
│   ├── scaffold_tool.py
│   └── code_writer.py
└── units/                  # ATOMIC MICRO-CREWS
    ├── designer/
    │   ├── config/ (agents.yaml, tasks.yaml)
    │   └── crew.py         # Logic: Request -> Blueprint
    ├── generator/
    │   ├── config/ (agents.yaml, tasks.yaml)
    │   └── crew.py         # Logic: Blueprint -> Files
    └── optimizer/
        ├── config/ (agents.yaml, tasks.yaml)
        └── crew.py         # Logic: Files + Critique -> Better Config
```

-----

## 3\. The Flow Protocol (State Management)

To ensure robust communication between atomic units, CrewGen relies on a strict Pydantic State Protocol, not unstructured dictionaries.

### 3.1 The State Object (`CrewGenState`)

Passed through the `main_flow.py`.

  * **`request`**: The initial user input (Name, Description, Paths).
  * **`blueprint`**: The JSON architecture output by the **Designer**.
  * **`generation`**: The file paths and status output by the **Generator**.
  * **`optimization_history`**: A log of scores and changes made by the **Optimizer**.

-----

## 4\. The "Twin" Design Pattern

Regardless of the internal architecture, the *output* of CrewGen remains the "Twin" pattern.

### 4.1 The Feature Crew ("The Doer")

  * **Archetype:** `Creative` (High Temperature).
  * **Structure:** Linear pipeline.
  * **Location:** `{feature_name}/` (Source), `{feature_name}/config/` (YAMLs).

### 4.2 The Evaluation Crew ("The Judge")

  * **Archetype:** `Evaluation` (Low Temperature).
  * **Structure:** Iterative Loop (Rubric-based scoring).
  * **Location:** `{feature_name}_eval/` (Source), `{feature_name}_eval/config/` (YAMLs).
  * **Constraint:** Must produce JSON with `score` (1-10) and `critique`.

-----

## 5\. Operational Workflow (The Flow)

The `CrewGenFlow` controller manages the lifecycle across three phases.

### Phase 1: Design (Unit: Designer)

1.  **Input:** User Description.
2.  **Action:** The **Solutions Architect** agent analyzes the request.
3.  **Output:** A `Blueprint` JSON defining the directory structure and required files.
4.  **Benefit:** This JSON can be inspected or modified by a human before code is written.

### Phase 2: Generation (Unit: Generator)

1.  **Input:** `Blueprint` JSON + `Creative/Evaluation Standards` (Knowledge Base).
2.  **Action:**
      * **Scaffolder Agent:** Uses `AmshaStructScaffolderTool` to build the directory tree.
      * **Engineer Agent:** Uses `AmshaCodeWriterTool` to write Python and YAML files.
3.  **Output:** Files written to disk.

### Phase 3: Validation & Optimization (Unit: Optimizer)

1.  **Ground Truth Check:** User manually verifies the generated Evaluation Rubric.
2.  **The Loop:**
      * Run Feature Crew -\> Get Output.
      * Run Evaluation Crew -\> Get Score.
      * **If Score \< Target:**
          * **Optimizer Agent** reads the critique.
          * **Optimizer Agent** rewrites `agents.yaml` or `tasks.yaml` (Prompts only).
          * **Restarts Loop.**
      * **If Score \>= Target:** Exit.

-----

## 6\. Atomic Units Specification

### Unit A: The Designer

  * **Path:** `units/designer/`
  * **Agent:** `Solutions Architect`
  * **Goal:** Convert vague requirements into a structured `Blueprint`.
  * **Key Behavior:** Decides separation of concerns (what goes into Feature vs. Evaluator).

### Unit B: The Generator

  * **Path:** `units/generator/`
  * **Agent:** `Senior Python Engineer`
  * **Goal:** Execute the Blueprint.
  * **Tools:**
      * `AmshaStructScaffolderTool`: Enforces the "3-Folder Config" (agents/tasks/metrics).
      * `AmshaCodeWriterTool`: writes file content.
  * **Knowledge:** Loads `creative_standard.md` and `evaluation_standard.md`.

### Unit C: The Optimizer

  * **Path:** `units/optimizer/`
  * **Agent:** `Config Optimizer`
  * **Goal:** Improve Agent Performance.
  * **Tools:** `FileReadTool`, `FileWriteTool`.
  * **Safety Rule:** Strictly forbidden from modifying `.py` files. Only modifies YAML configuration to "steer" the LLM.

-----

## 7\. Public Interface

Users interact via a clean Python API that initializes the Flow.

```python
# src/nikhil/amsha/crew_gen/interface.py
from nikhil.amsha.crew_gen.domain.state import CrewGenRequest
from nikhil.amsha.crew_gen.flow.main_flow import CrewGenFlow

def run_crewgen(
    feature_name: str,
    description: str,
    target_dir: str = "src/impl",
    data_dir: str = "data",
    auto_optimize: bool = True
):
    """
    Entry point for the CrewGen Facility.
    """
    # 1. Construct Request Protocol
    request = CrewGenRequest(
        feature_name=feature_name,
        description=description,
        target_directory=target_dir,
        data_directory=data_dir
    )

    # 2. Initialize Flow
    flow = CrewGenFlow()

    # 3. Kickoff
    final_state = flow.kickoff(request)
    
    return final_state
```

-----

## 8\. Success Metrics & Governance

For CrewGen to be considered successful, the generated code must pass these checks:

1.  **Structure Compliance:** Does the output match the `Blueprint`?
2.  **Vak Compliance:** Does the generated Python inject `LLMContainer` correctly?
3.  **Isolation:** Are the Agents, Tasks, and Metrics in their dedicated `config/` subfolders?
4.  **Runnable:** Can the generated twins be instantiated without `ImportError`?