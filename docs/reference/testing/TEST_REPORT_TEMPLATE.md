# Test Report Template (Academic, Module-Wise)

## 1. Report Metadata

| Field | Value |
| --- | --- |
| Report Title | |
| Project | |
| Target Version/Commit | |
| Report Date | |
| Prepared By | |
| Reviewed By | |

## 2. Objective and Scope

### 2.1 Objective

| Item | Details |
| --- | --- |
| Primary Objective | |
| Secondary Objective | |
| Success Criteria | |

### 2.2 Scope

| Scope Type | Details |
| --- | --- |
| In Scope | |
| Out of Scope | |
| Assumptions | |
| Constraints | |

## 3. Test Suite Availability Check (Run Before Reporting)

### 3.1 Current Repository Baseline (as of this template update)

| Suite | Expected Location | Present in Repo |
| --- | --- | --- |
| Unit | `tests/unit/` | Yes |
| Integration | `tests/integration/` | No |
| End-to-End (E2E) | `tests/e2e/` | No |

### 3.2 Execution-Time Verification

| Suite | Checked? (Y/N) | Command or Method Used | Result |
| --- | --- | --- | --- |
| Unit | | | |
| Integration | | | |
| E2E | | | |

## 4. Experimental Environment

| Parameter | Value |
| --- | --- |
| OS | |
| Python Version | |
| Test Framework | |
| Coverage Tool | |
| Dependency Snapshot | |
| Dataset/Fixtures | |
| CI/CD Job Link | |

## 5. Overall Execution Summary

| Metric | Value |
| --- | --- |
| Start Time | |
| End Time | |
| Duration | |
| Total Tests | |
| Passed | |
| Failed | |
| Skipped | |
| Errors | |
| Pass Rate (%) | |

## 6. Module-Wise Test Report (Primary Section)

Use one row per module/package (for example: `crew_forge`, `crew_monitor`, `llm_factory`, `utils`).

| Module | Unit (P/F/S) | Integration (P/F/S) | E2E (P/F/S) | Coverage (%) | Status | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| [module_1] | | | | | | |
| [module_2] | | | | | | |
| [module_3] | | | | | | |

Status suggestion: `Pass`, `Conditional Pass`, `Fail`, `Not Executed`.

## 7. Suite-Wise Detailed Tables

### 7.1 Unit Test Details

| Module | Command | Total | Passed | Failed | Skipped | Coverage (%) | Key Failures |
| --- | --- | --- | --- | --- | --- | --- | --- |
| | | | | | | | |

### 7.2 Integration Test Details (If Available)

| Module | Command | Total | Passed | Failed | Skipped | Environment | Key Failures |
| --- | --- | --- | --- | --- | --- | --- | --- |
| | | | | | | | |

### 7.3 E2E Test Details (If Available)

| Module/Flow | Command | Total Scenarios | Passed | Failed | Skipped | Environment | Key Failure Scenarios |
| --- | --- | --- | --- | --- | --- | --- | --- |
| | | | | | | | |

## 8. Coverage Analysis

| Module | Lines (%) | Branch (%) | Target (%) | Meets Target (Y/N) |
| --- | --- | --- | --- | --- |
| | | | | |

### 8.1 Low-Coverage Critical Paths

| Path/Function | Current Coverage | Risk | Planned Action |
| --- | --- | --- | --- |
| | | | |

## 9. Defect and Root-Cause Summary

### 9.1 Defect Register

| Defect ID | Module | Severity | Root Cause Category | Owner | Status |
| --- | --- | --- | --- | --- | --- |
| | | | | | |

### 9.2 Root Cause Pattern Analysis

| Pattern | Frequency | Impact | Mitigation |
| --- | --- | --- | --- |
| | | | |

## 10. Risks, Gaps, and Deferred Tests

| Item | Type (Risk/Gap/Deferred) | Impact | Reason | Planned Phase |
| --- | --- | --- | --- | --- |
| | | | | |

## 11. Evidence Index

| Evidence Type | Path/Link | Description |
| --- | --- | --- |
| Pytest Output Log | | |
| Coverage Report | | |
| JUnit/XML/JSON Results | | |
| Screenshots/Videos (E2E) | | |

## 12. Conclusion and Recommendation

| Item | Decision |
| --- | --- |
| Release Recommendation | Go / Conditional Go / No-Go |
| Mandatory Fixes Before Release | |
| Optional Improvements | |

## 13. Sign-Off

| Role | Name | Date | Signature/Approval |
| --- | --- | --- | --- |
| Test Owner | | | |
| Engineering Owner | | | |
| Product/Research Owner (Optional) | | | |
