### 📂 `.agent/skills/chatha/resources/manager_report_template.md`

# 📋 System Manager State Report: [MODULE_NAME]

## 🌍 Stage 0: Environment Health

* **Interpreter:** `./.venv/bin/python` (Verified: [🟢/🔴])
* **Source Root:** `{root}` (Parsed from `pyproject.toml`)
* **Dependency Sync:** `pyproject.toml` vs `.venv` (Status: [🟢/🔴])

## 🏗️ Foundation Status (The TDD Loop)

| Stage | Artifact Check | Status | Verification Tool |
| --- | --- | --- | --- |
| **1. Design** | `docs/features/[feature]/README.md` | [🟢/🔴] | `check_foundations.py` |
| **2. Test** | `tests/unit/[feature]/test_unit.py` | [🟢/🔴] | `pytest` via `.venv` |
| **3. Build** | `src/{root}/[feature]/core.py` | [🟢/🔴] | `project_doctor.py` |

## 📝 Quality Audit (Pillars of Quality)

* **Absolute Imports:** [Verified/Pending]
* **Frozen Pydantic Models:** [Verified/Pending]
* **Traceability IDs (XX-UT-00X):** [Mapped/Missing]
* **Zero-Print Policy:** [Enforced/Violation Found]

---

## ⏭️ Next Step

**Current State:** [e.g., Stage 2 Verified]
**Action:** Triggering **Clean-Implementation** with `{root}` absolute import context.

---

