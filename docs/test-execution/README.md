# Test Execution Guide

This guide explains how to run tests, generate coverage and JUnit artifacts, and auto-populate the module-wise testing summary.

## 1. Prerequisites

- Windows PowerShell
- Project virtual environment at `.venv`
- Repository root as current directory

## 2. Activate Environment

```powershell
Set-Location E:\Python\Amsha
(Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned) ; (& E:\Python\Amsha\.venv\Scripts\Activate.ps1)
```

## 3. Ensure Package Import Resolution

If tests fail with `ModuleNotFoundError: amsha`, install the project in editable mode:

```powershell
E:\Python\Amsha\.venv\Scripts\python.exe -m pip install -e .
```

If needed, set PYTHONPATH for the current shell session:

```powershell
$env:PYTHONPATH = "E:\Python\Amsha\src\nikhil"
```

## 4. Verify Available Test Suites

```powershell
Test-Path tests\unit
Test-Path tests\integration
Test-Path tests\e2e
```

Expected current baseline in this repository:

- `tests/unit`: present
- `tests/integration`: not present
- `tests/e2e`: not present

## 5. Run Unit Tests With Report Artifacts

```powershell
New-Item -ItemType Directory -Path output\testing -Force | Out-Null
E:\Python\Amsha\.venv\Scripts\python.exe -m pytest tests/unit --junitxml=output/testing/junit-unit.xml --cov=src/nikhil/amsha --cov-report=xml:output/testing/coverage-unit.xml --cov-report=term
```

Artifacts produced:

- `output/testing/junit-unit.xml`
- `output/testing/coverage-unit.xml`

## 6. Generate Module-Wise Summary

```powershell
E:\Python\Amsha\.venv\Scripts\python.exe scripts/testing/generate_module_summary.py --junit output/testing/junit-unit.xml --coverage output/testing/coverage-unit.xml --output-md output/testing/module-summary.md --output-json output/testing/module-summary.json
```

Artifacts produced:

- `output/testing/module-summary.md`
- `output/testing/module-summary.json`

## 7. Use the Academic Report Template

Template:

- `docs/reference/testing/TEST_REPORT_TEMPLATE.md`

Pre-filled sample baseline report:

- `docs/reference/testing/SAMPLE_TEST_REPORT_UNIT_BASELINE.md`

Recommended workflow:

1. Execute steps 2 to 6.
2. Copy the template into a dated report file.
3. Fill metadata and environment tables.
4. Paste module-wise rows from `output/testing/module-summary.md`.
5. Attach artifact paths in Evidence Index.

## 8. Quick Troubleshooting

### Issue: `ModuleNotFoundError: amsha`

Cause:

- Package import path not resolved in test runtime.

Fix:

1. Run editable install: `python -m pip install -e .`
2. If still failing, set `PYTHONPATH` to `src/nikhil` for the session.

### Issue: Coverage is 0 percent with many errors

Cause:

- Tests failed during collection, so no executable test bodies ran.

Fix:

- Resolve import/runtime setup first, rerun step 5, then regenerate step 6.

### Issue: Integration/E2E sections are empty

Cause:

- Suites are not yet present as runnable directories.

Fix:

- Add integration and E2E suites, then re-run with matching JUnit/Coverage commands and update report tables.

## 9. One-Command Sequence (Copy/Paste)

```powershell
Set-Location E:\Python\Amsha
(Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned) ; (& E:\Python\Amsha\.venv\Scripts\Activate.ps1)
E:\Python\Amsha\.venv\Scripts\python.exe -m pip install -e .
New-Item -ItemType Directory -Path output\testing -Force | Out-Null
E:\Python\Amsha\.venv\Scripts\python.exe -m pytest tests/unit --junitxml=output/testing/junit-unit.xml --cov=src/nikhil/amsha --cov-report=xml:output/testing/coverage-unit.xml --cov-report=term
E:\Python\Amsha\.venv\Scripts\python.exe scripts/testing/generate_module_summary.py --junit output/testing/junit-unit.xml --coverage output/testing/coverage-unit.xml --output-md output/testing/module-summary.md --output-json output/testing/module-summary.json
```

## 10. Single Script (Recommended)

You can run the entire flow (editable install, available suite execution, JUnit + coverage XML, and module summary generation) with one command:

```powershell
E:\Python\Amsha\.venv\Scripts\python.exe scripts/testing/run_all_reports.py
```

Optional flags:

- `--skip-editable-install`: Skip `pip install -e .`
- `--cov-target <path>`: Override coverage target (default: `src/nikhil/amsha`)

The script writes:

- `output/testing/junit-<suite>.xml`
- `output/testing/coverage-<suite>.xml`
- `output/testing/module-summary-<suite>.md`
- `output/testing/module-summary-<suite>.json`
- `output/testing/report-run-summary.json`
