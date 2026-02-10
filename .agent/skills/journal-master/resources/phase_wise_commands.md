# Lutapi Phase-Wise Paper Generation - Quick Reference

## Command Cheat Sheet

### Module Analysis (Phase 1)
```bash
# Analyze individual modules (one at a time - safer!)
"Lutapi, analyze module crew_forge for the paper"
"Lutapi, analyze module llm_factory for the paper"
"Lutapi, analyze module output_process for the paper"
"Lutapi, analyze module crew_monitor for the paper"
"Lutapi, analyze module crew_gen for the paper"
"Lutapi, analyze module execution_runtime for the paper"
"Lutapi, analyze module execution_state for the paper"
```

### Cross-Module Analysis (Phase 2)
```bash
# Run after at least 2 modules are analyzed
"Lutapi, run cross-module analysis for the paper"
```

### Final Synthesis (Phase 3)
```bash
# Combine everything into final report
"Lutapi, synthesize the final journal report"
```

### Progress Tracking
```bash
# Check what's been completed
"Lutapi, show paper generation progress"
```

### Full Pipeline (Risky for large projects)
```bash
# Attempts all phases - may fail after 1-2 modules
"Lutapi, generate complete research paper"
```

---

## Recommended Workflow

### For 7-Module Project (like Amsha):

**Day 1: Core Modules**
1. `"Lutapi, analyze module crew_forge for the paper"`
2. `"Lutapi, analyze module llm_factory for the paper"`

**Day 2: Critical Modules**
3. `"Lutapi, analyze module output_process for the paper"`
4. `"Lutapi, analyze module crew_monitor for the paper"`

**Day 3: Supporting Modules**
5. `"Lutapi, analyze module crew_gen for the paper"`
6. `"Lutapi, analyze module execution_runtime for the paper"`
7. `"Lutapi, analyze module execution_state for the paper"`

**Day 4: Integration**
8. `"Lutapi, run cross-module analysis for the paper"`
9. `"Lutapi, synthesize the final journal report"`

---

## File Structure After Completion

```
docs/paper/
├── .progress.yaml                    # Progress tracker
├── modules/
│   ├── crew_forge/
│   │   ├── mathematics.md           # Algorithms formalized
│   │   ├── architecture.md          # Diagrams
│   │   ├── gaps.md                  # Research gaps
│   │   └── summary.md               # Module overview
│   ├── llm_factory/
│   │   └── ... (same 4 files)
│   └── ... (one dir per module)
├── cross_module/
│   ├── interactions.md              # How modules communicate
│   ├── dependencies.md              # Dependency graph
│   └── patterns.md                  # Shared patterns
└── drafts/
    └── FINAL_JOURNAL_REPORT.md      # Publication-ready paper
```

---

## Configuration File

Edit `.agent/paper_config.yaml` to control which modules are analyzed:

```yaml
modules:
  - name: crew_forge
    path: src/nikhil/amsha/crew_forge
    include_in_final: true       # Set to false to skip
    priority: critical
```

---

## Error Recovery

### If a module analysis fails:
1. Check `docs/paper/.progress.yaml` to see what completed
2. Re-run only the failed module: `"Lutapi, analyze module <name> for the paper"`
3. Continue with remaining modules

### If synthesis fails:
1. Verify all modules are completed: `"Lutapi, show paper generation progress"`
2. Re-run synthesis: `"Lutapi, synthesize the final journal report"`

---

## Expected Output Per Phase

### Module Analysis (~15 min per module)
- **Algorithms:** 3-7 formalized with LaTeX
- **Diagrams:** 3-5 Mermaid diagrams
- **Gaps:** 10-15 research gaps identified
- **Summary:** 1-page overview

### Cross-Module Analysis (~20 min)
- **Interactions:** Data flow + dependency matrix
- **Dependencies:** Module dependency graph
- **Patterns:** Shared design patterns

### Final Synthesis (~15 min)
- **Journal Report:** 15-20 page publication-ready paper
- **Algorithms Index:** Complete algorithm summary
- **Gap Summary:** Prioritized recommendations

---

## Tips for Success

✅ **Do:**
- Analyze modules one at a time
- Wait for each phase to complete before starting the next
- Review outputs after each module
- Check progress regularly

❌ **Don't:**
- Try to analyze all 7 modules in one command
- Skip progress tracking
- Run phases out of order (always Phase 1 → 2 → 3)
- Modify `.progress.yaml` manually (auto-generated)
