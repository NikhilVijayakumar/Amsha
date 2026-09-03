# Proposal 14 — LLM Lifecycle Management (LM Studio, Local Only)

| | |
|---|---|
| **Status** | ✅ Done — lifecycle load/unload, retry, global context default, and model capability tagging shipped |
| **Priority** | New — requested directly |
| **Risk** | Medium — makes real HTTP calls that unload/load models on a local server before a crew runs; wrong config could unload a model another process depends on |
| **Effort** | Medium |
| **Depends on** | Nothing in `crew_forge` — this is `llm_factory`-only. Follows the same "opt-in, off by default" precedent as [04](archive/04-memory-adoption.md)/[05](archive/05-checkpointing-consolidation.md)/[13](13-observability-tracing.md) |
| **Scope** | **LM Studio only. Local server only.** Explicitly not Ollama, not any cloud provider (OpenAI, Azure, Gemini, OpenRouter) |

## Execution Log (2026-09-03)

- `LMStudioLifecycleConfig` + `LMStudioLifecycleClient` (`llm_factory/adapters/lmstudio_lifecycle_client.py`, stdlib `urllib` only, no new dependency) built and wired into `LLMBuilder.build()`, gated by `isinstance(...) and .enabled` so every pre-existing test/config with no `lmstudio_lifecycle` field is an untouched no-op.
- **Live-tested against a real local LM Studio server**, not just mocks: load (`google/gemma-4-12b-qat`, ~18s cold), reuse-when-context-matches (no reload), reload-on-context-mismatch (unload+load, ~17.5s), explicit unload — all confirmed correct.
- **Real bug found and fixed from that live test**: the original 30s default HTTP timeout was too short for a real multi-GB model load. `load()` now uses a separate, longer timeout (300s default) from `list`/`unload` (still 30s) — `LMStudioLifecycleClient.__init__(base_url, timeout=30.0, load_timeout=300.0)`.
- **Open question resolved**: went with **explicit `context_length`** (option A). Auto-detect (option B) was not built — stays out of scope for the reason already given (couples behavior to live external state).
- **Retry added**: `LMStudioLifecycleConfig.max_load_retries: int = 0`, `load_retry_delay_seconds: float = 2.0`. `load()` retries only the network call itself (transient `LMStudioLifecycleError`, e.g. LM Studio briefly busy); the post-load context-length-mismatch check still raises immediately without retrying, since retrying the same request against the same misconfiguration can't fix it. Default `0` retries — today's fail-fast behavior is unchanged unless a caller opts in.
- **Global context-length default added**: `LLMSettings.lmstudio_context_length_default: Optional[int] = None`. Resolution order in `LLMBuilder.build()`: per-model `lmstudio_lifecycle.context_length` (if set) → this global default (if set) → `None` (defers to LM Studio's own per-model default, whatever that happens to be locally — this is where an unconfigured install's "40000 by default" comes from). Avoids repeating the same `context_length` across every model entry in `llm_config.yaml`.
- **Model capability tagging added** — a related but separate, provider-agnostic addition (works for any `LLMModelConfig`, not just LM Studio ones): `LLMModelCapabilities` (`reasoning`, `vision`, `tool_use`, all `bool = False`) as an optional `LLMModelConfig.capabilities` field, plus `LLMSettings.get_model_key_for_capability(use_case, capability, model_key=None)` and `LLMBuilder.build_for_capability(llm_type, capability, model_key=None)`. Declarative only — the config author tags what a model is good for; nothing is auto-detected from LM Studio's own `capabilities`/`reasoning` metadata (which does exist and could be cross-checked later, but isn't today — see "What NOT to do"). Lets a use case with several models be selected by "give me the one tagged for reasoning" instead of hardcoding a `model_key` at every call site that needs it. Raises a clear `ValueError` (listing valid capability names) on an unknown capability string or no match, rather than silently returning nothing.
- 26 new tests: `tests/unit/llm_factory/adapters/test_lmstudio_lifecycle_client.py` (client + retry, mocked HTTP), `tests/integration/llm_factory/test_lmstudio_lifecycle_live.py` (real LM Studio, auto-skips if unreachable), additions to `test_llm_builder_enhanced.py` and `test_llm_settings.py`. Zero regressions in the pre-existing suite (3 pre-existing unrelated failures confirmed present on `master` before this work, untouched by it).
- MCP verification followed, per the "real field first, governance after" rule: `llm_model` component type added to `amsha_mcp`'s `verification.py` with 4 checks (missing `base_url`, non-local `base_url`, `model_id`/`model` confusion, unset `context_length`) — see `mcp/docs/proposal/03-plan-and-crew-verification.md`.

## Why this is scoped to LM Studio, local, and nothing else

Confirmed by reading `llm_factory` source (`llm_model_config.py`, `llm_builder.py`, `llm_settings.py`) and `docs/feature/llm_factory/About.md`: Amsha has no `provider` field at all today. Every backend — Ollama, LM Studio, Azure, Gemini, OpenRouter — is just an OpenAI-compatible `base_url` + `model` string (litellm-prefixed, e.g. `lm_studio/openai/gpt-oss-20b`) passed straight into `crewai.LLM(...)`. `LLMBuilder.build()` never talks to the backend except through that one chat-completions call.

A model-lifecycle API (list loaded models, load a model, unload a model, control per-load context length) is **not part of the OpenAI-compatible surface**. It is a separate, vendor-specific management API:

- **LM Studio**: `GET/POST http://<host>:<port>/api/v1/models`, `/api/v1/models/load`, `/api/v1/models/unload` — a different path prefix (`/api/v1/...`) on the *same* host:port as the OpenAI-compatible `/v1/...` endpoints Amsha already calls.
- **Ollama**: a different, incompatible mechanism (`keep_alive` in the chat request, `ollama stop`).
- **Cloud providers**: no such concept — nothing is "loaded" locally, so unload/load is meaningless.

Building this generically now would mean inventing an abstraction over one real backend and three imagined ones. Don't. This proposal adds an **LM-Studio-specific, explicitly-named, opt-in adapter** — not a new generic field on `LLMModelConfig` that quietly implies every provider supports it. If Ollama-lifecycle or another backend becomes a real need later, that's a separate proposal with its own vendor API, not an extension of this one.

## The problem

Today, running an Amsha crew against LM Studio assumes whatever model is currently loaded in LM Studio is the right one, with the right context length, already. Nothing in Amsha checks this. Two failure modes follow from that:

1. **Wrong model loaded.** A developer switches models in the LM Studio UI for a different task, forgets to switch back, then reruns an Amsha crew — the crew silently runs against the wrong model. LM Studio's OpenAI-compat endpoint will happily serve a request for `"model": "gemma-3-12b-it"` by auto-loading it if configured to (or erroring if not) — behavior Amsha has no visibility into either way.
2. **Wrong context length loaded.** LM Studio's `/api/v1/models/load` accepts `context_length` as a *load-time* parameter — it is fixed for the lifetime of that loaded instance and cannot be changed without unloading and reloading. A model already loaded with `context_length: 4096` silently truncates a crew that needs 16k, with no error from Amsha's side — the OpenAI-compat call just proceeds against whatever context the instance was loaded with.

Both are exactly the kind of "looks like it worked, quietly did the wrong thing" failure Amsha's other guardrail-shaped features (task `guardrail`, checkpoint `on_events`, tracing's opt-in warning) exist to prevent.

## Proposal

Add an opt-in `LMStudioLifecycleConfig` reachable from `LLMModelConfig`, and a lifecycle check that runs **before `LLMBuilder.build()` constructs the `crewai.LLM(...)` instance** — i.e., before any crew that uses this model config can start.

```yaml
# llm_config.yaml
llm:
  creative:
    default: gpt
    models:
      gpt:
        base_url: "http://localhost:1234/v1"
        model: "lm_studio/openai/gpt-oss-20b"
        api_key: "lm_studio"
        lmstudio_lifecycle:
          enabled: true
          model_id: "openai/gpt-oss-20b"   # LM Studio's own model key, from GET /api/v1/models
          context_length: 16384            # optional — see open question below
          unload_other_models: true        # guardrail: only this model resident before build
```

`LLMModelConfig` gains one new optional field:

```python
class LLMModelConfig(BaseModel):
    base_url: Optional[str] = None
    model: str
    api_key: Optional[str] = None
    api_version: Optional[str] = None
    output_config: Optional[LLMOutputConfig] = None
    lmstudio_lifecycle: Optional[LMStudioLifecycleConfig] = None   # new, opt-in
```

```python
class LMStudioLifecycleConfig(BaseModel):
    enabled: bool = False
    model_id: str                              # LM Studio's model key (GET /api/v1/models -> key)
    context_length: Optional[int] = None        # explicit only — see "Open question" below
    unload_other_models: bool = True
    max_load_retries: int = 0                   # retries the /models/load network call only
    load_retry_delay_seconds: float = 2.0
```

Plus one field on `LLMSettings` (not per-model — a use-case-wide fallback):

```python
class LLMSettings(BaseModel):
    llm: Dict[str, LLMUseCaseConfig]
    llm_parameters: Dict[str, LLMParameters]
    lmstudio_context_length_default: Optional[int] = None   # global fallback when a model omits context_length
```

`enabled: false` or the field being absent entirely means **zero new behavior** — `LLMBuilder.build()` runs exactly as it does today. This mirrors `CrewData.checkpoint`/`tracing`'s conditional-pass-through pattern exactly.

### Guardrail 1: before loading — check what's loaded, unload if needed, load the target

New method, e.g. `LMStudioLifecycleClient.ensure_loaded(model_id, context_length, unload_other_models)`, called from `LLMBuilder.build()` only when `model_config.lmstudio_lifecycle and model_config.lmstudio_lifecycle.enabled`:

1. `GET /api/v1/models` — read `loaded_instances` across all models.
2. If the target `model_id` is already loaded:
   - If `context_length` is unset, or the loaded instance's `config.context_length` already matches → done, reuse the running instance (no unnecessary reload).
   - If it's loaded with a **different** context length than requested → this is the guardrail firing: `POST /api/v1/models/unload` that instance, then `POST /api/v1/models/load` fresh with the requested `context_length`. LM Studio has no in-place context-length change; unload+reload is the only path.
3. If the target is not loaded at all → `POST /api/v1/models/load` with `model_id` and `context_length` (if set), `echo_load_config: true` so the actual applied config is checked against the request, not assumed.
4. If `unload_other_models: true` and a **different** model instance is loaded → unload it first, per FR-CREW-style "only the intended thing is resident" guardrail. Default `true` because the common case (a dev box running one crew at a time) benefits from not silently accumulating loaded models across a session; a shared-instance setup should set it `false` explicitly.

### Guardrail 2: before running the crew — re-verify, don't just trust step 1

Because `ensure_loaded()` runs inside `LLMBuilder.build()`, and `build()` runs every time a crew is constructed (not cached across runs), this check is inherently re-run "before running the crew" for every kickoff — not a separate mechanism. No additional wiring needed in `FileCrewOrchestrator` beyond calling the existing `LLMBuilder.build()` path, which it already does.

## Open question: explicit `context_length` vs. auto-detect — RESOLVED (see Execution Log)

Two options were weighed:

- **A — explicit only** (as sketched above): `context_length` is set in `llm_config.yaml` or left `None` (meaning "don't care, accept whatever's loaded"). Matches Amsha's existing philosophy everywhere else — `FR-CREW-10`/`FR-CREW-11`'s fields are all explicit-optional, nothing is inferred from a live external system. Con: a developer has to know and maintain the right number instead of it "just working."
- **B — auto-detect**: read the model's `max_context_length` from `GET /api/v1/models` and pass that as `context_length` on load, with no config needed. Con: couples Amsha's runtime behavior to whatever LM Studio reports as the model's max at that moment — a quantization/format change, or an LM Studio update, changes crew behavior with no corresponding change in Amsha's own config. That's the same "silent drift" class of problem `FR-SYNC`/Git-as-source-of-truth exists to prevent elsewhere in Amsha.

**Leaning A, with `context_length: None` as the explicit "I don't care" escape hatch** — consistent with treating config as the source of truth rather than live-probing external state. Not settling this in the proposal; flagging it for a decision before implementation.

## Non-negotiables

- **Off by default.** No `lmstudio_lifecycle` field, or `enabled: false`, means zero new HTTP calls and zero change to today's `LLMBuilder.build()` behavior.
- **LM Studio and local only.** Do not attempt to detect "is this LM Studio" from the `base_url` — require the explicit `lmstudio_lifecycle` block so a user opts in knowingly, the same reasoning [13](13-observability-tracing.md) applied to tracing ("this decision needs to be explicit, not a convenience default").
- **Fail loud, not silent.** If the LM Studio management API is unreachable, or `echo_load_config`'s returned config doesn't match what was requested, raise — don't fall back to building the `LLM` against an unverified state. Matches `FR-CREW-06`'s "unknown tool raises `ValueError` at build time" precedent.
- **Document the latency and concurrency cost.** Loading a model is not free — LM Studio's own docs show multi-second `load_time_seconds` for real models. A crew with `lmstudio_lifecycle.enabled: true` pays that cost on every build that needs a swap. Also document plainly: this assumes single-consumer use of the LM Studio instance; two Amsha processes (or a human using the LM Studio UI) sharing one instance with `unload_other_models: true` will fight each other. Not solved here — called out as a known limitation.

## What NOT to do

- Don't add a generic `provider` enum or a generic `lifecycle` field on `LLMModelConfig` that implies Ollama/Azure/OpenRouter support the same thing — they don't. Name the field `lmstudio_lifecycle` specifically.
- Don't infer "this is LM Studio" from the `base_url` string (e.g. `localhost:1234`) — require explicit opt-in config instead of a guess.
- Don't try to solve multi-process/multi-consumer coordination over one LM Studio instance in this proposal — out of scope, documented as a limitation.
- Don't wire MCP verification for this until the field actually exists in `LLMModelConfig` — same order as every other capability this session: real field in Amsha core first, MCP governance after.
- Capability tags (`reasoning`/`vision`/`tool_use`) are declarative only — don't auto-populate them from LM Studio's own `GET /api/v1/models` `capabilities`/`reasoning` metadata. That metadata is real and could ground an auto-tag feature later, but it's LM-Studio-only and live-probed, which would make `capabilities` behave differently depending on which provider a model config happens to point at — same "silent drift" argument as the auto-detect context-length option above. Keep it a config-author's explicit statement.
- Don't build silent model-fallback (auto-switch to a different model if the configured one won't load) — discussed and explicitly deferred. If wanted later, it must be an explicit, user-configured `fallback_model_id`, never an automatic guess.

## Testing bar

- `ensure_loaded()` against a real local LM Studio instance (integration test, skipped/marked if LM Studio isn't running in CI): target not loaded → loads it, `echo_load_config` context length matches request.
- Target already loaded with matching context → no unload/reload call made (assert no `POST /api/v1/models/unload` happened).
- Target loaded with mismatched context → unload then reload observed, final state matches requested context.
- `unload_other_models: true` with a different model loaded → that other instance unloaded before target load.
- `enabled: false` (or field absent) → zero calls to `/api/v1/models*`, `LLMBuilder.build()` behavior byte-identical to today.
- LM Studio unreachable with `enabled: true` → raises, does not silently proceed to build the `LLM`.
