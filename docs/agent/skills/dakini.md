# Dakini (Paper Config Generator)

**Role:** CONFIGURATOR - Automatically generates `paper_config.yaml` by intelligently detecting and analyzing modules in your codebase.

## Activation Triggers
- `"Dakini"` or `"dakini"`
- `"Generate paper config"`
- `"Create paper configuration"`

## Purpose
Dakini eliminates the manual work of creating paper generation configurations. It scans your source code, detects modules, analyzes their purpose and importance, and produces a comprehensive `paper_config.yaml` ready for use with Journal Master.

## What It Does

### 1. Auto-Detection
Scans your `src/` directory to find all modules:
- Filters out non-module directories
- Requires minimum 2 Python files per module
- Excludes test and cache directories

### 2. Intelligent Analysis
For each module, determines:
- **Priority**: Critical, High, Medium, or Low
  - Based on file names, patterns, and architectural significance
- **Description**: Extracted from docstrings or inferred from structure
- **Focus Areas**: Detected patterns like `repository_pattern`, `factory_pattern`, `clean_architecture`
- **Inclusion**: Whether to include in final paper (auto-determined by priority)

### 3. Smart Configuration
Generates a complete `paper_config.yaml` with:
- Module specifications sorted by priority
- Processing order optimized for comprehension
- Quality thresholds scaled to module count
- All recommended settings pre-configured

## Example Usage

**Generate Fresh Config:**
```
"Dakini, create the paper config."
```

**Regenerate (with backup):**
```
"Dakini, regenerate paper config."
```

Dakini will:
1. Scan `src/nikhil/amsha/` for modules
2. Analyze each module's purpose and patterns
3. Generate `.agent/paper_config.yaml`
4. Display summary of detected modules
5. Suggest next steps

## Output

**File:** `.agent/paper_config.yaml`

**Summary Display:**
```
✅ Generated paper_config.yaml
📦 Detected 6 modules:
   - 2 critical priority
   - 2 high priority
   - 1 medium priority
   - 1 low priority (excluded from final paper)

🎯 Next Steps:
1. Review .agent/paper_config.yaml
2. Adjust priorities/descriptions if needed
3. Run: "Lutapi, generate research paper"
```

## Priority Detection Logic

| Priority | Indicators |
|:---------|:-----------|
| **Critical** | `core.py`, `engine.py`, `repository.py`, Pydantic models, domain logic |
| **High** | `manager.py`, `processor.py`, `service.py`, orchestration |
| **Medium** | `factory.py`, `builder.py`, `adapter.py`, utilities |
| **Low** | `utils.py`, `helpers.py`, `common.py`, pure support functions |

## Focus Area Detection

Dakini automatically identifies architectural patterns:
- `repository_pattern` - Repository classes found
- `factory_pattern` - Factory classes found
- `builder_pattern` - Builder classes found
- `clean_architecture` - Protocol/interface usage detected
- `dependency_injection` - Constructor injection patterns
- `mongodb_integration` - Database integration code
- `performance_monitoring` - Metric tracking code
- `evaluation_algorithms` - Statistical/grading logic

## When to Use

Run Dakini when:
- Starting a new research paper
- Adding new modules to your project
- Updating existing paper configuration
- Switching from unified to modular mode

## Related Skills

- [Journal Master (Lutapi)](journal-master.md) - Uses the generated config
- [Package Maintainer](package-maintainer.md) - Understands module structure
- [Doc Architect](doc-architect.md) - Can enhance module descriptions

## Benefits

✅ **Time Saving**: No manual YAML writing
✅ **Accuracy**: Detects all modules automatically  
✅ **Intelligence**: Assigns priorities based on code analysis
✅ **Consistency**: Follows best practices for paper generation
✅ **Maintainability**: Easy to regenerate as project evolves
