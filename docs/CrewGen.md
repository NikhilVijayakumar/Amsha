# CrewGen: Technical Design Specification

**Module:** `nikhil.amsha.crew_gen`
**Version:** 1.0.0
**Dependencies:** `Vak` (Configuration/DI), `Amsha Core` (Orchestration)

## 1\. Executive Summary

**CrewGen** is the meta-programming engine within the Amsha framework. It is an autonomous "Factory" designed to generate, validate, and optimize new CrewAI capabilities (Features) without manual boilerplate coding.

Its core philosophy is **"Twin Generation & Self-Correction"**:

1.  **Twin Generation:** For every request, CrewGen creates two distinct crews: a **Feature Crew** (The Doer) and an **Evaluation Crew** (The Judge).
2.  **Agentic Optimization:** It utilizes an automated feedback loop where the "Judge" critiques the "Doer," and a specialized Optimizer Agent refines the Doer's configuration (`agents.yaml`, `tasks.yaml`) until quality metrics are met.

-----

## 2\. System Architecture

CrewGen sits as a sibling package to the runtime `crew_forge`. It uses `crew_forge` libraries to run its own internal agents but operates independently to manage the file system.

### 2.1 Package Directory Structure

```text
nikhil/amsha/
├── crew_forge/               # [Runtime] Core Orchestrator, Base Classes
└── crew_gen/                 # [Meta-System] The Generator Engine
    ├── __init__.py
    ├── interface.py          # Public Entry Point: run_crewgen()
    ├── application/          # Internal Application Logic
    │   └── crew_gen_app.py   # The Meta-Crew Class
    ├── domain/               # Data Models
    │   ├── blueprint.py      # Schema for generated architectures
    │   └── optimization.py   # Schema for tracking improvement loops
    ├── knowledge/            # "The Golden Standards"
    │   ├── creative_std.md   # Reference: Seed Plot Crew Code
    │   └── evaluation_std.md # Reference: Plot Arc Eval Code
    ├── tools/                # File System Capabilities
    │   └── code_writer.py    # Safe writing to src/ directory
    └── internal_crew/        # The Agents that build Agents
        └── config/
            ├── agents.yaml   # Architect, Engineer, QA, Optimizer
            └── tasks.yaml    # Blueprinting, Coding, Optimizing
```

-----

## 3\. The "Twin" Design Pattern

CrewGen strictly enforces the creation of paired crews to ensure measurable quality.

### 3.1 The Feature Crew ("The Doer")

  * **Purpose:** Execution of the user's desired outcome (e.g., "Write a Novel Chapter", "Analyze Stocks").
  * **Archetype:** `Creative` (High Temperature).
  * **Implementation:** Inherits `AmshaCrewFileApplication`.
  * **Vak Config:** Uses `LLMType.CREATIVE`.
  * **Structure:** Linear pipeline or hierarchical process.

### 3.2 The Evaluation Crew ("The Judge")

  * **Purpose:** Quantifiable validation of the Feature Crew's output.
  * **Archetype:** `Evaluation` (Low Temperature, Deterministic).
  * **Implementation:** Inherits `AmshaCrewFileApplication`.
  * **Vak Config:** Uses `LLMType.EVALUATION`.
  * **Structure:** Iterative Loop (e.g., "For each item in output, score against Rubric X").
  * **Output Requirement:** Must produce valid JSON with `score` (1-10) and `critique`.

-----

## 4\. Operational Workflow

The system operates in three distinct phases managed by `interface.py`.

### Phase 1: Blueprint & Generation

1.  **Ingestion:** User provides `requirements_doc` and `feature_name`.
2.  **Architecting:** The **Solutions Architect** agent analyzes the request and creates a JSON Blueprint defining the file structure for both Twins.
3.  **Synthesis:** The **Senior Python Engineer** agent generates the Python and YAML code into the target `src/` directory.
4.  **Verification:** The **QA Specialist** checks the generated code for *Vak* compliance (e.g., correct `super().__init__` calls, correct imports).

### Phase 2: Human Ground-Truthing (Critical Stop)

  * **Stop Condition:** The system pauses after generation.
  * **User Action:** The user must review the **Evaluation Crew's Rubric** (`tasks.yaml` of the Evaluator).
  * **Logic:** The system cannot optimize if the "Judge" is hallucinating. The user confirms: *"Yes, this is how I want the output measured."*

### Phase 3: The Optimization Loop

The system enters a `while` loop (Default Max: 5 iterations):

1.  **Run Feature:** Execute the Feature Crew dynamically.
      * *Result:* `output_v1.md`
2.  **Run Evaluator:** Feed `output_v1.md` into the Evaluation Crew.
      * *Result:* `{ "score": 6, "critique": "Tone is too casual." }`
3.  **Check Threshold:** If `score >= 9`, **EXIT**.
4.  **Optimize:**
      * The **Config Optimizer** agent reads the *Critique* and the *Documentation*.
      * It modifies the Feature Crew's `agents.yaml` or `tasks.yaml` (e.g., changing Backstory or Goal).
      * **Safety Rule:** It *never* modifies Python code during this phase to prevent runtime crashes.
5.  **Repeat:** Go to Step 1 with the new Configuration.

-----

## 5\. Internal Agents Specification

These agents live in `nikhil/amsha/crew_gen/internal_crew/config/agents.yaml`.

### 5.1 The Solutions Architect

  * **Role:** System Designer.
  * **Goal:** Convert vague requirements into a concrete "Twin" architecture plan.
  * **Key Skill:** Deciding which tasks belong to the "Creative" twin and which belong to the "Evaluation" twin.

### 5.2 The Senior Python Engineer

  * **Role:** Implementation Specialist.
  * **Goal:** Write production-ready Python and YAML.
  * **Constraint:** Must use `Vak` Dependency Injection patterns perfectly. Never hardcodes API keys or models. Uses `_prepare_multiple_inputs_for` in orchestration logic.

### 5.3 The Config Optimizer

  * **Role:** Prompt Engineer / Fine-tuner.
  * **Goal:** Maximize the Evaluation Score.
  * **Tools:** `FileReadTool`, `FileWriteTool`.
  * **Logic:** Reads specific critiques and surgically updates the YAML configuration of the Feature Crew to address them.

-----

## 6\. Public Interface (Python API)

Developers interact with CrewGen via a function call.

```python
# src/nikhil/amsha/crew_gen/interface.py

def run_crewgen(
    feature_name: str,
    requirements: str,
    target_dir: str = "src/impl",
    target_score: int = 8,
    auto_optimize: bool = True
) -> Dict[str, str]:
    """
    Orchestrates the full CrewGen lifecycle.
    
    Args:
        feature_name: The name of the new capability (e.g., 'ChapterWriter').
        requirements: Detailed text description of what the crew should do.
        target_dir: Where to generate the code.
        target_score: The evaluation score (1-10) required to stop optimization.
        auto_optimize: If False, stops after Generation Phase.
        
    Returns:
        Dict containing paths to the final optimized configuration.
    """
    pass
```

-----

## 7\. Success Metrics & Governance

For CrewGen to be considered successful, the generated code must pass these automated checks (The "Meta-Evaluation"):

1.  **Syntax Valid:** Generated Python must compile.
2.  **Vak Compliant:** Must inject `LLMContainer` and pass `LLMType` to the base class.
3.  **Orchestrator Compliant:** Must use standard `Amsha` orchestration methods.
4.  **Separation of Concerns:** Python files must contain *logic*; YAML files must contain *prompts*. The Optimizer agent is strictly forbidden from editing `.py` files.