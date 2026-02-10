# Amsha Agent System

The **Amsha Agent System** is a portable, plug-and-play AI ecosystem designed for **publication-ready software development**. It automates the full development lifecycle from documentation → testing → implementation → verification, and includes specialized agents for **generating research papers** from your codebase.

---

## 🚀 Quick Start

### Core Orchestrators

| Agent | Trigger | Purpose | Outcome |
|:------|:--------|:--------|:--------|
| **Chatha** | `"Chatha"` | Quality & TDD lifecycle manager | Enforces Stage 0-4 workflow |
| **Mayavi** | `"Mayavi"` or `"Fix it"` | Diagnose & refactor | Identifies issues, delegates fixes |
| **Lutapi** | `"Lutapi, analyze module X for the paper"` | Research paper generator | Publication-ready academic paper |

### Specialist Skills

| Skill | Trigger | Output |
|:------|:--------|:-------|
| **Doc Architect** | `"Document [Feature]"` | Trinity docs (Functional/Technical/Test) |
| **Clean Implementation** | `"Implement [Feature]"` | Pydantic + Clean Architecture code |
| **Test Scaffolder** | `"Create tests for [Feature]"` | Unit + E2E + Integration tests |
| **Compliance Officer** | `"Audit [Feature]"` | Rule violation report |
| **Refactor Agent** | `"Refactor [Feature]"` | Complexity reduction, pattern extraction |
| **Security Scanner** | `"Scan [Feature] for security issues"` | Vulnerability report |

---

## 📄 Research Paper Generation (Phase-Wise)

### Step 1: Generate Configuration
```
"Dakini, generate paper config"
```
**Output:** `.agent/paper_config.yaml` (auto-detected modules)

### Step 2: Analyze Modules (One at a Time)
```
"Lutapi, analyze module crew_forge for the paper"
"Lutapi, analyze module llm_factory for the paper"
"Lutapi, analyze module output_process for the paper"
```
**Output per module:** 5 files (mathematics, architecture, gaps, novelty, summary)

### Step 3: Cross-Module Analysis
```
"Lutapi, run cross-module analysis for the paper"
```
**Output:** 3 files (interactions, dependencies, patterns)

### Step 4: Final Synthesis
```
"Lutapi, synthesize the final journal report"
```
**Output:** `docs/paper/drafts/FINAL_JOURNAL_REPORT.md`

### Check Progress
```
"Lutapi, show paper generation progress"
```

---

## 📂 Directory Structure

```
.agent/
├── README.md (this file)
├── paper_config.yaml (research paper configuration)
├── rules/ (architectural standards)
│   ├── core-standards.md
│   ├── testing-standards.md
│   ├── import-standards.md
│   └── ...
└── skills/ (AI agent implementations)
    ├── chatha/ (orchestrator)
    ├── mayavi/ (refactoring)
    ├── journal-master/ (paper generation orchestrator)
    ├── novelty-analyst/ (academic contribution analysis) ⭐ NEW
    ├── math-extractor/ (algorithm formalization)
    ├── visual-generator/ (diagrams)
    ├── research-gap-analyst/ (technical gaps)
    ├── dakini/ (config generator)
    ├── doc-architect/
    ├── clean-implementation/
    ├── test-scaffolder/
    ├── refactor-agent/
    ├── compliance-officer/
    ├── security-and-pitfalls/
    ├── package-maintainer/
    └── logging-architect/
```

---

## 🧠 Available Skills

### Orchestrators (3)
1. **chatha** - Quality & TDD lifecycle manager
2. **mayavi** - Verification & refactoring orchestrator
3. **journal-master** - Research paper generation orchestrator ⭐ Phase-wise execution

### Paper Publishing (5)
4. **dakini** - Auto-generates `paper_config.yaml`
5. **math-extractor** - Extracts algorithms as LaTeX
6. **visual-generator** - Creates Mermaid diagrams & tables
7. **research-gap-analyst** - Identifies technical gaps (tests, benchmarks, docs)
8. **novelty-analyst** - Identifies academic contributions & suggests research angles ⭐ NEW

### Core Development (4)
9. **doc-architect** - Documentation scaffolding (Trinity structure)
10. **clean-implementation** - Pydantic + Clean Architecture code generation
11. **test-scaffolder** - TDD automation (unit/E2E/integration)
12. **refactor-agent** - Complexity reduction & pattern extraction

### Quality & Infrastructure (4)
13. **compliance-officer** - Rule auditing & enforcement
14. **security-and-pitfalls** - Vulnerability detection
15. **package-maintainer** - Dependency management & PyPI readiness
16. **logging-architect** - Structured logging standards

---

## 🛠️ Example Workflows

### A. Start New Feature
```
User: "Chatha, create a new feature called 'document-processor'"

Chatha: (Orchestrates):
  1. Doc Architect → Creates Trinity docs
  2. Test Scaffolder → Creates failing tests
  3. Clean Implementation → Writes code
  4. Verification → Runs tests & reports
```

### B. Fix Build Issues
```
User: "Mayavi, tests are failing"

Mayavi: (Diagnoses):
  1. Runs verification scripts
  2. Analyzes failure patterns
  3. Delegates to Refactor Agent or Clean Implementation
  4. Re-verifies fix
```

### C. Generate Research Paper (Phase-Wise)
```
Day 1: "Lutapi, analyze module crew_forge for the paper"
Day 2: "Lutapi, analyze module llm_factory for the paper"
Day 3: "Lutapi, analyze module output_process for the paper"
Day 4: "Lutapi, run cross-module analysis for the paper"
Day 5: "Lutapi, synthesize the final journal report"
```

---

## 📜 Configuration Files

| File | Purpose |
|:-----|:--------|
| `paper_config.yaml` | Controls research paper generation (modules, depth, focus areas) |
| `rules/*.md` | Architectural standards enforced by agents |
| `skills/*/SKILL.md` | Detailed skill instructions & usage |

---

## 🎯 Key Features

✅ **Phase-Wise Paper Generation** - Analyze modules incrementally, resume from failures  
✅ **Novelty Analysis** - Identifies academic contributions, suggests research angles  
✅ **TDD Enforcement** - Tests before implementation (Chatha orchestration)  
✅ **Clean Architecture** - Pydantic models, protocol-based DI, strict layering  
✅ **Automatic Auditing** - Compliance Officer enforces all rules  
✅ **Publication-Ready Output** - Scopus-standard research papers with LaTeX & diagrams

---

## 📖 Further Reading

- **Full documentation:** `docs/agent/README.md`
- **Skill details:** `.agent/skills/{skill-name}/SKILL.md`
- **Rules:** `.agent/rules/*.md`
- **Phase-wise commands:** `.agent/skills/journal-master/resources/phase_wise_commands.md`

---

**Version:** 2.0  
**Last Updated:** 2026-02-10  
**Based on:** Nibandha (enhanced for research projects)
