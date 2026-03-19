# LLM Factory: Research Gap Analysis

This document identifies gaps against Scopus-indexed publication standards, categorized by severity and effort.

---

## 1. Quality Assurance Gaps

### GAP QA-001: Missing Unit Tests (CRITICAL)

The `tests/unit/llm_factory/` directory structure exists with compiled `.pyc` caches (suggesting tests were previously written and ran), but **no active `.py` test files** are present. The configuration resolution, factory logic, and telemetry disabling are all unverified.

- **Severity:** Critical ⛔
- **Impact:** Cannot validate provider switching, parameter defaults, or privacy enforcement.
- **Source:** `tests/unit/llm_factory/` — Contains `.pyc` files but no `.py` sources.
- **Historical Note:** Compiled caches suggest tests were deleted or moved. Recovery of test intent is possible from cache analysis.
- **Recommendation:** Regenerate test suites covering:
  1. `LLMBuilder.build()` — Cloud vs. Local branching
  2. `LLMSettings.get_model_config()` — Default resolution, missing use case, missing model
  3. `LLMUtils.disable_telemetry()` — Verify all Telemetry methods are replaced
  4. `LLMUtils.extract_model_name()` — All prefix variations
- **Estimated Effort:** 2 days

---

## 2. Experimental Gaps

### GAP PERF-001: No Provider Latency Benchmarks (CRITICAL)

No empirical data exists on the latency differences between supported providers (Cloud Gemini vs. Local LM Studio models).

- **Severity:** Critical ⛔
- **Description:** The module's primary claim — unified multi-provider access — cannot be validated without latency comparison data.
- **Impact:** Cannot defend provider selection recommendations in the paper.
- **Source:** No timing instrumentation in [llm_builder.py](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/llm_factory/service/llm_builder.py).
- **Recommendation:** Benchmark suite measuring:
  1. Time to First Token (TTFT) per provider
  2. Total Completion Time for standardized prompts
  3. Init time for local vs. cloud instantiation
- **Estimated Effort:** 2 days

### GAP PERF-002: No Parameter Sensitivity Analysis (MODERATE)

The creative (τ=1.0, p=0.9) and evaluation (τ=0.3, p=0.5) parameter presets are not empirically justified.

- **Severity:** Moderate
- **Description:** Temperature and top_p values are configured without documented rationale or A/B testing results.
- **Source:** [llm_config.yaml.template:L65–L81](file:///home/dell/PycharmProjects/Amsha/config/llm_config.yaml.template#L65-L81)
- **Recommendation:** Run standardized benchmarks varying τ and p, measuring output quality metrics.
- **Estimated Effort:** 3 days

### GAP PERF-003: No Cost Analysis (MODERATE)

No cost-per-token comparison across providers is documented.

- **Severity:** Moderate
- **Description:** Production deployment decisions require cost data alongside latency data.
- **Recommendation:** Document cost per 1k input/output tokens for each provider.
- **Estimated Effort:** 1 day

---

## 3. Implementation Gaps

### GAP IMPL-001: Hardcoded Model Prefixes (MODERATE)

The `extract_model_name()` method uses a hardcoded prefix list `["lm_studio/", "gemini/", "open_ai/", "azure"]`.

- **Severity:** Moderate
- **Description:** Adding new providers (e.g., Anthropic/Claude, Mistral, Cohere) requires code changes.
- **Source:** [llm_utils.py:L28](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/llm_factory/utils/llm_utils.py#L28)
- **Recommendation:** Move prefix list to YAML config or derive from model string structure (split on `/`).
- **Estimated Effort:** 0.5 days

### GAP IMPL-002: Inconsistent Azure Prefix (MINOR)

The prefix `"azure"` (without trailing `/`) causes incorrect extraction: `"azure/gpt-4o"` → `"/gpt-4o"` (note leading slash).

- **Severity:** Minor (Bug)
- **Source:** [llm_utils.py:L28](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/llm_factory/utils/llm_utils.py#L28)
- **Recommendation:** Change `"azure"` to `"azure/"` in the prefix list.
- **Estimated Effort:** 5 minutes

### GAP IMPL-003: No Provider Health Check (MODERATE)

No pre-flight validation checks whether a provider is reachable before attempting LLM construction.

- **Severity:** Moderate
- **Description:** Local LM Studio may not be running; cloud APIs may have expired keys.
- **Source:** [llm_builder.py:L15–L48](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/llm_factory/service/llm_builder.py#L15-L48) — No connectivity check.
- **Recommendation:** Add optional `health_check()` that pings `base_url` or validates API key.
- **Estimated Effort:** 1 day

### GAP IMPL-004: Streaming Always Enabled (MINOR)

`stream=True` is hardcoded in both instantiation paths.

- **Severity:** Minor
- **Source:** [llm_builder.py:L31, L45](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/llm_factory/service/llm_builder.py#L31)
- **Recommendation:** Make configurable via `LLMParameters` or use-case config.
- **Estimated Effort:** 0.5 days

### GAP IMPL-005: No Fallback/Retry Logic (MODERATE)

If the primary provider fails, there is no automatic fallback to an alternative provider.

- **Severity:** Moderate
- **Description:** Multi-provider systems benefit from automatic failover (e.g., if Gemini rate-limits, fall back to LM Studio).
- **Source:** `LLMBuilder` has no retry or fallback mechanism.
- **Recommendation:** Implement provider chain with ordered fallback list.
- **Estimated Effort:** 2 days

---

## 4. Validation Gaps

### GAP VAL-001: No Telemetry Disabling Verification (HIGH)

The reflection-based telemetry patch is applied but never verified — no test confirms all Telemetry methods are actually replaced.

- **Severity:** High
- **Description:** If CrewAI updates its `Telemetry` class, the patch may silently fail.
- **Source:** [llm_utils.py:L16–L24](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/llm_factory/utils/llm_utils.py#L16-L24)
- **Recommendation:** Add assertion test: `assert all(getattr(Telemetry, a) == noop for a in callables)`.
- **Estimated Effort:** 0.5 days

### GAP VAL-002: No YAML Schema Validation (MODERATE)

The YAML config file is loaded without schema validation — malformed configs produce cryptic Pydantic errors.

- **Severity:** Moderate
- **Source:** [llm_container.py:L15–L18](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/llm_factory/dependency/llm_container.py#L15-L18) — Raw `yaml_safe_load` with no validation.
- **Recommendation:** Add YAML schema validation or improve error messages in `LLMSettings`.
- **Estimated Effort:** 1 day

---

## 5. Gap Summary Matrix

| Gap ID | Category | Severity | Effort | Priority |
|--------|----------|----------|--------|----------|
| QA-001 | Testing | Critical ⛔ | 2 days | P0 |
| PERF-001 | Benchmark | Critical ⛔ | 2 days | P0 |
| PERF-002 | Benchmark | Moderate | 3 days | P2 |
| PERF-003 | Benchmark | Moderate | 1 day | P2 |
| IMPL-001 | Extensibility | Moderate | 0.5 day | P2 |
| IMPL-002 | Bug | Minor | 5 min | P1 |
| IMPL-003 | Resiliency | Moderate | 1 day | P2 |
| IMPL-004 | Config | Minor | 0.5 day | P3 |
| IMPL-005 | Resiliency | Moderate | 2 days | P2 |
| VAL-001 | Validation | High | 0.5 day | P1 |
| VAL-002 | Validation | Moderate | 1 day | P2 |

**Total Critical Gaps:** 2 | **Total Gaps:** 11 | **Estimated Total Effort:** ~14 days
