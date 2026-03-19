# Amsha Agent System Documentation

The **Amsha Agent System** is a comprehensive ecosystem of specialized AI agents designed for **publication-ready software development**. Originally derived from Nibandha, it has been significantly enhanced with **research paper publishing capabilities** for M.Tech/PhD projects.

This system ensures that if you follow the agents' guidance, your code is **Publication-Ready by Default** - meeting academic standards for Scopus-indexed journals.

---

## 🚀 Quick Start Guide

### Core Concept: Specialized Agents (Skills)

Each "skill" is an AI agent with specific expertise. Instead of generic prompts, use **trigger phrases** to activate the right agent for your task.

> 📚 **Writing a Research Paper?** If you are here specifically to generate an ESWA-compliant academic paper from this codebase, please start by reading the **[Research Paper Generation Guide (User Manual)](paper_generation_guide.md)** for an in-depth walkthrough of the `Dakini` -> `Lutapi` -> `Kutusan` workflow.

---

## 🎯 Agent Categories

### 1. Orchestrators (Managing Complex Workflows)

#### Chatha - Quality & TDD Lifecycle Manager
**Trigger:** `"Chatha"` or `"Quality Manager"`

**Purpose:** Enforces the Test-Driven Development lifecycle across 5 stages.

**Stages:**
- Stage 0: Environment Setup
- Stage 1: Documentation (via Doc Architect)
- Stage 2: Test Creation (via Test Scaffolder)
- Stage 3: Implementation (via Clean Implementation)
- Stage 4: Verification & Reporting

**Example:**
```
"Chatha, create a new feature called 'document-processor' with full TDD workflow"
```

**Details:** [chatha.md](skills/chatha.md)

---

#### Mayavi - Verification & Refactoring Orchestrator
**Trigger:** `"Mayavi"` or `"Fix it"` or `"Diagnose the issue"`

**Purpose:** Diagnoses code quality issues and orchestrates fixes via specialized agents.

**Capabilities:**
- Runs verification scripts
- Analyzes hygiene reports
- Identifies architectural drift
- Delegates to Refactor Agent, Clean Implementation, or Test Scaffolder
- Re-verifies after fixes

**Example:**
```
"Mayavi, the build is failing. Please diagnose and fix."
```

**Details:** [mayavi.md](skills/mayavi.md)

---

#### Lutapi (Journal Master) - Research Paper Generator
**Trigger:** `"Lutapi, analyze module {name} for the paper"` (phase-wise) or `"Lutapi, generate complete research paper"` (full pipeline)

**Purpose:** Generates publication-ready research papers from your codebase using phase-wise execution.

**Phase-Wise Workflow (Recommended):**

**Phase 1.x - Per-Module Analysis** (one command per module):
```
"Lutapi, analyze module crew_forge for the paper"
"Lutapi, analyze module llm_factory for the paper"
"Lutapi, analyze module output_process for the paper"
```
Output per module: 5 files (mathematics, architecture, gaps, novelty, summary)

**Phase 2 - Cross-Module Analysis:**
```
"Lutapi, run cross-module analysis for the paper"
```
Output: 6 files (interactions, dependencies, patterns, novelty, mathematics, architecture)

**Phase 3 - Cross-Library Analysis:**
```
"Lutapi, run cross-library analysis for the paper"
```
Output: 4 files (interactions, dependencies, patterns, novelty)

**Phase 4 - Final Synthesis:**
```
"Lutapi, synthesize the final journal report"
```
Output: `docs/paper/drafts/FINAL_JOURNAL_REPORT.md` (15-20 pages)

**Phase 5 - User Input Templates:** ⭐ NEW
```
"Lutapi, generate user input templates for the paper"
```
Output: Smart templates in `docs/paper/Amsha/user_inputs/` — `app_execution_results.md` (guided metrics template) and `practical_implications.md` (auto-generated, user-verified).

**Progress Tracking:**
```
"Lutapi, show paper generation progress"
```

**Why Phase-Wise?** Analyzing all modules in one session can fail. Phase-wise execution allows resuming from any point.

**Details:** [journal-master.md](skills/journal-master.md)

---

### 2. Paper Publishing Agents (5 Specialists)

#### Dakini - Paper Config Generator
**Trigger:** `"Dakini, generate paper config"` or `"Dakini, generate library paper config"` or `"Dakini"`

**Purpose:** Auto-detects modules in your codebase and generates `.agent/paper_config.yaml`.

**Output:**
```yaml
generation:
  mode: modular
  depth: comprehensive

modules:
  - name: crew_forge
    path: src/nikhil/amsha/crew_forge
    priority: critical
    include_in_final: true
```

**Details:** [dakini.md](skills/dakini.md)

---

#### Math Extractor - Algorithm Formalization
**(Invoked by Journal Master - not directly triggered)**

**Purpose:** Scans code for algorithms and converts them to formal LaTeX equations.

**Output:** `docs/paper/modules/{module}/mathematics.md`

**Example Output:**
```latex
$$
\text{findOne}: \mathcal{Q} \rightarrow \mathcal{D} \cup \{\emptyset\}
$$
Complexity: $O(\log n)$ with indexing
```

**Details:** [math-extractor.md](skills/math-extractor.md)

---

#### Visual Generator - Diagram & Metrics Creation
**(Invoked by Journal Master - not directly triggered)**

**Purpose:** Creates Mermaid.js diagrams and performance tables.

**Output:** `docs/paper/modules/{module}/architecture.md`

**Diagram Types:**
- Class diagrams
- Sequence diagrams
- Architecture diagrams
- Component diagrams
- ER diagrams

**Details:** [visual-generator.md](skills/visual-generator.md)

---

#### Research Gap Analyst - Technical Gap Identification
**(Invoked by Journal Master - not directly triggered)**

**Purpose:** Identifies **technical gaps** that block Scopus publication (tests, benchmarks, documentation).

**Output:** `docs/paper/modules/{module}/gaps.md`

**Gap Categories:**
- Critical: No unit tests, no benchmarks
- Moderate: Missing documentation, no Docker setup
- Minor: Code quality issues

**Details:** [research-gap-analyst.md](skills/research-gap-analyst.md)

---

#### Novelty Analyst - Academic Contribution Analysis ⭐ NEW
**(Invoked by Journal Master - not directly triggered)**

**Purpose:** Identifies **academic novelty** and suggests research angles when novelty is weak.

**Output:** `docs/paper/modules/{module}/novelty.md`

**Novelty Classification:**
- **NOVEL:** New algorithms, original patterns
- **INCREMENTAL:** Known techniques in new contexts
- **STANDARD:** Textbook implementations
- **NONE:** Utilities, boilerplate

**Key Feature:** If no novelty found, suggests 3-5 **empirical studies** or **comparative analyses** to strengthen the contribution.

**Example:**
```markdown
## Novelty Classification
**Status:** STANDARD  
**Reason:** Repository pattern is well-established

## Suggested Contributions
1. **Empirical Study:** "Performance Trade-offs: Repository vs. Direct DB Access"
2. **Methodological:** "Protocol-Based DI Framework for Multi-Agent Systems"
3. **Case Study:** "Lessons from Applying Clean Architecture to Python LLM Orchestration"
```

**Details:** `.agent/skills/novelty-analyst/SKILL.md`

---

#### Kutusan - Journal Paper Orchestrator ⭐ NEW
**(Trigger:** `"Kutusan, initialize the final journal report outline"` or `"Kutusan, generate the [Section Name] for the paper"`)

**Purpose:** Manages a 5-stage sequential pipeline (Plan -> Analyze -> Augment -> Draft -> Review) to synthetically draft the `FINAL_JOURNAL_REPORT.md` section by section. It ensures deep intelligence is derived from `Amsha`, `Yantra`, `Bodha`, and `cross_module` integrations.

**Output:** `docs/paper/Amsha/drafts/FINAL_JOURNAL_REPORT.md`

| Agent | Role & Intent | Core Capabilities | Output Target |
| :--- | :--- | :--- | :--- |
| **`kutusan`** | **Paper Orchestrator:** Drives the 5-stage paper generation pipeline (Plan -> Analyze -> Augment -> Draft -> Review). | 11-stage section sequencing, state management, final synthesis. | `docs/paper/Amsha/drafts/FINAL_JOURNAL_REPORT.md` |
| **`paper-planner`** | **Planner:** Translates section goals into executable YAML instructions. | Identifies data sources, defines drafting style, sets ESWA mandatory elements. | `docs/paper/Amsha/drafts/details/[N]. [Section Name]/plan_*.yaml` |
| **`paper-analyzer`** | **Fact Extractor:** Synthesizes architecture, interactions, and gaps across all 4 doc layers. | Traceability, code-to-text translation, gap summarization. | `docs/paper/Amsha/drafts/details/[N]. [Section Name]/analysis_*.md` |
| **`external-researcher`** | **Q1 Academic Scholar:** Augments references and related work. | Finds 2022-2026 Q1 Scopus citations, ESWA-specific relevance, builds comparison tables. | `docs/paper/Amsha/drafts/details/[N]. [Section Name]/augmented_analysis_*.md` |
| **`deep-analyzer`** | **Principal Engineer:** Synthesizes profound architectural trade-offs. | Explains the "Why", enforces mathematical complexity analysis (Big-O, runtime limits). | `docs/paper/Amsha/drafts/details/[N]. [Section Name]/augmented_analysis_*.md` |
| **`paper-drafter`** | **Academic Writer:** Converts analysis into publication-ready prose. | IEEE LaTeX math, Mermaid.js Visual Hierarchy (Logical vs Physical diagrams), Scopus tone. | `docs/paper/Amsha/drafts/details/[N]. [Section Name]/draft_*.md` |
| **`paper-reviewer`** | **Peer Reviewer:** Verifies drafts against the plan and data points. | Anti-hallucination checks, ESWA vocabulary tone enforcement (bans "simple", "easy"). | `docs/paper/Amsha/drafts/details/[N]. [Section Name]/verified_*.md` |
| **`eswa-compliance-checker`** | **Desk Editor:** Verifies global structural benchmarks post-review. | Checks 6,500+ word count, 35-45 refs, 60-70% recency, ESWA citations, statistical tests. | `docs/paper/Amsha/drafts/details/eswa_compliance_report.md` |

---

### 3. Core Development Agents (4 Specialists)

#### Doc Architect - Documentation Scaffolding
**Trigger:** `"Document [Feature]"` or `"Create docs for [Feature]"`

**Purpose:** Creates the Trinity documentation structure (Functional + Technical + Test).

**Output:**
```
docs/features/{feature}/
├── functional/
│   └── README.md (user-facing requirements)
├── technical/
│   └── README.md (architecture & design)
└── test/
    └── README.md (test strategy)
```

**Details:** [doc-architect.md](skills/doc-architect.md)

---

#### Clean Implementation - Pydantic & Clean Architecture
**Trigger:** `"Implement [Feature]"` or `"Write code for [Feature] following Clean Architecture"`

**Purpose:** Writes publication-quality Python code following strict standards.

**Enforces:**
- Pydantic models for all data
- Protocol-based interfaces
- Dependency injection
- Layer separation (Domain/Application/Infrastructure)
- No hardcoded values

**Details:** [clean-implementation.md](skills/clean-implementation.md)

---

#### Test Scaffolder - TDD Automation
**Trigger:** `"Create tests for [Feature]"` or `"Scaffold tests"`

**Purpose:** Generates comprehensive test suites (Unit + E2E + Integration).

**Test Structure:**
```
tests/
├── unit/{feature}/
│   └── test_{component}.py
├── e2e/{feature}/
│   └── test_{scenario}.py
└── integration/{feature}/
    └── test_{workflow}.py
```

**Details:** [test-scaffolder.md](skills/test-scaffolder.md)

---

#### Refactor Agent - Code Quality Improvement
**Trigger:** `"Refactor [Feature]"` or `"Reduce complexity in [Feature]"`

**Purpose:** Identifies architectural drift, complexity spikes, and dependency cycles.

**Capabilities:**
- Extract use cases from bloated classes
- Reduce cyclomatic complexity
- Break dependency cycles
- Apply design patterns

**Details:** [refactor-agent.md](skills/refactor-agent.md)

---

### 4. Quality & Infrastructure (4 Specialists)

#### Compliance Officer - Rule Enforcement
**Trigger:** `"Audit [Feature]"` or `"Check compliance"`

**Purpose:** Ensures adherence to `.agent/rules/*.md`.

**Checks:**
- Absolute imports only
- Pydantic model usage
- Non-interactive configuration
- Naming conventions
- Test coverage

**Details:** [compliance-officer.md](skills/compliance-officer.md)

---

#### Security & Pitfalls - Vulnerability Detection
**Trigger:** `"Scan [Feature] for security issues"`

**Purpose:** Identifies security vulnerabilities and common Python pitfalls.

**Scans For:**
- SQL injection
- Path traversal
- Resource leaks
- Mutable default arguments
- Unsafe eval/exec usage

**Details:** [security-and-pitfalls.md](skills/security-and-pitfalls.md)

---

#### Package Maintainer - PyPI Readiness
**Trigger:** `"Prepare package for PyPI"` or `"Update dependencies"`

**Purpose:** Manages public API exports and dependency tree.

**Capabilities:**
- Generates `__init__.py` exports
- Validates dependency versions
- Ensures PyPI metadata completeness

**Details:** [package-maintainer.md](skills/package-maintainer.md)

---

#### Logging Architect - Structured Logging
**Trigger:** `"Add logging to [Feature]"`

**Purpose:** Ensures consistent, traceable logging using Protocols.

**Standards:**
- Protocol-based logger interfaces
- Structured logging (JSON)
- Correlation IDs
- Log level appropriateness

**Details:** [logging-architect.md](skills/logging-architect.md)

---

## 📋 Complete Agent Reference Table

| # | Agent | Category | Trigger | Output |
|:--|:------|:---------|:--------|:-------|
| 1 | Chatha | Orchestrator | `"Chatha"` | TDD lifecycle enforcement |
| 2 | Mayavi | Orchestrator | `"Mayavi"` | Diagnosis & fix delegation |
| 3 | Lutapi | Orchestrator | `"Lutapi, analyze module X"` | Research paper (phase-wise) |
| 4 | Kutusan | Orchestrator | `"Kutusan, generate X"` | 5-Stage Section Pipeline |
| 5 | Dakini | Paper Publishing | `"Dakini"` | `paper_config.yaml` |
| 6 | Math Extractor | Paper Publishing | (Auto) | LaTeX algorithms |
| 7 | Visual Generator | Paper Publishing | (Auto) | Mermaid diagrams |
| 8 | Research Gap Analyst | Paper Publishing | (Auto) | Technical gaps |
| 9 | Novelty Analyst | Paper Publishing | (Auto) | Academic contribution analysis |
| 10 | Paper Planner | Paper Publishing | (Auto, Kutusan) | Planner config (YAML) |
| 11 | Paper Analyzer | Paper Publishing | (Auto, Kutusan) | Data Synthesis |
| 12 | External Researcher | Paper Publishing | (Auto, Kutusan) | Analysis Augmentation |
| 13 | Deep Analyzer | Paper Publishing | (Auto, Kutusan) | Architectural Synthesis |
| 14 | Paper Drafter | Paper Publishing | (Auto, Kutusan) | Academic Section Draft |
| 15 | Paper Reviewer | Paper Publishing | (Auto, Kutusan) | Section Verification |
| 16 | ESWA Compliance Checker | Paper Publishing | (Auto, Kutusan) | Compliance Report |
| 17 | Doc Architect | Development | `"Document X"` | Trinity docs |
| 18 | Clean Implementation | Development | `"Implement X"` | Pydantic + Clean Arch code |
| 19 | Test Scaffolder | Development | `"Create tests"` | Unit/E2E/Integration tests |
| 20 | Refactor Agent | Development | `"Refactor X"` | Complexity reduction |
| 21 | Compliance Officer | Quality | `"Audit X"` | Rule violation report |
| 22 | Security Scanner | Quality | `"Scan X"` | Vulnerability report |
| 23 | Package Maintainer | Infrastructure | `"Prepare package"` | PyPI readiness |
| 24 | Logging Architect | Infrastructure | `"Add logging"` | Structured logging |

---

## 🛠️ Practical Workflows

### Workflow 1: New Feature Development (TDD)
```bash
Step 1: "Chatha, create feature 'document-analyzer'"
  → Doc Architect creates Trinity docs
  → Test Scaffolder creates failing tests
  → Clean Implementation writes code
  → Verification runs and reports

Step 2: "Compliance Officer, audit 'document-analyzer'"
  → Checks rule adherence

Step 3: "Security Scanner, scan 'document-analyzer'"
  → Identifies vulnerabilities
```

---

### Workflow 2: Fix Failing Build
```bash
Step 1: "Mayavi, diagnose the build failure"
  → Runs verification scripts
  → Identifies root cause (e.g., "Cyclomatic complexity too high")

Step 2: Mayavi delegates to Refactor Agent
  → Refactor reduces complexity

Step 3: Mayavi re-verifies
  → Build passes
```

---

### Workflow 3: Generate Research Paper (Phase-Wise)
```bash
Week 1 - Core Modules:
  Day 1: "Dakini, generate paper config"
  Day 2: "Lutapi, analyze module crew_forge for the paper"
  Day 3: "Lutapi, analyze module llm_factory for the paper"

Week 2 - Supporting Modules:
  Day 4: "Lutapi, analyze module output_process for the paper"
  Day 5: "Lutapi, analyze module crew_monitor for the paper"

Week 3 - Synthesis:
  Day 6: "Lutapi, run cross-module analysis for the paper"
  Day 7: "Lutapi, run cross-library analysis for the paper"
  Day 8: "Lutapi, synthesize the final journal report"

Result: 15-20 page publication-ready paper with:
  - 10+ LaTeX algorithms
  - 12+ Mermaid diagrams
  - Technical gap analysis
  - Academic novelty assessment
  - Suggestions for strengthening contributions
```

---

### Workflow 4: Draft Final Journal Report (Kutusan 5-Stage Pipeline)
```bash
Phase 1: Setup
  "Kutusan, initialize the final journal report outline"
  → Creates `docs/paper/Amsha/drafts/FINAL_JOURNAL_REPORT.md`

Phase 2: Generate Section (e.g., "Related Work")
  - `paper-planner.md`: Generates a detailed YAML plan for the section, defining data sources, academic goals, and ESWA mandatory elements.
  - `paper-analyzer.md`: Scans designated data sources to synthesize raw facts, equations, and diagrams.
  - `external-researcher.md`: Augments references with Q1 Scopus citations (2022-2026), ESWA relevance, and comparison tables.
  - `deep-analyzer.md`: Augments methodology with profound architectural synthesis and formal mathematical complexity analysis.
  - `paper-drafter.md`: Converts facts to academic prose with LaTeX/Mermaid (enforcing Visual Hierarchy).
  - `paper-reviewer.md`: Verifies drafts against data to block hallucination and enforces ESWA vocabulary tone.
  - `eswa-compliance-checker.md`: Validates global structural benchmarks (word count, citation recency, figure density) before final assembly.

Phase 3: Final Synthesis
  "Kutusan, finalize the journal paper"
  → Assembles all verified sections into the final PDF/Markdown
```

---

## 📜 Architectural Rules

The agents enforce these standards (stored in `.agent/rules/`):

| Rule File | Enforces |
|:----------|:---------|
| `core-standards.md` | Naming, layers, environment |
| `testing-standards.md` | Scenario-based testing |
| `import-standards.md` | Absolute imports only |
| `config-enforcement.md` | Pydantic + non-interactive |
| `ddd-structure.md` | Domain-Driven Design layers |
| `creational-patterns.md` | Factory/Builder patterns |
| `logging-standards.md` | Structured logging |
| `manager-rules.md` | Orchestrator behavior |
| `python-env.md` | Virtual environment usage |

---

## 📂 Generated Documentation Structure

After full TDD + Paper generation workflow:

```
project/
├── .agent/ (agent system)
│   ├── README.md
│   ├── paper_config.yaml
│   ├── rules/
│   └── skills/
├── docs/
│   ├── features/ (from Doc Architect)
│   │   └── {feature}/
│   │       ├── functional/README.md
│   │       ├── technical/README.md
│   │       └── test/README.md
│   └── paper/ (from Lutapi)
│       ├── .progress.yaml (progress tracker)
│       ├── Amsha/
│       │   ├── modules/
│       │   │   └── {module}/
│       │   │       ├── mathematics.md
│       │   │       ├── architecture.md
│       │   │       ├── gaps.md
│       │   │       ├── novelty.md ⭐
│       │   │       └── summary.md
│       │   ├── cross_module/
│       │   │   ├── interactions.md
│       │   │   ├── dependencies.md
│       │   │   ├── patterns.md
│       │   │   ├── novelty.md
│       │   │   ├── mathematics.md
│       │   │   └── architecture.md
│       ├── Bodha/
│       ├── Yantra/
│       ├── cross_library/
│       │   ├── interactions.md
│       │   ├── dependencies.md
│       │   ├── patterns.md
│       │   └── novelty.md
│       └── drafts/
│           └── FINAL_JOURNAL_REPORT.md
├── src/ (from Clean Implementation)
├── tests/ (from Test Scaffolder)
└── reports/ (from Verification)
```

---

## 🎯 Key Innovations (vs. Nibandha)

### 1. Phase-Wise Paper Generation
- **Problem:** Analyzing 7+ modules in one session causes failures
- **Solution:** Each module is a separate phase, progress is tracked
- **Benefit:** Resumable, incremental, fault-tolerant

### 2. Novelty Analysis
- **Problem:** Technical gaps identified, but academic contribution unclear
- **Solution:** Separate `novelty-analyst` skill
- **Benefit:** Suggests empirical studies when novelty is weak

### 3. Dual Orchestrators
- **Chatha:** TDD lifecycle (0→4 stages)
- **Mayavi:** Verification & refactoring
- **Benefit:** Separation of concerns

### 4. Comprehensive Paper Publishing
- 5 specialized skills (Dakini, Math Extractor, Visual Generator, Research Gap, Novelty)
- Generates Scopus-ready papers with LaTeX + Mermaid diagrams

---

## 🔗 Further Resources

- **Paper Generation Guide:** `docs/agent/paper_generation_guide.md`
- **Quick commands:** `.agent/skills/journal-master/resources/phase_wise_commands.md`
- **Individual skill docs:** `.agent/skills/{skill-name}/SKILL.md`
- **Rule definitions:** `.agent/rules/*.md`
- **Project README:** `README.md`

---

**System Version:** 2.0  
**Last Updated:** 2026-02-25  
**Based On:** Nibandha (significantly enhanced)  
**Primary Authors:** Amsha Research Team
