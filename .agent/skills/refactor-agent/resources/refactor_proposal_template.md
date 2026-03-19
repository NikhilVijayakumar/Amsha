# Refactor Proposal: [MODULE_NAME]

## 🔴 The Issue
- **Metric:** [e.g., Cyclomatic Complexity 14]
- **File:** `src/nikhil/amsha/...`
- **Report Link:** `.agent/reports/complexity_report.md`

## 🛠️ Proposed Solution
- [ ] Move logic [X] to new Domain Model: `[name].py`
- [ ] Implement Protocol: `[name]_protocol.py`
- [ ] Update `__init__` for Dependency Injection.

## ✅ Verification Plan
- [ ] Run `pytest tests/unit/[module]`
- [ ] Run `ruff check`