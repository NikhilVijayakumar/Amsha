# Checkpointing and Recovery

## Purpose

Defines the core rules for **checkpointing and recovery** in Amsha.

> **Checkpointing preserves enough durable execution state and artifact references to resume a workflow safely from a defined recovery boundary.**

Checkpointing is a **reliability mechanism**, not a second state-management system.

---

# 1. Checkpoint

A checkpoint is a durable snapshot of the information required to resume an execution: `Process A → Checkpoint → Process B → Process C`. If Process C fails, execution resumes from the checkpoint rather than necessarily restarting from Process A.

---

# 2. Why Checkpointing Exists

Valuable when: execution is long-running, processes are expensive, external operations have completed, human approval creates a pause, recovery from failure is required, intermediate artifacts are expensive to reproduce. Unnecessary when restarting the whole workflow is cheap and safe.

---

# 3. Checkpoint Is Not State

Flow State = current runtime condition; Checkpoint = durable recovery point. A checkpoint may contain a selected subset of state, not every runtime detail.

---

# 4. Checkpoint Boundary

Create checkpoints at meaningful recovery boundaries: expensive Process completed, important Artifact created, external side effect completed, human approval completed, major workflow stage completed, before a risky operation. Avoid checkpointing every tiny operation.

---

# 5. Checkpoint Placement

`Generate Chapter → Checkpoint → Evaluate Chapter → Checkpoint → Human Approval → Checkpoint → Publish`. Correct placement depends on recovery cost and side effects.

---

# 6. Checkpoint Contents

Normally preserve: execution_id, flow_id, flow_version, current/recovery process, required Flow State, process outputs, artifact references, iteration counters, decisions, approval state, relevant failure information. Not unnecessary large artifacts.

---

# 7. Artifact References

Prefer references over embedded artifacts (per `15-files-and-artifacts.md`):

```yaml
checkpoint:
  artifacts:
    - id: chapter_07
      version: "3"
      reference: artifacts/chapter_07_v3.md
```

---

# 8. Checkpoint Version

Identify the Flow version it was created from:

```yaml
checkpoint:
  flow:
    id: chapter_production
    version: "1.2"
```

Recovery against an incompatible Flow version must not happen silently.

---

# 9. Recovery

Restoring an execution from a valid checkpoint: `Failure → Identify Recovery Boundary → Load Checkpoint → Validate Checkpoint → Restore State → Resume`.

---

# 10. Recovery Must Be Explicit

Amsha should know where recovery starts, what state is restored, which artifacts are required, which Process executes next, and what completed work must not be repeated. Avoid implicit "try again from somewhere."

---

# 11. Recovery Validation

Before resuming: checkpoint exists, Flow version compatible, state valid, artifact references valid, required artifacts accessible, dependencies valid, permissions valid, recovery Process valid. If unsatisfied, fail explicitly or escalate.

---

# 12. Recovery Point vs Restart Point

Not necessarily identical. The checkpoint may represent state **after Process A**, while recovery starts by executing Process B (`Checkpoint → Validation → Recovery preparation → Process B`).

---

# 13. Completed Work

Recovery preserves valid completed work. If the checkpoint is after Process B (`A → completed, B → completed, C → failed`), recovery just runs Process C — no reason to regenerate A/B unless their outputs are no longer valid.

---

# 14. Artifact Validity During Recovery

An artifact valid at checkpoint time may no longer be usable. Check reference, version, integrity, availability, dependency validity before relying on it.

---

# 15. Stale Checkpoints

A checkpoint becomes stale when: required artifacts deleted, external dependencies/config/permissions changed, Flow version changed, required capabilities unavailable. Detect these rather than blindly restoring.

---

# 16. Recovery and Version Compatibility

Preferred: `Checkpoint Flow v1.2 → Recover with Flow v1.2`. Potentially unsafe: recover with unrelated Flow v2.0. If migration is supported, make it explicit and validated.

---

# 17. Recovery and Idempotency

Recovery often re-executes an operation, so side-effecting operations need defined idempotency (`Publish → network failure → uncertain → recovery`). The system must not blindly publish twice.

---

# 18. Recovery and External Side Effects

External side effects (send email, publish content, create DB record, invoke external API, submit job) need defined recovery behavior: idempotent retry, status verification, compensation, human confirmation, or manual recovery.

---

# 19. Recovery vs Retry

**Retry** (`Process → Failure → Retry`) repeats a failed operation within the current execution. **Recovery** (`Execution → Failure → Checkpoint → Restore → Resume`) restores execution from a durable checkpoint. A recovery may contain retries.

---

# 20. Recovery and Iteration

Iteration is a workflow decision (revision loop: `Generate → Evaluate → Needs Revision → Revise → Evaluate`). Recovery is a runtime failure restore (`Evaluate → Runtime failure → Restore → Resume Evaluate`). Don't confuse revision loops with recovery.

---

# 21. Human Gates

Human approval is a natural checkpoint boundary (`Generate → Evaluate → Human Approval → Checkpoint → Publish`). Once received, the approval decision should be durably associated with the relevant artifact version.

---

# 22. Checkpoint Frequency

Balance: recovery cost, checkpoint storage cost, execution duration, artifact size, reproducibility requirements, failure probability. More checkpoints are not automatically better.

---

# 23. Checkpoint Minimality

Contain the **minimum sufficient recovery information**. Prefer `state + references + decisions` over `entire execution history + entire artifacts + all prompts`.

---

# 24. Checkpoint Integrity

Validate the checkpoint itself: schema valid, execution valid, Flow version valid, state valid, artifact references valid, required fields present.

---

# 25. Schemas: Checkpoint, Recovery Plan, Outcomes, Events

**Checkpoint:**

```yaml
checkpoint:
  id: ""
  execution_id: ""
  flow: { id: "", version: "" }
  created_at: ""
  recovery: { resume_process: "", reason: "" }
  state: {}
  process_outputs: {}
  artifacts:
    - id: ""
      version: ""
      reference: ""
  decisions: {}
  iterations: { counters: {}, limits: {} }
  approvals: { status: "", decision: "" }
  integrity: { hash: "" }
  status: ""
```

**Recovery plan:**

```yaml
recovery_plan:
  checkpoint_id: ""
  validate:
    state: true
    artifacts: true
    permissions: true
  resume:
    process_id: ""
  behavior:
    invalid_checkpoint: ""
    missing_artifact: ""
    version_conflict: ""
    side_effect_uncertain: ""
```

**Recovery outcomes:** `RESUMED, RECOVERY_FAILED, CHECKPOINT_INVALID, ARTIFACT_UNAVAILABLE, VERSION_CONFLICT, MANUAL_RECOVERY_REQUIRED, TERMINATED`.

**Checkpoint events:** `checkpoint.created, checkpoint.validated, checkpoint.restored, checkpoint.invalid, recovery.started, recovery.completed, recovery.failed` — belong to execution observability.

---

# 26. Recovery Flow

`Execution Failure → Classify Failure → Recovery Required? {NO → Retry/Fail/Escalate | YES → Locate Checkpoint → Validate Checkpoint → Validate Artifacts → Validate Version → Restore State → Resume Process → Continue Flow}`.

---

# 27. Recovery Safety Rules

1. A terminal execution cannot be resumed accidentally.
2. Invalid checkpoints cannot be restored.
3. Missing required artifacts block recovery.
4. Incompatible Flow versions block recovery unless migration is explicit.
5. Side effects are not blindly repeated.
6. Retry limits remain enforced after recovery.
7. Iteration limits remain enforced after recovery.
8. Human approval decisions remain associated with the correct artifact/version.
9. Recovery does not bypass required validation or human gates.
10. Recovery remains traceable to the original execution.

---

# 28. Recovery and Execution Identity

A recovered execution preserves its lineage:

```yaml
execution:
  id: exec_001
  recovery:
    recovered: true
    checkpoint_id: checkpoint_004
```

If a new runtime execution ID is created, the relationship to the original execution must remain explicit.

---

# 29. Checkpoint Retention

Keep a checkpoint available as long as recovery requires it; when no longer needed, archive/delete. Cleanup must account for dependent artifacts.

---

# 30. Anti-Patterns

**Checkpoint Everything** — unnecessary storage and complexity. **Store Entire Artifacts** — use references. **Ignore Version Compatibility** — can resume against an incompatible architecture. **Retry Side Effects Blindly** — can duplicate external effects. **Treat Every Failure as Recoverable** — some require termination or human intervention. **Use Checkpoints as Long-Term Memory** — checkpointing is for execution recovery, not general history. **Resume Without Validation** — a stale checkpoint can produce invalid execution.

---

# 31. Minimal Amsha Model

```
EXECUTION
  ├── CURRENT STATE
  ├── EVENTS
  └── CHECKPOINT → {State, Decisions, Process Outputs, Artifact References → ARTIFACTS}
```

---

# 32. Final Principle

> **Checkpoint only at meaningful recovery boundaries, persist the minimum state required to resume safely, reference artifacts rather than embedding them, validate checkpoints before restoration, and explicitly control retries and external side effects.**

`Failure → Known Recovery Point → Validated Restore → Safe Resume → Continue Toward Goal`.

Checkpointing should make long-running Amsha workflows **recoverable without turning runtime state into a second database, duplicating artifacts, or silently changing workflow semantics.**