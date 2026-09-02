# Test Report (Sample) - Unit-Only Baseline

## 1. Report Metadata

| Field | Value |
| --- | --- |
| Report Title | Amsha Unit Baseline Test Report |
| Project | Amsha |
| Target Version/Commit | Working tree snapshot (local) |
| Report Date | 2026-04-18 |
| Prepared By | GitHub Copilot |
| Reviewed By | Pending |

## 2. Objective and Scope

### 2.1 Objective

| Item | Details |
| --- | --- |
| Primary Objective | Establish a measurable unit-test baseline and generate module-wise status. |
| Secondary Objective | Validate report automation using JUnit + coverage XML inputs. |
| Success Criteria | Produce a reproducible report with suite availability, totals, and module-wise table. |

### 2.2 Scope

| Scope Type | Details |
| --- | --- |
| In Scope | Unit test execution, module summary generation, coverage XML parsing, report generation. |
| Out of Scope | Fixing failing tests/import paths, enabling integration/E2E suites, CI pipeline changes. |
| Assumptions | Current environment uses local venv and direct pytest invocation. |
| Constraints | Existing tests failed at collection due import resolution issues. |

## 3. Test Suite Availability Check (Run Before Reporting)

### 3.1 Current Repository Baseline

| Suite | Expected Location | Present in Repo |
| --- | --- | --- |
| Unit | `tests/unit/` | Yes |
| Integration | `tests/integration/` | No |
| End-to-End (E2E) | `tests/e2e/` | No |

### 3.2 Execution-Time Verification

| Suite | Checked? (Y/N) | Command or Method Used | Result |
| --- | --- | --- | --- |
| Unit | Y | `python -m pytest tests/unit --junitxml=... --cov=...` | Executed; collection errors present |
| Integration | Y | Filesystem check for `tests/integration/` | Not present |
| E2E | Y | Filesystem check for `tests/e2e/` | Not present |

## 4. Experimental Environment

| Parameter | Value |
| --- | --- |
| OS | Windows |
| Python Version | 3.12.11 |
| Test Framework | pytest |
| Coverage Tool | coverage.py via pytest-cov |
| Dependency Snapshot | Local venv (`.venv`) |
| Dataset/Fixtures | Existing project unit tests and fixtures |
| CI/CD Job Link | N/A (local run) |

## 5. Overall Execution Summary

| Metric | Value |
| --- | --- |
| Start Time | 2026-04-18T12:42:54+05:30 (from JUnit timestamp) |
| End Time | Start + 25.367s |
| Duration | 25.367 s |
| Total Tests | 32 |
| Passed | 0 |
| Failed | 0 |
| Skipped | 0 |
| Errors | 32 |
| Pass Rate (%) | 0.00 |

## 6. Module-Wise Test Report (Primary Section)

| Module | Unit (P/F/S/E) | Integration (P/F/S/E) | E2E (P/F/S/E) | Coverage (%) | Status | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| common | 0/0/0/0 | 0/0/0/0 | 0/0/0/0 | 0.00 | Not Executed | No collected unit case in this run set |
| crew_forge | 0/0/0/18 | 0/0/0/0 | 0/0/0/0 | 0.00 | Fail | Collection errors (`ModuleNotFoundError: amsha`) |
| crew_monitor | 0/0/0/3 | 0/0/0/0 | 0/0/0/0 | 0.00 | Fail | Collection errors (`ModuleNotFoundError: amsha`) |
| execution_runtime | 0/0/0/1 | 0/0/0/0 | 0/0/0/0 | 0.00 | Fail | Collection errors (`ModuleNotFoundError: amsha`) |
| execution_state | 0/0/0/2 | 0/0/0/0 | 0/0/0/0 | 0.00 | Fail | Collection errors (`ModuleNotFoundError: amsha`) |
| llm_factory | 0/0/0/4 | 0/0/0/0 | 0/0/0/0 | 0.00 | Fail | Collection errors (`ModuleNotFoundError: amsha`) |
| output_process | 0/0/0/1 | 0/0/0/0 | 0/0/0/0 | 0.00 | Fail | Collection errors (`ModuleNotFoundError: amsha`) |
| utils | 0/0/0/3 | 0/0/0/0 | 0/0/0/0 | 0.00 | Fail | Collection errors (`ModuleNotFoundError: amsha`) |

## 7. Suite-Wise Detailed Tables

### 7.1 Unit Test Details

| Module | Command | Total | Passed | Failed | Skipped | Errors | Coverage (%) | Key Failures |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| All modules | `python -m pytest tests/unit --junitxml=output/testing/junit-unit.xml --cov=src/nikhil/amsha --cov-report=xml:output/testing/coverage-unit.xml` | 32 | 0 | 0 | 0 | 32 | 0.00 | Import resolution (`No module named amsha`) during collection |

### 7.2 Integration Test Details (If Available)

| Module | Command | Total | Passed | Failed | Skipped | Environment | Key Failures |
| --- | --- | --- | --- | --- | --- | --- | --- |
| N/A | N/A | N/A | N/A | N/A | N/A | N/A | Suite not present in repository |

### 7.3 E2E Test Details (If Available)

| Module/Flow | Command | Total Scenarios | Passed | Failed | Skipped | Environment | Key Failure Scenarios |
| --- | --- | --- | --- | --- | --- | --- | --- |
| N/A | N/A | N/A | N/A | N/A | N/A | N/A | Suite not present in repository |

## 8. Coverage Analysis

| Module | Lines (%) | Branch (%) | Target (%) | Meets Target (Y/N) |
| --- | --- | --- | --- | --- |
| All observed modules | 0.00 | 0.00 | 80.00 | N |

### 8.1 Low-Coverage Critical Paths

| Path/Function | Current Coverage | Risk | Planned Action |
| --- | --- | --- | --- |
| `src/nikhil/amsha/**/*` | 0.00 | High | Fix import path/package resolution before rerunning baseline |

## 9. Defect and Root-Cause Summary

### 9.1 Defect Register

| Defect ID | Module | Severity | Root Cause Category | Owner | Status |
| --- | --- | --- | --- | --- | --- |
| BASELINE-IMPORT-001 | Multiple | High | Test environment/import configuration | Pending | Open |

### 9.2 Root Cause Pattern Analysis

| Pattern | Frequency | Impact | Mitigation |
| --- | --- | --- | --- |
| `ModuleNotFoundError: amsha` at collection | 32 | Blocks all unit execution and distorts coverage | Run tests with correct package import path or editable install |

## 10. Risks, Gaps, and Deferred Tests

| Item | Type (Risk/Gap/Deferred) | Impact | Reason | Planned Phase |
| --- | --- | --- | --- | --- |
| Integration suite absent | Gap | Medium | Folder and runnable suite not present | Future testing phase |
| E2E suite absent | Gap | Medium | Folder and runnable suite not present | Future testing phase |
| Unit collection blocked | Risk | High | Import path mismatch | Immediate |

## 11. Evidence Index

| Evidence Type | Path/Link | Description |
| --- | --- | --- |
| JUnit XML | `output/testing/junit-unit.xml` | Raw pytest test outcomes and collection errors |
| Coverage XML | `output/testing/coverage-unit.xml` | Coverage metrics for source tree |
| Module summary (Markdown) | `output/testing/module-summary.md` | Auto-generated module-wise table |
| Module summary (JSON) | `output/testing/module-summary.json` | Auto-generated machine-readable summary |

## 12. Conclusion and Recommendation

| Item | Decision |
| --- | --- |
| Release Recommendation | No-Go |
| Mandatory Fixes Before Release | Resolve Python import/package setup so tests can execute beyond collection |
| Optional Improvements | Add integration and E2E runnable suites for complete verification |

## 13. Sign-Off

| Role | Name | Date | Signature/Approval |
| --- | --- | --- | --- |
| Test Owner | Pending | 2026-04-18 | Pending |
| Engineering Owner | Pending | 2026-04-18 | Pending |
| Product/Research Owner (Optional) | Pending | 2026-04-18 | Pending |
