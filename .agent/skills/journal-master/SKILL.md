---
name: journal-master
description: The orchestrator. It coordinates math-extractor, visual-generator, and research-gap-analyst skills to compile a comprehensive research paper. Supports both unified (whole-project) and modular (per-module) analysis modes controlled by .agent/paper_config.yaml.
---

# Journal Master Skill (Lutapi)

## Purpose
This skill acts as the orchestrator for generating complete research papers. It manages the execution of three sub-skills, aggregates their outputs, verifies consistency, and produces the final publication-ready report.

## Modes of Operation

### 1. Unified Mode (Quick)
Analyzes the entire project at once. Best for initial drafts or when time is limited.

**Output:** 3 documents (mathematics, architecture, gaps) + 1 final report

### 2. Modular Mode (Comprehensive) ⭐ **Recommended**
Analyzes each module separately for maximum depth and detail coverage. Controlled by `.agent/paper_config.yaml`.

**Output:** N modules × 4 documents (math, arch, gaps, summary) + cross-module analysis + 1 final report

**Configuration File:** `.agent/paper_config.yaml`

```yaml
generation:
  mode: modular              # 'modular' or 'unified'
  depth: comprehensive       # 'summary', 'standard', 'comprehensive'

modules:
  - name: crew_forge
    path: src/nikhil/amsha/crew_forge
    include_in_final: true   # Set false to exclude from final paper
    priority: critical
  # ... more modules
```

## Phase-Wise Execution Model ⭐ **Recommended**

To prevent failures during long analysis sessions, the workflow is broken into **independent phases**. Each phase can be executed separately and resumed if interrupted.

### Phase Execution Commands

**Phase 1.x - Per-Module Analysis** (one phase per module):
```
"Lutapi, analyze module crew_forge for the paper"
"Lutapi, analyze module llm_factory for the paper"
"Lutapi, analyze module output_process for the paper"
```

**Phase 2 - Cross-Module Analysis:**
```
"Lutapi, run cross-module analysis for the paper"
```

**Phase 3 - Cross-Library Analysis:**
```
"Lutapi, run cross-library analysis for the paper"
```

**Phase 4 - Final Synthesis:**
```
"Lutapi, synthesize the final journal report"
```

**Or run all phases sequentially:**
```
"Lutapi, generate complete research paper" (attempts all phases)
```

---

## Detailed Phase Breakdown

### Phase 1.x: Module Analysis (Per Module)

**Trigger:** "Lutapi, analyze module {module_name} for the paper"

**Input:** `.agent/paper_config.yaml` (reads module configuration)

**Process:**
1. **Math Extractor** → `docs/paper/Amsha/modules/{module}/mathematics.md`
   - Extract algorithms specific to this module
   - Minimum 1 algorithm per module
   - LaTeX formalization with variable mapping

2. **Visual Generator** → `docs/paper/Amsha/modules/{module}/architecture.md`
   - Module-specific class/sequence diagrams
   - Minimum 2 diagrams per module
   - Performance tables if applicable

3. **Research Gap Analyst** → `docs/paper/Amsha/modules/{module}/gaps.md`
   - Module-specific gaps against Scopus standards
   - Categorized by severity (critical/moderate/minor)
   - Effort estimation for each gap

4. **Novelty Analyst** → `docs/paper/Amsha/modules/{module}/novelty.md` ⭐ **NEW**
   - Academic contribution analysis
   - Novel vs. standard classification
   - Suggests research angles if novelty is weak
   - Proposes empirical studies to strengthen contribution

5. **Summary Generator** → `docs/paper/Amsha/modules/{module}/summary.md`
   - Quick overview of module findings
   - Key metrics and highlights

**Output:** 5 files in `docs/paper/Amsha/modules/{module}/`

**Status Tracking:** Updates `docs/paper/Amsha/.progress.yaml` with completion status

---

### Phase 2: Cross-Module Analysis

**Trigger:** "Lutapi, run cross-module analysis for the paper"

**Prerequisites:** At least 2 modules must be analyzed in Phase 1

**Process:**
1. **Interaction Analyzer** → `docs/paper/Amsha/cross_module/interactions.md`
   - How modules communicate
   - Data flow diagrams
   - Dependency matrix

2. **Dependency Analyzer** → `docs/paper/Amsha/cross_module/dependencies.md`
   - Module dependency graph (Mermaid)
   - Coupling analysis
   - Architectural layer validation

3. **Pattern Analyzer** → `docs/paper/Amsha/cross_module/patterns.md`
   - Recurring architectural patterns
   - Shared design principles
   - Protocol compliance

4. **Novelty Analyst** → `docs/paper/Amsha/cross_module/novelty.md`
   - System-level innovations (e.g., hybrid orchestration)
   - Synergy between modules (e.g., dynamic crew generation + validation)
   - Comparison with existing multi-agent frameworks

5. **Math Extractor** → `docs/paper/Amsha/cross_module/mathematics.md`
   - System-wide mathematical models
   - Cross-module algorithmic dependencies
   - Global complexity analysis

6. **Visual Generator** → `docs/paper/Amsha/cross_module/architecture.md`
   - High-level system architecture diagrams
   - End-to-end data flow (Amsha to Yantra)
   - Global performance metrics

**Output:** 6 files in `docs/paper/Amsha/cross_module/`

---

### Phase 3: Cross-Library Analysis

**Trigger:** "Lutapi, run cross-library analysis for the paper"

**Prerequisites:** 
- Phase 2 completed (cross-module analysis) OR
- Multiple libraries detected in `docs/paper/`

**Process:**
1. **Library Interaction Analyzer** → `docs/paper/cross_library/interactions.md`
   - How libraries (Amsha, Bodha, Yantra) interact with each other
   - High-level system architecture diagrams
2. **Library Dependency Analyzer** → `docs/paper/cross_library/dependencies.md`
   - Dependency graph mapping shared layers
3. **Library Pattern Analyzer** → `docs/paper/cross_library/patterns.md`
   - Universal patterns spanning across libraries
4. **Library Novelty Analyst** → `docs/paper/cross_library/novelty.md`
   - Macro-level innovations across the entire suite of libraries

**Output:** 4 files in `docs/paper/cross_library/`

---

### Phase 4: Final Synthesis

**Trigger:** "Lutapi, synthesize the final journal report"

**Prerequisites:** 
- Phase 1 completed for at least 2 modules
- Phase 2 completed (cross-module analysis)
- Phase 3 completed (cross-library analysis, if applicable)

**Process:**
1. Read all module analyses from `docs/paper/Amsha/modules/*/` (and other libraries)
2. Read cross-module analysis from `docs/paper/Amsha/cross_module/`
3. Read cross-library analysis from `docs/paper/cross_library/`
4. Compile into publication-ready format
5. Generate:
   - Abstract
   - Introduction
   - Library-by-library analysis sections
   - Cross-Library insights
   - Experimental evaluation (if data available)
   - Discussion & Limitations
   - Conclusion
   - Appendix (algorithm index, pattern summary)

**Output:** `docs/paper/drafts/FINAL_JOURNAL_REPORT.md`

---

### Phase 5: User Input Template Generation

**Trigger:** "Lutapi, generate user input templates for the paper"

**Prerequisites:** Phase 2 completed (cross-module analysis)

**Purpose:** Auto-generates intelligent, data-aware templates in `docs/paper/Amsha/user_inputs/` for sections that require user-provided data. These templates are pre-filled with insights inferred from existing analysis.

**Process:**
1. **Execution Results Template** → `docs/paper/Amsha/user_inputs/app_execution_results.md`
   - Reads `mathematics.md`, `novelty.md`, and `gaps.md` across all libraries
   - Suggests relevant metrics (F1, Precision, Recall) and baselines (Drain, Spell)
   - Suggests experiment structures (chunk size sensitivity, noise injection)
   - User fills in actual empirical values

2. **Practical Implications Document** → `docs/paper/Amsha/user_inputs/practical_implications.md`
   - Reads `paper_config.yaml` (via Dakini), `architecture.md`, and `novelty.md`
   - **Auto-generates** industry applicability, cost/efficiency claims, and deployment considerations
   - Each claim has a verification checkbox for user to confirm (✅) or reject (❌)
   - User reviews, updates, and adds their own observations

**Output:** 2 files in `docs/paper/Amsha/user_inputs/`

## Configuration Reference

### Module Definition

```yaml
modules:
  - name: module_name          # Required: Short identifier
    path: src/path/to/module   # Required: Source directory
    description: "..."         # Optional: Module purpose
    priority: critical         # Optional: critical|high|medium|low
    include_in_final: true     # Required: Include in final paper?
    focus_areas:               # Optional: Specific areas to emphasize
      - repository_pattern
      - clean_architecture
```

### Exclusion Options

```yaml
# Exclude a module from final report (but still analyze it)
modules:
  - name: utils
    include_in_final: false

# Skip certain file types during analysis
exclusions:
  skip_test_files: true
  skip_example_files: true
  skip_init_files: true
```

### Quality Thresholds

```yaml
quality:
  min_latex_equations: 10      # Across all modules
  min_diagrams: 12             # Total diagrams required
  min_identified_gaps: 15      # Minimum gaps to identify
```

## Instructions for Phase Execution

### Step 1: Detect Phase from User Request

**Pattern Matching:**
```python
user_request = input_message.lower()

if "analyze module" in user_request:
    # Extract module name from request
    module_name = extract_module_name(user_request)
    phase = f"MODULE_ANALYSIS_{module_name}"
elif "cross-module" in user_request:
    phase = "CROSS_MODULE_ANALYSIS"
elif "cross-library" in user_request:
    phase = "CROSS_LIBRARY_ANALYSIS"
elif "synthesize" in user_request or "final report" in user_request:
    phase = "FINAL_SYNTHESIS"
else:
    # Default: try to run all phases sequentially
    phase = "FULL_PIPELINE"
```

### Step 2: Load Configuration

```python
config = load_yaml('.agent/paper_config.yaml')
modules = [m for m in config['modules'] if m['include_in_final']]
```

### Step 3: Execute Appropriate Phase

#### Phase 1.x: Module Analysis

```python
if phase.startswith("MODULE_ANALYSIS_"):
    module_name = phase.split("_")[-1]
    module_config = find_module(modules, module_name)
    
    if not module_config:
        raise ValueError(f"Module '{module_name}' not found in paper_config.yaml")
    
    # Execute sub-skills for this module only
    run_math_extractor(module_config['path'], f"docs/paper/Amsha/modules/{module_name}/mathematics.md")
    run_visual_generator(module_config['path'], f"docs/paper/Amsha/modules/{module_name}/architecture.md")
    run_research_gap_analyst(module_config['path'], f"docs/paper/Amsha/modules/{module_name}/gaps.md")
    run_novelty_analyst(module_config['path'], f"docs/paper/Amsha/modules/{module_name}/novelty.md")
    generate_module_summary(module_name, f"docs/paper/Amsha/modules/{module_name}/summary.md")
    
    # Update progress tracker
    update_progress(module_name, status="completed")
```

#### Phase 2: Cross-Module Analysis

```python
elif phase == "CROSS_MODULE_ANALYSIS":
    completed_modules = get_completed_modules()
    
    if len(completed_modules) < 2:
        raise ValueError("Need at least 2 modules analyzed before cross-module analysis")
    
    # Analyze interactions and global architecture
    analyze_module_interactions(completed_modules, "docs/paper/Amsha/cross_module/interactions.md")
    analyze_dependencies(completed_modules, "docs/paper/Amsha/cross_module/dependencies.md")
    analyze_patterns(completed_modules, "docs/paper/Amsha/cross_module/patterns.md")
    analyze_cross_module_novelty(completed_modules, "docs/paper/Amsha/cross_module/novelty.md")
    run_math_extractor_cross_module(completed_modules, "docs/paper/Amsha/cross_module/mathematics.md")
    run_visual_generator_cross_module(completed_modules, "docs/paper/Amsha/cross_module/architecture.md")
    
    update_progress("cross_module", status="completed")
```

#### Phase 3: Cross-Library Analysis

```python
elif phase == "CROSS_LIBRARY_ANALYSIS":
    library_config = load_yaml('.agent/library_config.yaml')
    libraries = library_config['libraries']
    
    # Analyze library interactions
    analyze_library_interactions(libraries, "docs/paper/cross_library/interactions.md")
    analyze_library_dependencies(libraries, "docs/paper/cross_library/dependencies.md")
    analyze_library_patterns(libraries, "docs/paper/cross_library/patterns.md")
    analyze_library_novelty(libraries, "docs/paper/cross_library/novelty.md")
    
    update_progress("cross_library", status="completed")
```

#### Phase 4: Final Synthesis

```python
elif phase == "FINAL_SYNTHESIS":
    progress = load_progress()
    
    if not progress.get("cross_module") == "completed":
        raise ValueError("Cross-module analysis must be completed first")
    
    # Compile all analyses
    synthesize_final_report(
        module_analyses=glob("docs/paper/*/modules/*/"),
        cross_module_dir="docs/paper/*/cross_module/",
        cross_library_dir="docs/paper/cross_library/",
        output="docs/paper/drafts/FINAL_JOURNAL_REPORT.md"
    )
    
    update_progress("final_report", status="completed")
```

#### Full Pipeline (Sequential Execution)

```python
elif phase == "FULL_PIPELINE":
    # Phase 1: Analyze all modules
    for module in modules:
        execute_phase(f"MODULE_ANALYSIS_{module['name']}")
    
    # Phase 2: Cross-module
    execute_phase("CROSS_MODULE_ANALYSIS")
    
    # Phase 3: Synthesis
    execute_phase("FINAL_SYNTHESIS")
```

#### Progress Checking

```python
elif "show progress" in user_request or "check progress" in user_request:
    progress = load_yaml("docs/paper/Amsha/.progress.yaml")
    
    # Display current status
    modules_completed = [m for m, data in progress['modules'].items() if data['status'] == 'completed']
    modules_in_progress = [m for m, data in progress['modules'].items() if data['status'] == 'in_progress']
    modules_failed = [m for m, data in progress['modules'].items() if data['status'] == 'failed']
    
    print(f"📊 Paper Generation Progress:")
    print(f"  ✅ Modules Completed: {len(modules_completed)}/{progress['stats']['total_modules']}")
    print(f"  🔄 In Progress: {', '.join(modules_in_progress) if modules_in_progress else 'None'}")
    print(f"  ❌ Failed: {', '.join(modules_failed) if modules_failed else 'None'}")
    print(f"  📈 Cross-Module: {progress['cross_module']['status']}")
    print(f"  📚 Cross-Library: {progress['cross_library']['status']}")
    print(f"  📄 Final Report: {progress['final_report']['status']}")
    
    # Recommend next step
    if len(modules_completed) == progress['stats']['total_modules'] and progress['cross_module']['status'] != 'completed':
        print("\n💡 Next: Run cross-module analysis")
    elif progress['cross_module']['status'] == 'completed' and progress['cross_library']['status'] != 'completed':
        print("\n💡 Next: Run cross-library analysis")
    elif progress['cross_library']['status'] == 'completed' and progress['final_report']['status'] != 'completed':
        print("\n💡 Next: Synthesize final journal report")
```

### Step 3: Verification

**Cross-Check Consistency:**
- Verify variable names in math match code
- Ensure diagrams reflect actual module structure
- Validate that all gaps are code-verified
- Check for duplicate content across modules

**Quality Checks:**
- Meet minimum thresholds from config
- All code references are valid file paths
- All LaTeX equations render correctly
- All Mermaid diagrams are syntactically valid

### Step 4: Synthesis

**Deduplication:**
- Merge duplicate gaps across modules
- Combine similar architectural patterns
- Cross-reference related algorithms

**Structure:**
```markdown
# Final Paper Structure (Multi-Library Mode)

1. Abstract
2. Introduction
3. Related Work
4. Library Overviews:
   - 4.1 Amsha Framework
   - 4.2 Bodha Engine
   - 4.3 Yantra Core
5. Cross-Library Interactions
6. System-Level Performance
7. Discussion & Future Work
8. Conclusion
9. Appendix
```

### Step 5: Output

Generate `docs/paper/drafts/FINAL_JOURNAL_REPORT.md` with:
- All library modules integrated
- Cross-module insights
- Cross-library interactions
- Comprehensive appendix
- Traceability matrix

## Example Usage

### Phase-Wise Execution (Recommended)

**Step 1: Analyze first module**
```
"Lutapi, analyze module crew_forge for the paper"
```
Output: `docs/paper/Amsha/modules/crew_forge/{mathematics,architecture,gaps,summary}.md`

**Step 2: Analyze second module**
```
"Lutapi, analyze module llm_factory for the paper"
```
Output: `docs/paper/Amsha/modules/llm_factory/{mathematics,architecture,gaps,summary}.md`

**Step 3: Continue for remaining critical modules**
```
"Lutapi, analyze module output_process for the paper"
"Lutapi, analyze module crew_monitor for the paper"
```

**Step 4: Cross-module analysis**
```
"Lutapi, run cross-module analysis for the paper"
```
Output: `docs/paper/Amsha/cross_module/{interactions,dependencies,patterns,novelty,mathematics,architecture}.md`

**Step 5: Cross-library analysis**
```
"Lutapi, run cross-library analysis for the paper"
```
Output: `docs/paper/cross_library/{interactions,dependencies,patterns,novelty}.md`

**Step 6: Final synthesis**
```
"Lutapi, synthesize the final journal report"
```
Output: `docs/paper/drafts/FINAL_JOURNAL_REPORT.md`

### Resumable Workflow

If any phase fails, you can resume from the last completed phase:

```
# Check progress
"Lutapi, show paper generation progress"

# Resume from next incomplete module
"Lutapi, analyze module execution_runtime for the paper"
```

### Full Pipeline (Advanced Users)

```
"Lutapi, generate complete research paper"
```
Attempts all phases sequentially. **Warning:** May fail on large projects with 5+ modules.

## Verification Requirements

**Per Module:**
- ✅ All mathematical entities have source code references
- ✅ All diagrams accurately reflect module structure
- ✅ All gaps are verified against actual code (no assumptions)
- ✅ Complexity analysis provided for algorithms

**Cross-Module:**
- ✅ Module interaction diagrams show actual data flow
- ✅ Dependency analysis reflects real import relationships
- ✅ Pattern identification is evidence-based

**Final Report:**
- ✅ Variable naming consistency (math ↔ code)
- ✅ No duplicate content
- ✅ All external references valid
- ✅ Meets publication quality standards

## Output Directory Structure

```
docs/paper/
├── Amsha/
│   ├── modules/
│   │   ├── crew_forge/
│   │   │   ├── mathematics.md
│   │   │   ├── architecture.md
│   │   │   ├── gaps.md
│   │   │   └── summary.md
│   │   ├── output_process/
│   │   │   └── ...
│   ├── cross_module/
│   │   ├── interactions.md
│   │   ├── dependencies.md
│   │   └── patterns.md
│   └── ...
├── Bodha/
│   └── ...
├── Yantra/
│   └── ...
├── cross_library/
│   ├── interactions.md
│   ├── dependencies.md
│   ├── patterns.md
│   └── novelty.md
└── drafts/
    └── FINAL_JOURNAL_REPORT.md   # Final compiled overarching paper
```

## Benefits of Modular Mode

1. **Deeper Analysis** - Full attention on each module's specifics
2. **No Missed Details** - Comprehensive coverage of all components
3. **Better Organization** - Clear separation of concerns
4. **Easier Review** - Can review/approve module-by-module
5. **Incremental Progress** - Can pause/resume between modules
6. **Selective Inclusion** - Exclude utility/support modules from final paper

## Tips for Best Results

- Use **modular mode** for M.Tech/PhD thesis-level depth
- Use **unified mode** for conference papers or quick drafts
- Set `depth: comprehensive` for maximum detail
- Exclude `utils` or helper modules if they're not research-worthy
- Review per-module outputs before final synthesis
- Adjust quality thresholds based on journal requirements

## Supporting Materials

### Resources
- **[paper_template.md](resources/paper_template.md)** - Complete research paper structure template with sections for abstract, introduction, related work, module analyses, cross-module analysis, experimental evaluation, discussion, future work, conclusion, and appendices. Includes formatting guidelines for equations, figures, tables, and citations.

### Examples
- **[final_paper_example.md](examples/final_paper_example.md)** - Full example of a final journal report for the Amsha project showing how all sub-skill outputs are synthesized into a cohesive academic paper with proper LaTeX equations, Mermaid diagrams, performance tables, and gap analysis integration.

## Quality Indicators

When using these materials:
- **Structure:** Follow the 9-section template (Abstract → Conclusion → Appendices)
- **Integration:** Each module analysis includes math, architecture, and implementation sections
- **Cross-References:** Use "See Section X.Y" and "Figure X.Y" liberally
- **Verification:** Include Appendix with automated checks performed and manual verification required
- **Traceability:** Every claim must reference source files (file:///path/to/file.py)
