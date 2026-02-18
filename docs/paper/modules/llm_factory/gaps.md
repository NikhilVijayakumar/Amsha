# LLM Factory: Research Gap Analysis

## 1. Quality Assurance Gaps (CRITICAL)

### Missing Unit Tests
The `tests/unit/llm_factory` directory structure exists but contains **zero test files**. The configuration parsing and factory logic are completely unverified.

- **Gap ID:** QA-002
- **Severity:** Critical +
- **Description:** No automated verification of the build process or parameter validation.
- **Impact:** High risk of runtime failures when switching providers.
- **Recommendation:** Implement tests for `LLMBuilder` covering all supported providers (Gemini, OpenAI, Local).

## 2. Experimental Gaps

### Provider Performance Comparison (Moderate)
There is no data on the inference latency differences between the supported providers.

- **Gap ID:** PERF-002
- **Severity:** Moderate
- **Description:** Lack of benchmarks comparing "Time to First Token" and "Total Completion Time" across different configured models.
- **Recommendation:** Create a benchmark script using `LLMBuilder` to measure response times.

## 3. Implementation Gaps

### Hardcoded Model Prefixes (Minor)
The `LLMUtils.extract_model_name` method contains hardcoded strings.

- **Gap ID:** MAINT-001
- **Severity:** Minor
- **Description:** New providers (e.g., Anthropic) require code changes to be supported.
- **Source Reference:** `src/nikhil/amsha/llm_factory/utils/llm_utils.py:28`
