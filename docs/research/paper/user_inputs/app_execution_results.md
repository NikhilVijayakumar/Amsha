# Amsha — Application Execution Results Template

> **Purpose:** This template is pre-filled with suggested experiments and metrics inferred from the existing module analysis (mathematics, novelty, gaps). Fill in your actual empirical values where marked with `📝 YOUR DATA`.

---

## 1. Crew Construction Performance

> *Inferred from:* crew_forge/mathematics.md §1–3, crew_forge/gaps.md PERF-001

### 1.1 Build Latency: Crew Assembly Overhead

Measure the time for `CrewBuilderService.build()` with varying crew sizes.

| Crew Size (Agents × Tasks) | Amsha DB-Backed (ms) | Amsha YAML-Backed (ms) | Direct CrewAI (ms) | Overhead vs. CrewAI (%) |
|:---|:---:|:---:|:---:|:---:|
| 1 × 1 | 📝 | 📝 | 📝 | 📝 |
| 3 × 3 | 📝 | 📝 | 📝 | 📝 |
| 5 × 5 | 📝 | 📝 | 📝 | 📝 |
| 10 × 10 | 📝 | 📝 | 📝 | 📝 |
| 20 × 20 | 📝 | 📝 | 📝 | 📝 |

**Methodology:**
- Iterations per measurement: 📝 (suggested: 100)
- Environment: 📝 (CPU, RAM, OS)
- MongoDB version: 📝
- Warm-up runs excluded: 📝 (suggested: 5)

### 1.2 Backend Equivalence Verification

Verify that DB-backed and YAML-backed crews produce identical output for the same input.

| Test Case | DB Output Hash | YAML Output Hash | Match? |
|:---|:---:|:---:|:---:|
| Simple 1-agent crew | 📝 | 📝 | 📝 |
| 3-agent sequential crew | 📝 | 📝 | 📝 |
| 5-agent with knowledge | 📝 | 📝 | 📝 |

### 1.3 Idempotent Sync Convergence

Measure `DatabaseSeeder.synchronize()` behavior over multiple runs on the same YAML set.

| Run | New Entities Created | Entities Updated | Entities Skipped | Total Time (ms) |
|:---|:---:|:---:|:---:|:---:|
| Run 1 (initial) | 📝 | 📝 | 📝 | 📝 |
| Run 2 (repeat) | 📝 | 📝 | 📝 | 📝 |
| Run 5 (steady state) | 📝 | 📝 | 📝 | 📝 |
| Run 10 (final) | 📝 | 📝 | 📝 | 📝 |

**Expected:** Runs 2–N should show 0 Creates, 0 Updates, N Skips.

---

## 2. LLM Provider Performance

> *Inferred from:* llm_factory/mathematics.md §1–2, llm_factory/gaps.md PERF-001/002/003

### Available Provider Inventory

| Tier | Provider | Endpoint | Models Available |
|:---|:---|:---|:---|
| ☁️ Cloud (Direct) | Google Gemini | Direct API | gemini-1.5-flash, gemini-2.0-flash |
| ☁️ Cloud (Azure) | Azure OpenAI | Azure API | gpt-4o |
| ☁️ Cloud (Router) | OpenRouter | `https://openrouter.ai/api/v1` | Free-tier models (varies) |
| 🖥️ Local (LM Studio) | LM Studio | `http://localhost:1234/v1` | 6 GGUF models (see below) |

### Local Model Inventory (LM Studio)

| Model | Quantization | Provider | Size (B) | File Size (GB) | Format |
|:---|:---|:---|:---:|:---:|:---:|
| Qwen3 14B | Q6_K | lmstudio-community | 14B | 11.29 | GGUF |
| GPT-OSS 20B | MXFP4 | openai | 20B | 11.28 | GGUF |
| Meta Llama 3.1 8B Instruct | Q6_K_L | bartowski | 8B | 6.38 | GGUF |
| MN 12B Lyra v1 | Q6_K_L | bartowski | 12B | 9.67 | GGUF |
| Gemma 3 12B Instruct | Q6_K | lmstudio-community | 12B | 9.79 | GGUF |
| Phi 4 Reasoning Plus | Q4_K_M | microsoft | 15B | 8.43 | GGUF |

### 2.1 Provider Latency Comparison

| Provider | Model | TTFT (ms) | Total Completion (s) | Init Time (ms) | Tokens/sec |
|:---|:---|:---:|:---:|:---:|:---:|
| **☁️ Cloud (Direct API)** | | | | | |
| Google Gemini | gemini-1.5-flash | 📝 | 📝 | 📝 | 📝 |
| Google Gemini | gemini-2.0-flash | 📝 | 📝 | 📝 | 📝 |
| **☁️ Cloud (Azure API)** | | | | | |
| Azure OpenAI | gpt-4o | 📝 | 📝 | 📝 | 📝 |
| **☁️ Cloud (OpenRouter Free)** | | | | | |
| OpenRouter | 📝 (free model 1) | 📝 | 📝 | 📝 | 📝 |
| OpenRouter | 📝 (free model 2) | 📝 | 📝 | 📝 | 📝 |
| **🖥️ Local (LM Studio)** | | | | | |
| LM Studio | Qwen3 14B (Q6_K) | 📝 | 📝 | 📝 | 📝 |
| LM Studio | GPT-OSS 20B (MXFP4) | 📝 | 📝 | 📝 | 📝 |
| LM Studio | Llama 3.1 8B (Q6_K_L) | 📝 | 📝 | 📝 | 📝 |
| LM Studio | MN 12B Lyra v1 (Q6_K_L) | 📝 | 📝 | 📝 | 📝 |
| LM Studio | Gemma 3 12B (Q6_K) | 📝 | 📝 | 📝 | 📝 |
| LM Studio | Phi 4 Reasoning Plus (Q4_K_M) | 📝 | 📝 | 📝 | 📝 |

**Methodology:**
- Standardized prompt: 📝 (describe prompt used)
- Prompt token count: 📝
- Expected completion tokens: 📝
- Iterations per provider: 📝 (suggested: 10)
- Local GPU: 📝 (model, VRAM)
- OpenRouter endpoint: `https://openrouter.ai/api/v1`

### 2.2 Parameter Sensitivity Analysis

Effect of temperature (τ) and top_p on output quality for a standardized task.

**Representative models tested:** Gemini-2.0-flash (cloud), GPT-4o (Azure), Phi 4 Reasoning Plus (local).

| Temperature (τ) | top_p | Quality Score (0–10) | Creativity Score (0–10) | Consistency (σ over 5 runs) |
|:---|:---|:---:|:---:|:---:|
| 0.0 | 1.0 | 📝 | 📝 | 📝 |
| 0.3 | 0.5 (eval preset) | 📝 | 📝 | 📝 |
| 0.7 | 0.9 | 📝 | 📝 | 📝 |
| 1.0 | 0.9 (creative preset) | 📝 | 📝 | 📝 |
| 1.5 | 1.0 | 📝 | 📝 | 📝 |

### 2.3 Cost per Task

| Provider | Model | Avg Input Tokens | Avg Output Tokens | Cost/1K Input | Cost/1K Output | Total Cost/Task |
|:---|:---|:---:|:---:|:---:|:---:|:---:|
| **☁️ Cloud** | | | | | | |
| Google Gemini | gemini-1.5-flash | 📝 | 📝 | 📝 | 📝 | 📝 |
| Google Gemini | gemini-2.0-flash | 📝 | 📝 | 📝 | 📝 | 📝 |
| Azure OpenAI | gpt-4o | 📝 | 📝 | 📝 | 📝 | 📝 |
| OpenRouter (Free) | 📝 | 📝 | 📝 | $0 | $0 | $0 |
| **🖥️ Local** | | | | | | |
| LM Studio | Qwen3 14B | 📝 | N/A (local) | $0 | $0 | $0 (+ hw amort.) |
| LM Studio | GPT-OSS 20B | 📝 | N/A (local) | $0 | $0 | $0 (+ hw amort.) |
| LM Studio | Llama 3.1 8B | 📝 | N/A (local) | $0 | $0 | $0 (+ hw amort.) |
| LM Studio | MN 12B Lyra v1 | 📝 | N/A (local) | $0 | $0 | $0 (+ hw amort.) |
| LM Studio | Gemma 3 12B | 📝 | N/A (local) | $0 | $0 | $0 (+ hw amort.) |
| LM Studio | Phi 4 Reasoning Plus | 📝 | N/A (local) | $0 | $0 | $0 (+ hw amort.) |

**Hardware Amortization Note:** Local cost = 📝 (GPU cost ÷ expected lifetime hours × avg task duration).

### 2.4 Cloud vs. Local Trade-Off Summary

| Dimension | Cloud (Gemini/GPT-4o) | OpenRouter (Free) | Local (LM Studio) |
|:---|:---:|:---:|:---:|
| Latency | 📝 | 📝 | 📝 |
| Cost per 1K tasks | 📝 | $0 | $0 (+ hardware) |
| Privacy | ❌ Data leaves network | ❌ Data leaves network | ✅ Fully air-gapped |
| Availability | 99.9% SLA | Best-effort (free tier) | Depends on local uptime |
| Max Model Size | Unlimited (cloud) | Varies | Limited by VRAM |
| Quantization Loss | None (full precision) | None | 📝 (Q4/Q6 impact) |

---

## 3. Monitoring & Observability

> *Inferred from:* crew_monitor/mathematics.md §1–4, crew_monitor/gaps.md EXP-001

### 3.1 Monitoring Overhead (Observer Effect)

| Scenario | Without Monitor (s) | With Monitor (s) | Overhead (ms) | Overhead (%) |
|:---|:---:|:---:|:---:|:---:|
| Simple 1-agent task | 📝 | 📝 | 📝 | 📝 |
| 3-agent sequential | 📝 | 📝 | 📝 | 📝 |
| 5-agent with knowledge | 📝 | 📝 | 📝 | 📝 |

**Expected:** Overhead ≤ 5ms (≤ 0.05%) based on mathematical bound in cross_module/mathematics.md §6.

### 3.2 Resource Consumption per Provider Tier

| Metric | Cloud (Gemini) | Cloud (GPT-4o) | Local (Phi 4 RP) | Local (Qwen3 14B) |
|:---|:---:|:---:|:---:|:---:|
| Duration (s) | 📝 | 📝 | 📝 | 📝 |
| CPU Start (%) | 📝 | 📝 | 📝 | 📝 |
| CPU End (%) | 📝 | 📝 | 📝 | 📝 |
| RAM Δ (MB) | 📝 | 📝 | 📝 | 📝 |
| GPU VRAM Δ (MB) | N/A | N/A | 📝 | 📝 |
| GPU Utilization (%) | N/A | N/A | 📝 | 📝 |
| Total Tokens | 📝 | 📝 | 📝 | 📝 |
| Prompt Tokens | 📝 | 📝 | 📝 | 📝 |
| Completion Tokens | 📝 | 📝 | 📝 | 📝 |

### 3.3 Feature Consensus Validation

> *Inferred from:* crew_monitor/mathematics.md §3, crew_monitor/gaps.md EXP-002

| Feature | Consensus P(F) | Ground Truth Present? | Correct? |
|:---|:---:|:---:|:---:|
| Feature 1: 📝 | 📝% | 📝 | 📝 |
| Feature 2: 📝 | 📝% | 📝 | 📝 |
| Feature 3: 📝 | 📝% | 📝 | 📝 |
| ... | ... | ... | ... |

**Correlation:** Pearson r(P(F), accuracy) = 📝

---

## 4. Evaluation Pipeline Performance

> *Inferred from:* output_process/mathematics.md §1–3, output_process/gaps.md METH-001, output_process/novelty.md

### 4.1 JSON Sanitization Recovery Rate

| Stage | Strategy | Success Count | Cumulative Recovery (%) |
|:---|:---|:---:|:---:|
| 1 | Fence extraction | 📝 / 📝 total | 📝% |
| 2 | Direct parse | 📝 / remaining | 📝% |
| 3 | Object extraction | 📝 / remaining | 📝% |
| 4 | Quote repair | 📝 / remaining | 📝% |
| **Total** | **All stages** | **📝 / 📝** | **📝%** |

**Expected:** >90% by stage 2, >98% by stage 3 (from novelty analysis).

### 4.2 Grading Stability: Absolute vs. Relative

> *Inferred from:* output_process/novelty.md Study 1

| Run | Generation Model | Eval Model | Absolute Score (%) | Absolute Grade | Z-Score Grade | Rank (Abs) | Rank (Rel) |
|:---|:---|:---|:---:|:---:|:---:|:---:|:---:|
| 1 | Qwen3 14B | Gemini | 📝 | 📝 | 📝 | 📝 | 📝 |
| 2 | Phi 4 RP | Gemini | 📝 | 📝 | 📝 | 📝 | 📝 |
| 3 | GPT-OSS 20B | Gemini | 📝 | 📝 | 📝 | 📝 | 📝 |
| 4 | Llama 3.1 8B | Gemini | 📝 | 📝 | 📝 | 📝 | 📝 |
| 5 | Gemma 3 12B | Gemini | 📝 | 📝 | 📝 | 📝 | 📝 |
| 6 | MN 12B Lyra | Gemini | 📝 | 📝 | 📝 | 📝 | 📝 |

**Ranking Stability:** Kendall τ variance (absolute): 📝, Kendall τ variance (relative): 📝

### 4.3 Cross-Evaluator Agreement

> *Inferred from:* output_process/novelty.md Study 3, output_process/gaps.md METH-001

| Evaluator Pair | Fleiss' κ (Factual Tasks) | Fleiss' κ (Creative Tasks) | Agreement Level |
|:---|:---:|:---:|:---|
| Gemini × GPT-4o (Azure) | 📝 | 📝 | 📝 |
| Gemini × Qwen3 14B (Local) | 📝 | 📝 | 📝 |
| Gemini × Phi 4 RP (Local) | 📝 | 📝 | 📝 |
| GPT-4o × Qwen3 14B | 📝 | 📝 | 📝 |
| GPT-4o × Phi 4 RP | 📝 | 📝 | 📝 |
| Qwen3 14B × Phi 4 RP (both local) | 📝 | 📝 | 📝 |
| All evaluators (cloud + local) | 📝 | 📝 | 📝 |

**Interpretation:** κ > 0.6 = Substantial agreement, κ > 0.8 = Almost perfect.

**Key Research Question:** Does using local quantized models (Q4/Q6) as evaluators produce comparable agreement to full-precision cloud models?

### 4.4 Multi-Model Pivot Report Sample

**Generation models (Local):** All 6 LM Studio models. **Evaluator models:** Gemini (cloud), GPT-4o (Azure), Qwen3 14B (local as evaluator).

| Generation Model ↓ \ Evaluator → | Gemini Score | GPT-4o Score | Qwen3 14B Score | OpenRouter Score | Total | Grade |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| Qwen3 14B | 📝 | 📝 | N/A (self) | 📝 | 📝 | 📝 |
| GPT-OSS 20B | 📝 | 📝 | 📝 | 📝 | 📝 | 📝 |
| Llama 3.1 8B | 📝 | 📝 | 📝 | 📝 | 📝 | 📝 |
| MN 12B Lyra v1 | 📝 | 📝 | 📝 | 📝 | 📝 | 📝 |
| Gemma 3 12B | 📝 | 📝 | 📝 | 📝 | 📝 | 📝 |
| Phi 4 Reasoning Plus | 📝 | 📝 | 📝 | 📝 | 📝 | 📝 |

---

## 5. End-to-End System Performance

> *Inferred from:* cross_module/mathematics.md §1, cross_module/architecture.md §2

### 5.1 Full Pipeline Timing Breakdown

| Phase | Module(s) | Time (s) | % of Total |
|:---|:---|:---:|:---:|
| LLM Provisioning | llm_factory | 📝 | 📝 |
| Crew Assembly | crew_forge | 📝 | 📝 |
| Crew Execution | crew_forge + crew_monitor | 📝 | 📝 |
| JSON Sanitization | output_process | 📝 | 📝 |
| Rubric Scoring | output_process | 📝 | 📝 |
| Z-Score Grading | output_process | 📝 | 📝 |
| Pivot Consolidation | output_process | 📝 | 📝 |
| **Total End-to-End** | **All** | **📝** | **100%** |

### 5.2 Comparative Framework Analysis

> *Inferred from:* crew_forge/novelty.md Study 4

| Metric | Amsha | CrewAI (Vanilla) | AutoGen | LangGraph |
|:---|:---:|:---:|:---:|:---:|
| Lines of Code for Same Workflow | 📝 | 📝 | 📝 | 📝 |
| Config Files | 📝 | 📝 | 📝 | 📝 |
| Backend Switching (code changes) | 0 | N/A | N/A | N/A |
| Built-in Monitoring | ✅ | ❌ | ❌ | ❌ |
| Built-in Evaluation | ✅ | ❌ | ❌ | ❌ |
| Privacy Enforcement | Dual-layer | None | None | None |
| Provider Count (verified) | 4 tiers (10+ models) | 1–2 | 1–2 | 1–2 |
| Setup Time (min) | 📝 | 📝 | 📝 | 📝 |

---

## 6. Privacy Verification

> *Inferred from:* llm_factory/novelty.md, cross_module/mathematics.md §2

### 6.1 Telemetry Neutralization Verification

| Test | Method | Result |
|:---|:---|:---:|
| OTEL_SDK_DISABLED set? | `os.environ.get(...)` | 📝 (true/false) |
| All Telemetry methods replaced? | `inspect.getmembers()` | 📝 (count replaced / count total) |
| Network capture during execution | Wireshark/tcpdump | 📝 (0 telemetry packets expected) |
| LLM calls work after disabling? | Functional test | 📝 (pass/fail) |

### 6.2 Privacy per Provider Tier

| Provider Tier | Data Leaves Network? | Telemetry Blocked? | Fully Air-Gapped? |
|:---|:---:|:---:|:---:|
| Google Gemini (Direct API) | ✅ Yes | ✅ OTEL disabled | ❌ No |
| GPT-4o (Azure API) | ✅ Yes | ✅ OTEL disabled | ❌ No |
| OpenRouter (Free) | ✅ Yes | ✅ OTEL disabled | ❌ No |
| LM Studio (Local) | ❌ No | ✅ OTEL disabled | ✅ Yes |

---

## Notes

- Replace all `📝` markers with your actual empirical data
- Include error bars (±) for any measurement with multiple trials
- Cite the exact environment and versions used (GPU model, VRAM, LM Studio version)
- All suggested experiments align with gaps identified in the module gap analyses
- **Local models:** Note the quantization format (Q4_K_M, Q6_K, etc.) as it affects quality vs. speed trade-off
- **OpenRouter:** Document which free models were available at time of testing, as the free tier rotates
