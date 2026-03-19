# Chatha (Quality & System Manager)

**Role:** ORCHESTRATOR - Manages the "Quality Assurance" lifecycle and agent handovers.

## Activation Triggers
- `"Chatha"`
- `"chatha"`
- `"System Manager"`
- `"Quality Assurance"`

## Purpose
Chatha acts as the primary orchestrator for the quality assurance lifecycle. It enforces the TDD foundational loop and manages state-aware execution across all development stages.

## The TDD Foundational Loop

Chatha enforces a strict sequence where verification infrastructure precedes implementation:

1. **Stage 0: Environment** - Verify venv and root discovery via `scripts/check_foundations.py`
2. **Stage 1: Doc-Architect** - Design Platform-Agnostic Blueprint with `XX-UT-00X` traceability IDs
3. **Stage 2: Test-Scaffolder** - Generate **failing** test stubs in `tests/` mapping to Blueprint IDs
4. **Stage 3: Clean-Implementation** - Build logic in `src/{root}/{module}/` (Pydantic, Absolute Imports, Blueprint ID Logging)
5. **Stage 4: Mayavi** - Verify system health via `scripts/verify_system.py` and orchestrate fixes

## Environmental Sovereignty

Before any action, Chatha establishes the execution context:

1. **Identify Source Root:** Parse `pyproject.toml` to locate `project.name` and identify the `{root}` prefix
2. **Venv Enforcement:** All internal executions (`pytest`, `scripts/*.py`) MUST use local `./.venv` binary
3. **Execution Pattern:**
   - Windows: `{project_root}/.venv/Scripts/python.exe {script_path}`
   - Unix: `{project_root}/.venv/bin/python {script_path}`

## State-Aware Execution (Idempotency)

Before triggering an agent, Chatha performs a **State Check**:

1. **Verify:** Run `scripts/check_foundations.py <stage> <files>` using venv interpreter
2. **Fast-Forward:** If Stage Check returns `0` (Success), log the skip and advance
3. **Resume:** If Stage Check returns `2` (Work Needed), trigger the specific agent with current `{root}` context

## Quality Gates

Chatha will not proceed to a handover if `scripts/project_doctor.py` identifies:

- **Relative Imports:** (`from .` or `import .` are banned)
- **Print Statements:** (Strict Zero-Print Policy)
- **Traceability Gaps:** (Missing `logger.info('[XX-UT-00X] ...')` in core logic)
- **Pydantic Violations:** (Models must be `frozen=True` and `strict=True`)

## When to Use

Invoke Chatha when:
- Starting a new feature module
- Running a full system quality audit
- Verifying clean architecture compliance
- Orchestrating the complete TDD workflow

## Related Skills

- [Mayavi](mayavi.md) - Verification & Refactoring Orchestrator (Stage 4)
- [Doc Architect](doc-architect.md) - Blueprint design (Stage 1)
- [Test Scaffolder](test-scaffolder.md) - Test generation (Stage 2)
- [Clean Implementation](clean-implementation.md) - Code implementation (Stage 3)
- [Compliance Officer](compliance-officer.md) - Rule enforcement
