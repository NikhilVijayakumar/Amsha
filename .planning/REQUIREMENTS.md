# Amsha — Requirements

> **Project:** Amsha Research Paper Preparation  
> **Date:** 2026-04-10

---

## v1 Requirements

### Data Completion

- [ ] **DATA-01**: Analyze existing benchmark data in research/results/MASTER_AGGREGATION.json
- [ ] **DATA-02**: Fill in 📝 markers in docs/paper/user_inputs/app_execution_results.md with actual values
- [ ] **DATA-03**: Extract latency metrics from crew_construction_*.json files
- [ ] **DATA-04**: Extract end-to-end timing from end_to_end_*.json files
- [ ] **DATA-05**: Extract monitoring metrics from monitoring_observability_*.json files
- [ ] **DATA-06**: Extract evaluation pipeline results from evaluation_pipeline_*.json files
- [ ] **DATA-07**: Extract privacy verification results from privacy_verification_*.json files

### Practical Implications Verification

- [ ] **VERIFY-01**: Confirm/reject/modify claims in docs/paper/user_inputs/practical_implications.md
- [ ] **VERIFY-02**: Verify dual-backend equivalence claims (YAML vs MongoDB)
- [ ] **VERIFY-03**: Verify privacy enforcement claims (OTEL + telemetry)
- [ ] **VERIFY-04**: Verify monitoring overhead bounds (≤0.05%)

### Code Quality

- [ ] **QUAL-01**: Break circular dependency (output_process → crew_forge via CrewParser)
- [ ] **QUAL-02**: Add Pydantic domain models to output_process module
- [ ] **QUAL-03**: Document the cross-module integration in cross_module/architecture.md

### Paper Structure

- [ ] **PAPER-01**: Finalize architecture section for each module (crew_forge, llm_factory, crew_monitor, output_process)
- [ ] **PAPER-02**: Document novelty contributions for each module
- [ ] **PAPER-03**: Document mathematical foundations for each module
- [ ] **PAPER-04**: Analyze gaps and document in gaps.md for each module

---

## v2 Requirements (Deferred)

- [ ] Implement inter-rater reliability metrics (Cohen's κ, Fleiss' κ) for multi-judge evaluation
- [ ] Extend GPU monitoring beyond NVIDIA (AMD ROCm, Apple MPS, Intel ARC)
- [ ] Implement automatic provider failover with ordered fallback chains
- [ ] Validate Feature Consensus metric P(F) against ground truth

---

## Out of Scope

- [New provider integrations] — Not required for paper; current 4 tiers sufficient
- [Web UI or CLI interface] — Library-only focus; paper is technical
- [Parallel agent execution] — Sequential/hierarchical only; not in scope
- [Post-paper publication] — Beyond scope of this project

---

## Traceability

| REQ-ID | Phase | Description |
|--------|-------|-------------|
| DATA-01 | 1 | Analyze existing benchmark data |
| DATA-02 | 1 | Fill in empirical values in paper template |
| DATA-03 | 1 | Extract crew construction metrics |
| DATA-04 | 1 | Extract E2E timing metrics |
| DATA-05 | 1 | Extract monitoring metrics |
| DATA-06 | 1 | Extract evaluation metrics |
| DATA-07 | 1 | Extract privacy verification metrics |
| VERIFY-01 | 2 | Verify practical implications |
| VERIFY-02 | 2 | Verify dual-backend claims |
| VERIFY-03 | 2 | Verify privacy enforcement |
| VERIFY-04 | 2 | Verify monitoring overhead |
| QUAL-01 | 3 | Break circular dependency |
| QUAL-02 | 3 | Add Pydantic models to output_process |
| QUAL-03 | 3 | Document cross-module integration |
| PAPER-01 | 4 | Finalize architecture sections |
| PAPER-02 | 5 | Document novelty contributions |
| PAPER-03 | 5 | Document mathematical foundations |
| PAPER-04 | 6 | Analyze gaps and document |

---

*Last updated: 2026-04-10*