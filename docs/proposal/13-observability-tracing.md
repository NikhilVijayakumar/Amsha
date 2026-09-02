# Proposal 13 — Observability: Native Tracing vs. the Event Bus

| | |
|---|---|
| **Status** | ✅ Done — tracing passthrough wired, default off, verified end-to-end through the YAML path with a real kickoff |
| **Priority** | New — requested directly |
| **Risk** | Low for adoption itself; **the decision it forces (cloud vs. local) is the real risk to get right** |
| **Effort** | Small (it's mostly a decision + a flag, not new plumbing) |
| **Depends on** | [09](09-event-observability-upgrade.md) (already done — this proposal is about what sits *alongside* it, not a replacement) |

## Execution Log (2026-09-02)

- `CrewData.tracing: Optional[bool] = None` added — passthrough to `Crew(tracing=...)`.
- `CrewBuilderService.build()` conditionally passes `tracing` only when explicitly set (not `None`).
- `AtomicCrewFileManager.build_atomic_crew()` reads `tracing` from `crew_def` in `job_config.yaml`.
- Default is `None` (off) — matches the proposal's "do not enable by default" requirement.
- 2 new tests in `test_crew_builder_service.py` (`test_build_crew_with_tracing_enabled`, `test_build_crew_tracing_default_none`).
- `AmshaEventListener` remains Amsha's primary, default observability path (proposal 09).

### Bug found + fixed while adding a real example (2026-09-02)

The passthrough above was unreachable from actual `job_config.yaml` files: `AmshaJobConfig`'s strict-validation schema (`CrewDefinition` in `amsha_job_config.py`) never declared a `tracing` field, so `ConfigurationManager.load_from_yaml(...).model_dump()` silently dropped a YAML-authored `tracing: false`/`true` before `AtomicCrewFileManager` ever saw it — `crew_def.get("tracing")` always returned `None`. Only a caller constructing `CrewData` directly in Python (bypassing the YAML path entirely) could actually exercise this. Fixed by adding `tracing: Optional[bool] = None` to `CrewDefinition`, with matching tests in `test_amsha_job_config.py` (`test_tracing_false_round_trips`, `test_tracing_true_round_trips`, plus the `tracing` assertion added to `test_full_job_config_keeps_crew_fields`). `example/crew_forge/example_config/job_config.yaml` now sets `tracing: false` explicitly on `copy_crew`, and `verify_capability_example.py` asserts `crew.tracing is False` at build time and confirms the runtime "Tracing is disabled" banner on `--kickoff` — this is the first real (non-unit-test) exercise of the field end-to-end through the YAML config-as-code path.

## The core finding: these are two independent, non-overlapping systems

CrewAI's own observability-overview page documents Performance Monitoring / Quality Assurance / Cost Management as categories, lists nine third-party tracing integrations (Langfuse, Arize Phoenix, MLflow, etc.), and **does not mention the event bus at all**. CrewAI's native **Tracing** feature and the **event bus** (`CrewAIEventsBus`/`BaseEventListener`, which [09](09-event-observability-upgrade.md) already adopted) are documented completely separately, with no stated relationship. Don't assume tracing is "built on" the event bus or that adopting one gets you the other — treat this as a second, independent capability to evaluate on its own terms.

## What native Tracing actually is — and the part that matters most

- **Enable**: `Crew(tracing=True)` / `Flow(tracing=True)`, or `CREWAI_TRACING_ENABLED=true` (env/`.env`).
- **Captures**: agent reasoning, task sequencing/timing, tool calls + outputs, **full LLM prompts and responses**, performance metrics, error/stack traces.
- **Viewing: exclusively the CrewAI AMP cloud dashboard (`app.crewai.com`). There is no local or self-hosted viewer for this feature.** This is a hard cloud dependency, not an optional extra — enabling tracing means Amsha-built crews' full prompt/response content leaves the local machine and goes to CrewAI's hosted platform, gated behind a free `crewai login` account.
- **Privacy/cost**: not addressed on CrewAI's own tracing page. Worth flagging from broader context: CrewAI's general telemetry has a kill switch (`OTEL_SDK_DISABLED=true`, which Amsha's `LLMUtils.disable_telemetry()` already sets), but **it's unclear whether that switch governs the tracing feature specifically** — no dedicated opt-out env var is documented for tracing itself. Separately, CrewAI's ToS reportedly claims broad rights to use AMP-platform Customer Data for model training. No published per-trace or per-seat pricing was found.

This is a **real due-diligence item**, not a minor caveat: since Amsha's example runs already showed `tracing=True` capturing full prompt/response content (confirmed in the live example runs done in this session, where the "Tracing Status" panel appeared with tracing disabled by default), turning this on for any Amsha deployment that touches client data or proprietary prompts needs an explicit decision, not a default.

## Proposal

1. **Do not enable native tracing by default anywhere in Amsha.** `CrewData` should not set `tracing=True` unless a consuming application explicitly opts in — this mirrors the same caution already applied to memory ([04](04-memory-adoption.md)'s "don't wire memory on by default") and checkpointing ([05](05-checkpointing-consolidation.md)), for a stronger reason: memory/checkpoint change cost and latency, but tracing changes **where your data goes**.
2. Add `tracing: Optional[bool] = None` to `CrewData` (passthrough to `Crew(tracing=...)`, same conditional-pass-through pattern used throughout [08](08-agent-task-capability-expansion.md)) purely so a consumer *can* opt in via `job_config.yaml` if they've made an informed choice — this is enabling capability, not endorsing default use.
3. **Document the cloud dependency and data-sensitivity implications prominently** wherever this field is documented (`About.md`, `functional.md`) — a one-line YAML flag shouldn't be the only signal a developer gets before their full prompts start leaving the machine. State plainly: enabling this requires a `crewai login`, sends full prompt/response content to CrewAI's hosted dashboard, and has undocumented data-retention/training-use terms.
4. **Keep [09](09-event-observability-upgrade.md)'s `AmshaEventListener` as Amsha's primary, default observability path** — it's local, self-hosted-friendly, already integrated with Amsha's own logging pipeline, and captures the same categories of information (task/tool/LLM timing, crew and flow lifecycle) without a cloud round-trip. Native tracing is additive for teams that specifically want CrewAI's hosted trace UI, not a replacement for what's already shipped.
5. Third-party integrations (Langfuse, Arize Phoenix, MLflow, etc.) are out of scope for this proposal — they're each a separate integration decision with their own data-handling story, not something to bundle into a blanket "observability" pass. Revisit individually if a specific one becomes a real ask.

## What NOT to do

- Don't default `tracing=True` anywhere, in examples or in `CrewData`'s defaults — the whole point of this proposal is that this decision needs to be explicit, not a convenience default.
- Don't conflate this with [09](09-event-observability-upgrade.md) — they're different systems with different data-locality guarantees; adopting the passthrough field here doesn't reduce the value of what 09 already built, and 09 doesn't make this proposal redundant.
- Don't build Amsha-side tooling to view or export trace data — that's CrewAI AMP's job if a user opts in; Amsha's role here is just the opt-in switch and the warning label.
