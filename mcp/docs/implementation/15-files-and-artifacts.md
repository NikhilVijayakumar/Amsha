# Files and Artifacts

## Purpose

Defines how **Files, Artifacts, References, Storage, Context, and Execution Outputs** are modeled and engineered within Amsha architectures.

> **Files and Artifacts are data boundaries, not merely prompt content. Store large or persistent outputs as artifacts, pass references between Processes, and inject only the information required for the current execution.**

Extends: `03`, `05`, `06`, `08`, `09`, `10`, `11`, `13`, `14`.

---

# 1. Core Distinction

`File = a concrete data representation` · `Artifact = a meaningful execution-related data object` · `Reference = a pointer to an Artifact or external data` · `Context = information selected for current execution` · `Input = data explicitly accepted by a Process/Task contract` · `Output = data produced by an execution` · `State = workflow information controlling execution`.

These may overlap physically but must remain distinct architecturally.

**File** (examples: `chapter.md`, `review.json`, `character.png`, `voice.wav`, `scene.mp4`, `dataset.csv`) answers: "What physical or logical file contains this data?"

**Artifact** (Generated screenplay, Evaluation report, Character reference image, Audio generation, Research dataset, Compiled JSON, Rendered video) answers: "What meaningful piece of work or data exists in the workflow?" An Artifact may map to one or many Files.

**Artifact vs File** example: Artifact `Chapter 7 Review` → Files `chapter_07_review.json`, `.md`, `chapter_07_evidence.json`. The Artifact is the logical object; Files are concrete representations.

**Reference** (local path, URI, object-store key, database identifier, external resource identifier, artifact ID):

```yaml
artifact:
  id: chapter_07_review
  reference: artifacts/reviews/chapter_07.json
```

---

# 2. Why References Matter

Large artifacts should not be repeatedly copied into Flow State, Agent prompts, Task descriptions, Crew context, or Memory.

```
Artifact → Reference → Relevant retrieval → Context
```

This reduces token usage, memory usage, serialization, duplication, and context pollution.

**Artifact-Oriented Architecture** (preferred): `Process A → Artifact → Reference → Process B → Relevant extraction → Context`, instead of copying the entire artifact into Flow State then into Process B.

---

# 3. Artifact as Process Output

```yaml
process:
  id: generate_chapter
  output:
    name: chapter
    type: artifact
```

The Process contract should define: what is produced, format, schema, location/reference, validation, ownership, lifecycle.

**Artifact as Process Input:**

```yaml
input:
  required:
    - chapter_reference
```

The Process retrieves/inspects the artifact as needed — preferable to treating large artifacts as ordinary scalar inputs.

---

# 4. Artifact References in Flow State

Flow State retains `artifact_id, reference, version, status, metadata` rather than the complete artifact:

```yaml
state:
  artifacts:
    chapter:
      id: chapter_07
      reference: artifacts/chapter_07.md
      version: "3"
```

**Artifact State vs Content:** `chapter_status = GENERATED` + `chapter_reference` (Flow needs this) vs the complete chapter text (the writing Process needs this). They are different.

---

# 5. Lifecycle, Status, Ownership

**Lifecycle:** `REQUESTED → CREATED → VALIDATING → VALID → CONSUMED → ARCHIVED → DELETED`. Not every artifact needs every state.

**Status:** `PENDING, CREATING, CREATED, VALIDATING, VALID, INVALID, PARTIAL, SUPERSEDED, ARCHIVED, DELETED`.

**Ownership:** every important Artifact has an owner — Process, Task, Crew, Flow, External System, or Human:

```yaml
artifact:
  id: chapter_review
  produced_by:
    process: evaluate_chapter
```

Ownership determines responsibility for correctness and lifecycle.

---

# 6. Provenance, Versioning, Identity, Metadata

**Provenance** (preserves auditability):

```yaml
artifact:
  id: chapter_07_review
  provenance:
    produced_by:
      process: evaluate_chapter
      crew: chapter_quality_review
    source_artifacts:
      - chapter_07
      - story_bible_v3
    architecture_version: "2.1"
```

**Versioning** matters for iterations, revisions, human approval, external publication (`chapter_07 v1/v2/v3`).

**Identity:** stable identity independent of physical filename (`id: chapter_07, version: 3, representation: {file: chapters/chapter_07_v3.md}`) so storage can change without changing the logical object.

**Metadata:** id, version, type, format, size, created_at, updated_at, producer, source references, content hash, status, classification, location — retain only what's useful.

**Content hash** (`algorithm: sha256, value: ...`) aids deduplication, integrity checks, reproducibility, cache validation, change detection.

---

# 7. Integrity & Validation

Before an Artifact is consumed, validate: reference exists, file accessible, format valid, schema valid, content not corrupted, version compatible, producer known. Level depends on the Artifact.

**File-type validation** stays deterministic where possible:
- JSON: schema, syntax, required fields, types
- CSV: syntax, columns, types, encoding
- Image: format, dimensions, integrity
- Audio: format, sample rate, channels, duration
- Video: codec, container, resolution, duration, integrity

**File format ≠ semantic validity.** A valid JSON file can contain a semantically incorrect result; both File validation and Output validation may be required.

**Validation pipeline:** `Artifact → File Integrity → Format → Schema → Semantic → Approved`. Not every artifact needs every layer.

**Deterministic validation** (Python) for: file existence, checksum, format, schema, dimensions, duration, required metadata, reference validity. Use semantic Agents only when interpretation is required.

**Semantic validation** example: Deterministic = valid Markdown, required sections present; Semantic = character behavior consistent, narrative arc coherent.

---

# 8. Context Selection & Extraction

A Process should not automatically receive an entire Artifact. Preferred: `Artifact → Determine relevant information → Extract → Context`. Example: `Entire Story Bible → Character-related facts → Character Evaluation Task`.

**Python extraction** (before semantic processing) may pull sections, records, metadata, timestamps, tables, specific scenes/characters/pages.

**Summarization** is useful when the artifact is large, exact fidelity isn't required, and high-level understanding suffices (`Large research corpus → Summary → Agent context`). But summaries must not replace primary evidence when exact evidence is required.

**Evidence references** preserve auditability for semantic decisions:

```yaml
finding:
  issue: character_inconsistency
  evidence:
    - artifact: chapter_07
      location: scene_14
```

**References in Agent context:** prefer passing the reference when the Agent can retrieve via an appropriate mechanism; if the Agent needs actual content, provide the content, not just the reference.

**Artifact access capability:** a reference does not grant read permission — access is separately controlled.

---

# 9. Security & Classification

Consider who produced/read/modified/deletes it, whether it contains sensitive info, where stored, retention duration. **Artifact access is a security boundary.**

**Classification** (project-specific): `PUBLIC, INTERNAL, CONFIDENTIAL, RESTRICTED`; influences access and retention.

**File path security:** do not let unvalidated Agent-generated paths control filesystem operations. Prefer `Agent → Logical Artifact ID → Artifact Manager → Validated Storage Location` over `Agent → arbitrary filesystem path`.

---

# 10. Artifact Manager & Storage

The Artifact Manager represents the logical lifecycle: `create, register, retrieve, validate, version, reference, archive, delete`. The filesystem/object store is physical storage. This decouples application logic from one storage mechanism.

```yaml
artifact:
  id: ""
  storage:
    backend: ""
    location: ""
```

Backends: `local, object_store, database, external_service, artifact_registry`.

**Creation** defines id, type, producer, format, location, version, metadata, status.

**Registration** (when a Tool/external system creates a file): `External Tool → File created → Artifact registration → Artifact ID → Flow State`, making external data part of the architecture. **Creation ≠ Registration** — a file may exist before Amsha registers it.

---

# 11. Consumption, Mutation, Deletion, Retention

**Consumption** declares dependencies:

```yaml
artifact_input:
  id: ""
  required: true
  version: ""
  access: read
```

**Mutation:** prefer immutable versioning (`chapter v1 → revision → chapter v2`) over silent overwrite, for reproducibility and rollback.

**Immutable/superseded:** production outputs should remain independently addressable (`Artifact v1/v2/v3`) for review, approval, publishing, reproducibility, auditing, rollback. Old versions may remain for audit/rollback when superseded.

**Deletion** is explicit: `ACTIVE, ARCHIVED, DELETED`. Consequential artifacts may require authorization, retention policy, human approval, audit record.

**Retention** should be intentional: `temporary, execution-scoped, project-scoped, long-term, archival`. Example: temporary intermediate file → execution lifetime; final screenplay → project lifetime; audit report → long-term.

**Temporary files** must not accidentally become permanent Knowledge/Memory.

**Cleanup** must account for active references, checkpoint dependencies, recovery requirements, audit requirements, retention policy. Do not delete artifacts a checkpoint still needs for recovery.

---

# 12. Artifact & Checkpoint / Flow / Crew / Task / Agent

**Checkpoint** preserves the references needed to resume, not the content:

```yaml
checkpoint:
  process: evaluate_chapter
  artifacts:
    - id: chapter_07
      version: 3
      reference: artifacts/chapter_07_v3.md
```

**Flow** manages references, status, dependencies, decisions — not artifact storage.

**Crew** may produce multiple specialist artifacts (`Narrative/Character/Continuity Review → Artifacts → Synthesis → Final Review Artifact`) and returns the final result to the Process.

**Task** may consume, produce, modify, or validate artifacts — relationships should be explicit.

**Agent** should reason over relevant artifact content, not manage storage: prefer `Agent → Artifact Tool → Artifact` over unrestricted filesystem access.

**Python** handles deterministic management: create, copy, move, rename, validate, hash, serialize, deserialize, convert, index, register — separate from semantic reasoning.

---

# 13. Artifact & Tools / MCP / External

**Tools** may create/consume artifacts (`Image Tool → Image Artifact`, `Audio Tool → Audio Artifact`, `Publishing Tool → Published Artifact/External ID`); the Tool contract should identify the resulting artifact.

**MCP** may create/retrieve/modify external artifacts; the external system remains the source. Preserve the external identifier and provenance (`Agent → MCP Document Tool → External Document → Artifact Registration → Amsha`).

**External Artifact:**

```yaml
artifact:
  id: ""
  source:
    type: external
    system: ""
    external_id: ""
  reference: ""
```

Represents external data without necessarily copying it. Distinguish **Local** (managed by Amsha storage) vs **External** (managed by external system) — lifecycle responsibilities differ.

**Synchronization** (if copied locally): track source, retrieval time, source version, local version, synchronization status — else stale copies become ambiguous. Freshness matters when external data changes (`External document v5` / `Local copy v4` → likely stale).

---

# 14. Dependencies, Invalidation, Lineage

**Dependency graph** for reproducibility/invalidation:

```yaml
artifact:
  id: chapter_07
  depends_on:
    - character_profiles_v3
    - story_bible_v5
```

**Invalidation** is a semantic architecture decision, not a file-timestamp problem: if Story Bible goes v5→v6, must Chapter v3 be revalidated?

**Lineage** (`Input Artifacts → Process → Output Artifact → Downstream Process → New Artifact`) answers "What produced this artifact?" and "Which outputs depend on this source?"

```yaml
artifact_lineage:
  artifact_id: ""
  produced_by:
    process_id: ""
    task_id: ""
    agent_id: ""
    crew_id: ""
  inputs:
    - artifact_id: ""
      version: ""
  transformations:
    - type: ""
      description: ""
  outputs:
    - artifact_id: ""
      version: ""
```

---

# 15. Contracts: Artifact, Input, Output, Validation, Context

**Artifact contract:**

```yaml
artifact:
  id: ""
  type: ""
  version: ""
  producer:
    process_id: ""
    task_id: ""
    agent_id: ""
    crew_id: ""
  representation:
    format: ""
    reference: ""
    size: null
    hash: ""
  status: ""
  access:
    read: []
    write: []
    delete: []
  lifecycle:
    scope: ""
    retention: ""
    expires_at: ""
  provenance:
    inputs: []
    architecture_version: ""
  validation:
    integrity: false
    format: false
    schema: false
    semantic: false
  dependencies:
    upstream: []
    downstream: []
```

**File/Artifact input contract:**

```yaml
file_input:
  id: ""
  artifact_id: ""
  required: true
  accepted:
    formats: []
    mime_types: []
    max_size: null
  validation:
    integrity: true
    schema: false
    semantic: false
  access:
    mode: read
  provenance:
    source: ""
```

**File/Artifact output contract:**

```yaml
file_output:
  artifact_id: ""
  type: ""
  format: ""
  schema: {}
  validation:
    deterministic: []
    semantic: []
  lifecycle:
    scope: ""
    retention: ""
  provenance:
    producer_process: ""
```

**Artifact validation schema:**

```yaml
artifact_validation:
  artifact_id: ""
  version: ""
  existence:
    reference_valid: false
    accessible: false
  integrity:
    hash_valid: false
    corruption_detected: false
  format:
    valid: false
    expected: ""
  schema:
    required: false
    valid: false
  semantic:
    required: false
    valid: false
  provenance:
    producer_known: false
    source_known: false
  dependencies:
    valid: false
    stale: []
  security:
    authorized: false
    classification: ""
  lifecycle:
    valid: false
    retention_valid: false
  findings:
    - id: ""
      severity: ""
      category: ""
      message: ""
      recommendation: ""
  decision:
    status: ""
    action: ""
    rationale: ""
  approved: false
```

**Artifact context contract:**

```yaml
artifact_context:
  artifact_id: ""
  version: ""
  access:
    mode: read
  retrieval:
    strategy: ""
    sections: []
    filters: []
  representation:
    type: ""
    reference: ""
  provenance:
    source: ""
    retrieved_at: ""
  validation:
    integrity: false
    schema: false
```

---

# 16. Transfer Between Processes / Crews / Flows

**Between Processes:** `Process A → Artifact A → Reference → Process B`; validate reference exists, version compatible, access permitted, format/schema compatible, status acceptable.

**Between Crews:** `Crew A → Review Artifact → Crew B → Revision`; Crew B receives only the artifact info its Process requires.

**Across Flow boundaries:** `Flow A → Artifact → Flow B` — cross as an explicit contract, not implicit global context.

---

# 17. Context Budget, LLM, Multimodal

Prefer `Reference → Relevant extraction` over `Complete artifact → Prompt` when the whole artifact is unnecessary — a major token-efficiency mechanism.

**LLMs** should consume only the representation required: Task `identify character contradictions` needs relevant scenes + character facts, not the entire project archive.

**Multimodal artifacts** (text, image, audio, video, structured data, 3D assets, documents): use the appropriate representation — `Image Artifact → Vision-capable Agent` rather than converting everything to text.

**Conversion** is deterministic (CSV→JSON, PNG→JPEG, WAV→normalized WAV → Python/Tool) or semantic (Video→narrative scene description → Agent). Match the mechanism to the transformation.

**Transformation chain** stays traceable: `Source Artifact → Python/Tool → Intermediate → Agent → Semantic Artifact → Python validation → Final Artifact`.

---

# 18. Failure, Partial, Atomicity, Concurrency

**Failures:** missing artifact, invalid reference, corrupt file, unsupported format, schema failure, semantic validation failure, permission failure, storage failure, version conflict, stale dependency, partial artifact — each maps to the Process failure plan.

**Partial artifacts:** distinguish valid partial vs invalid partial vs recoverable intermediate vs final artifact. A partially generated file (e.g. video render at 80%) is not automatically a valid output.

**Atomicity:** make final artifacts visible only after successful completion (`write temporary artifact → validate → commit/register`) rather than incremental writes a consumer sees incomplete. Implementation depends on storage caps.

**Concurrency:** consider read/read, read/write, write/write, delete/read. Read-only sharing is simpler than concurrent mutation.

**Locking** (only if mutation requires it): locking, version checks, optimistic concurrency, transaction boundaries, copy-on-write. Do not introduce locking unnecessarily.

**Conflict** definition needed when two Processes mutate the same artifact: merge, last-write-wins, version conflict, or human resolution.

---

# 19. Naming, Storage Path, Serialization, Structured Output

**Names:** stable, meaningful, predictable, collision-resistant. Prefer logical IDs over timestamp/arbitrary-generated names.

**Storage paths** generated by the Artifact Manager (`Artifact ID → Storage policy → Managed path`) rather than Agent-generated arbitrary paths.

**Serialization:** use deterministic formats (JSON, CSV, YAML, Parquet) matching downstream requirements.

**Structured outputs:** `Agent → Structured result → Schema validation → Artifact persistence`; do not save invalid output just because the file is syntactically valid.

---

# 20. Caching, Reproducibility, Approval, Publishing

**Caching:** `Input + configuration + version → Artifact cache → existing valid artifact? YES reuse / NO execute`. Cache validity must account for relevant dependencies.

**Cache invalidation** — consider stale when important deps change: input, Knowledge/Skill versions, Agent/Task configuration, model configuration, Tool/MCP version, architecture version. The exact set is defined by the Process.

**Reproducibility:** important artifacts reproducible from architecture/Process version, Agent/Task configuration, input, Knowledge/Skill versions, model configuration, Tool/MCP versions.

**Human approval** must refer to a specific version (`chapter_07 v3`), not unversioned `chapter_07`.

**Publishing is a distinct Process:** `Generate Artifact → Validate → Human Approval → Publish Process → Publishing Tool/MCP`. Generation must not implicitly publish.

**External side effects:** an Artifact may represent a planned side effect, but the artifact itself must not auto-trigger it — the Flow decides when publication occurs (`Publish Package Artifact → Human Approval → Publishing Tool`).

---

# 21. Access Through MCP / Tools, Governance

**MCP access** (`Agent → MCP → External Artifact`): preserve external_id, source, access scope, version, retrieval time where relevant.

**Tool access** (`Agent → Artifact Tool → Artifact`): expose only required operations — `read_artifact` is preferable to `filesystem_admin` when reading suffices.

**Governance** — Amsha should answer: What is this artifact? Who produced it? From what inputs? Which Process? Which version? Who can access it? Which outputs depend on it? Is it valid/current? When can it be deleted? Part of architecture-governance.

---

# 22. Anti-Patterns

1. **Everything in Flow State** — don't use Flow State as an artifact store.
2. **Entire Artifact in Every Prompt** — use relevant extraction.
3. **Arbitrary Agent Filesystem Access** — use a bounded Artifact Tool.
4. **File Path as Security Boundary** — a path is not authorization.
5. **Overwriting Important Artifacts** — version when auditability/rollback matters.
6. **Untracked External Files** — register files external Tools/MCP create when they matter.
7. **Unvalidated Artifacts** — a successful write ≠ a valid Process output.
8. **Artifact as Memory** — a stored file is not automatically Memory.
9. **Artifact as Knowledge** — a generated report is not authoritative Knowledge.
10. **Artifact as Context** — it's context only when relevant info is selected for execution.
11. **Artifact as State** — a large document isn't workflow state; store a reference and status.
12. **Implicit Artifact Dependencies** — make version dependencies explicit.

---

# 23. Recommended Architectures

**Recommended file/artifact architecture:** FLOW manages Flow State → Artifact References → PROCESS dispatch into Python/Agent/Tool → ARTIFACT → Validate/Version/Register → STORAGE. The Artifact is the logical output boundary.

**Recommended end-to-end pattern:** `INPUT → Process → Python/Agent/Crew/Tool → Output → Deterministic Validation → Semantic Validation → Artifact Registration → Artifact Reference → Flow State → Next Process`.

---

# 24. Final Rules

1. A File is a concrete representation of data.
2. An Artifact is a meaningful workflow data object.
3. A Reference identifies where an Artifact can be accessed.
4. Context is selected information, not an artifact store.
5. Flow State stores Artifact references rather than large contents whenever possible.
6. Processes explicitly declare Artifact inputs and outputs.
7. Important Artifacts have stable identity.
8. Important Artifacts are versioned.
9. Artifact provenance is preserved where required.
10. Artifact dependencies are explicit.
11. Artifacts are validated before downstream consumption.
12. File integrity and semantic validity are separate concerns.
13. Python handles deterministic file/artifact operations whenever sufficient.
14. Tools provide bounded artifact capabilities.
15. Agents do not get unrestricted filesystem access merely to access artifacts.
16. MCP exposes only the external artifact capabilities required.
17. Artifact access is separate from Artifact reference.
18. Credentials and secrets must not be stored in ordinary Artifact context.
19. External artifacts preserve source and external identity where relevant.
20. Artifact versions are associated with human approvals when approval matters.
21. Important mutation prefers versioning or controlled concurrency.
22. Partial artifacts are not automatically valid final outputs.
23. Artifact lifecycle accounts for checkpoint and recovery requirements.
24. Artifact deletion respects retention and active dependencies.
25. Large artifacts are referenced rather than repeatedly embedded in prompts.
26. Relevant artifact content is extracted before semantic execution when possible.
27. Summaries do not replace exact evidence when fidelity is required.
28. Artifact lineage is preserved for important production outputs.
29. Artifact caching accounts for relevant dependency versions.
30. Publishing/external side effects remain explicit Processes.
31. Artifacts do not silently become Knowledge, Memory, Context, or State.
32. Every important Artifact dependency traces to a Process requirement.

---

# 25. Final Principle

The essential distinctions:

```
FILE:     "What concrete representation contains the data?"
ARTIFACT: "What meaningful piece of workflow data exists?"
REFERENCE: "Where can that artifact be accessed?"
INPUT:    "What data does this Process receive?"
CONTEXT:  "What information from the artifact matters right now?"
STATE:    "What artifact-related condition controls the workflow?"
OUTPUT:   "What did this Process produce?"
```

> **Amsha should treat Files and Artifacts as first-class data boundaries rather than as prompt content.**

Preferred architecture: `PROCESS → Execute Work → OUTPUT → VALIDATION → ARTIFACT → {REFERENCE, PROVENANCE} → FLOW STATE → DOWNSTREAM PROCESS → RELEVANT CONTEXT ONLY`.

> **Store meaningful outputs as managed Artifacts, move them between Processes through explicit references, retrieve only the information required for the current execution, and keep workflow State small, deterministic, and separate from Artifact content.**

This gives a clean boundary between execution, data, storage, context, and workflow state — minimizing token usage while preserving reproducibility, security, lineage, and recovery.