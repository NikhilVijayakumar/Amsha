# Journal Master (Lutapi) - Research Paper Orchestrator

**Category:** Orchestrator  
**Type:** Paper Publishing Coordinator  
**Trigger:** `"Lutapi, analyze module {name} for the paper"` (phase-wise) or `"Lutapi, generate complete research paper"` (full pipeline)

---

## Purpose

Journal Master orchestrates the generation of **publication-ready research papers** from your codebase. It coordinates specialized sub-skills, tracks progress, and compiles comprehensive academic reports suitable for Scopus-indexed journals.

---

## Execution Model: Phase-Wise (Recommended)

### Why Phase-Wise?

**Problem:** Analyzing 7+ modules in one session causes failures due to length.  
**Solution:** Break into independent phases that can be executed separately and resumed.

---

## Phase Commands

### Phase 1.x: Module Analysis (One Per Module)

Analyze modules individually:
```
"Lutapi, analyze module crew_forge for the paper"
"Lutapi, analyze module llm_factory for the paper"
"Lutapi, analyze module output_process for the paper"
```

**Per-Module Execution:**
1. Math Extractor → `mathematics.md` (LaTeX algorithms)
2. Visual Generator → `architecture.md` (Mermaid diagrams)
3. Research Gap Analyst → `gaps.md` (technical issues)
4. **Novelty Analyst** → `novelty.md` (academic contributions) ⭐ NEW
5. Summary Generator → `summary.md` (module overview)

**Output:** 5 files in `docs/paper/modules/{module}/`

---

### Phase 2: Cross-Module Analysis

After at least 2 modules are analyzed:
```
"Lutapi, run cross-module analysis for the paper"
```

**Execution:**
1. Interaction Analyzer → `interactions.md` (data flow, dependencies)
2. Dependency Analyzer → `dependencies.md` (module graph)
3. Pattern Analyzer → `patterns.md` (shared design patterns)
4. Novelty Analyst → `novelty.md` (system-level innovations)
5. Math Extractor → `mathematics.md` (cross-module mathematical models)
6. Visual Generator → `architecture.md` (high-level system diagrams)

**Output:** 6 files in `docs/paper/cross_module/`

---

### Phase 3: Cross-Library Analysis

After cross-module analysis is complete or when multiple libraries exist:
```
"Lutapi, run cross-library analysis for the paper"
```

**Execution:**
1. Interaction Analyzer → `interactions.md` (how libraries communicate)
2. Dependency Analyzer → `dependencies.md` (inter-library map)
3. Pattern Analyzer → `patterns.md` (universal architecture patterns)
4. Novelty Analyst → `novelty.md` (macro-level innovations)

**Output:** 4 files in `docs/paper/cross_library/`

---

### Phase 4: Final Synthesis

After cross-library analysis is complete (or if skipped, cross-module):
```
"Lutapi, synthesize the final journal report"
```

**Execution:**
1. Read all module analyses
2. Read cross-module analysis
3. Read cross-library analysis
4. Compile into publication-ready format
5. Generate Abstract, Introduction, Library/Module sections, Discussion, Conclusion
6. Create Appendix (algorithm index, pattern summary)

**Output:** `docs/paper/drafts/FINAL_JOURNAL_REPORT.md` (15-20 pages)

---

### Phase 5: User Input Template Generation ⭐ NEW

After cross-module analysis is complete:
```
"Lutapi, generate user input templates for the paper"
```

**Execution:**
1. Execution Results Template → `docs/paper/Amsha/user_inputs/app_execution_results.md`
   - Suggests relevant metrics and baselines inferred from codebase analysis
   - User fills in actual empirical values
2. Practical Implications Document → `docs/paper/Amsha/user_inputs/practical_implications.md`
   - Auto-generates industry applicability claims with verification checkboxes
   - User reviews, updates, and confirms claims

**Output:** 2 files in `docs/paper/Amsha/user_inputs/`

---

### Progress Tracking

Check what's been completed:
```
"Lutapi, show paper generation progress"
```

**Output:**
```
📊 Paper Generation Progress:
  ✅ Modules Completed: 2/7
  🔄 In Progress: None
  ❌ Failed: None
  📈 Cross-Module: not_started
  📚 Cross-Library: not_started
  📄 Final Report: not_started

💡 Next: "Lutapi, analyze module output_process for the paper"
```

---

## Workflow Example

### Day 1: Configuration
```
"Dakini, generate paper config"
```
Output: `.agent/paper_config.yaml`

### Week 1: Core Modules
```
Day 2: "Lutapi, analyze module crew_forge for the paper"
Day 3: "Lutapi, analyze module llm_factory for the paper"
```

### Week 2: Supporting Modules
```
Day 4: "Lutapi, analyze module output_process for the paper"
Day 5: "Lutapi, analyze module crew_monitor for the paper"
```

### Week 3: Integration
```
Day 6: "Lutapi, run cross-module analysis for the paper"
Day 7: "Lutapi, run cross-library analysis for the paper"
Day 8: "Lutapi, synthesize the final journal report"
```

**Result:** Complete research paper with 10+ algorithms, 12+ diagrams, gap analysis, and novelty assessment.

---

## Output Structure

```
docs/paper/
├── .progress.yaml              # Progress tracker
├── modules/
│   ├── crew_forge/
│   │   ├── mathematics.md      # LaTeX algorithms
│   │   ├── architecture.md     # Mermaid diagrams
│   │   ├── gaps.md            # Technical gaps
│   │   ├── novelty.md         # Academic contributions ⭐
│   │   └── summary.md         # Overview
│   ├── llm_factory/
│   │   └── ... (5 files)
│   └── ... (one dir per module)
├── cross_module/
│   ├── interactions.md        # Data flow & dependencies
│   ├── dependencies.md        # Module graph
│   ├── patterns.md            # Shared patterns
│   ├── novelty.md             # System-level innovations
│   ├── mathematics.md         # Cross-module math models
│   └── architecture.md        # High-level system diagrams
├── cross_library/             # Multi-library mode outputs
│   ├── interactions.md        # How libraries interact
│   ├── dependencies.md        # Macro-level dependencies
│   ├── patterns.md            # System-wide architecture
│   └── novelty.md             # Global innovations
└── drafts/
    └── FINAL_JOURNAL_REPORT.md # Publication-ready paper
```

---

## Sub-Skills Orchestrated

### Analysis Skills (Run Per Module)

1. **Math Extractor** ([docs](math-extractor.md))
   - Scans code for algorithms
   - Generates LaTeX formalization
   - Provides complexity analysis

2. **Visual Generator** ([docs](visual-generator.md))
   - Creates class/sequence/architecture diagrams
   - Generates performance tables
   - Uses Mermaid.js format

3. **Research Gap Analyst** ([docs](research-gap-analyst.md))
   - Identifies technical gaps (tests, benchmarks, docs)
   - Categorizes by severity (critical/moderate/minor)
   - Estimates effort to fix

4. **Novelty Analyst** ([docs](novelty-analyst.md)) ⭐ NEW
   - Classifies module novelty (NOVEL/INCREMENTAL/STANDARD/NONE)
   - Identifies academic contributions
   - Suggests research angles if novelty is weak

### Synthesis Skills (Run Once)

5. **Summary Generator**
   - Creates per-module overview
   - Highlights key findings

6. **Cross-Module Analyzers**
   - Interaction analysis
   - Dependency graphing
   - Pattern extraction

7. **Final Report Compiler**
   - Synthesizes all analyses
   - Generates publication-ready document

---

## Configuration

Controlled by `.agent/paper_config.yaml`:

```yaml
generation:
  mode: modular  # Always use modular for phase-wise
  depth: comprehensive

modules:
  - name: crew_forge
    path: src/nikhil/amsha/crew_forge
    priority: critical
    include_in_final: true  # Set false to skip
    focus_areas:
      - repository_pattern
      - clean_architecture
```

---

## Full Pipeline Command (Advanced)

For smaller projects (< 3 modules), you can run all phases sequentially:
```
"Lutapi, generate complete research paper"
```

**Warning:** May fail on large projects (5+ modules). Use phase-wise execution instead.

---

## Final Report Structure

The generated `FINAL_JOURNAL_REPORT.md` includes:

1. **Title & Abstract**
   - Project overview
   - Key contributions
   - Summary statistics

2. **Introduction**
   - Motivation
   - Problem statement
   - Contributions

3. **Related Work**
   - Comparison with existing frameworks

4. **Architecture & Design**
   - Module-by-module analysis
   - Cross-module interactions
   - Design patterns

5. **Mathematical Foundations**
   - Algorithms with LaTeX
   - Complexity analysis
   - Code references

6. **Experimental Evaluation** (if data available)
   - Performance metrics
   - Benchmarks

7. **Discussion & Limitations**
   - Technical gaps identified
   - Novelty assessment
   - Suggestions for improvement

8. **Conclusion**
   - Summary of contributions
   - Future work

9. **Appendix**
   - Algorithm index
   - Pattern summary
   - Module comparison table

---

## When to Use

Invoke Journal Master when:
- Preparing code for M.Tech/PhD thesis
- Generating research paper for academic publication
- Creating comprehensive technical documentation
- Assessing publication readiness

---

## Related Skills

**Prerequisites:**
- [Dakini](dakini.md) - Generate `paper_config.yaml` first

**Coordinated Skills:**
- [Math Extractor](math-extractor.md)
- [Visual Generator](visual-generator.md)
- [Research Gap Analyst](research-gap-analyst.md)
- [Novelty Analyst](novelty-analyst.md) ⭐

**Quality Assurance:**
- [Chatha](chatha.md) - Ensure code quality before paper generation
- [Mayavi](mayavi.md) - Fix issues identified by gap analysis

---

## Quick Reference

| Command | Phase | Output |
|:--------|:------|:-------|
| `"Lutapi, analyze module X"` | 1.x | 5 files per module |
| `"Lutapi, cross-module analysis"` | 2 | 6 cross-module files |
| `"Lutapi, run cross-library analysis"` | 3 | 4 cross-library files |
| `"Lutapi, synthesize final report"` | 4 | Final overarching journal paper |
| `"Lutapi, generate user input templates"` | 5 | 2 user input template files |
| `"Lutapi, show progress"` | - | Progress status |

---

**Status:** ✅ Active (Phase-Wise Model)  
**Last Updated:** 2026-02-25  
**Version:** 2.0
