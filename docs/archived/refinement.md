# Amsha 2.0 – Internal Architecture Specification

> **Audience:** Amsha core contributors
> **Nature:** Semi-formal internal design document
> **Primary Goal:** Generalize execution, not business logic
> **Secondary Goal:** Keep client code simple without stealing control

---

## 0. Core Positioning 

Amsha is a **general agentic execution substrate**.

It standardizes:

* Execution
* Instrumentation
* Observability
* State handling
* Framework abstraction

It explicitly does **not** standardize:

* Business workflows
* Domain logic
* Control flow decisions
* Scheduling or deployment infrastructure

---

## 1. Global Architectural Laws (Updated)

### L1. Domain Agnosticism

Amsha never understands *meaning*.

---

### L2. Proxy Rule

All external systems (LLMs, agents, tools, frameworks) are accessed only via Amsha protocols.

---

### L3. Configuration-First

Behavior changes via config, not code.

---

### L4. Client Owns Flow

Loops, branches, retries, batching, and conditionals belong to the client.

---

### ✅ **L5. State Infrastructure, Not State Logic**

Amsha may manage **state containers**, persistence, and replay —
but must never implement **state-driven decisions or transitions**.

---

### ✅ **L6. Execution Semantics, Not Infrastructure**

Amsha defines *how* execution behaves (streaming, background),
but not *where* or *when* it runs (FastAPI, cron, workers).

---

---

## 2. Module: LLM Factory (The Engine)

### 2.1 Problem

* Framework lock-in (`crewai.LLM`, LangChain objects)
* No clean separation between streaming and non-streaming calls
* Retry, logging, token tracking scattered or framework-bound
* No unified execution behavior across interactive vs batch usage

---

### 2.2 Why This Matters

Amsha must support:

* Interactive LLM use (chat, streaming)
* Background LLM use (batch, offline)
* Without forcing clients to adopt agent frameworks

---

### 2.3 Proposed Solution

#### 2.3.1 `ILLMProvider` (Unchanged Core)

* Minimal interface: `generate()` / `stream()`
* No framework imports
* Streaming is **capability-based**, not mandatory

---

#### 2.3.2 Execution-Aware LLM Wrapper

LLM Factory returns **Amsha-native wrappers** that:

* Support both streaming and non-streaming execution
* Normalize provider differences
* Emit execution events

---

#### 2.3.3 Internal Execution Decorators

`@amsha_llm_call` (internal only):

* Retry
* Token counting
* Timing
* Streaming normalization

Clients never interact with this directly.

---

### 2.4 Guardrails

* No framework-specific config leakage
* Streaming must degrade gracefully
* LLMs usable inside and outside agent execution

---

---

## 3. Module: Crew Forge (The Body)

### 3.1 Problem

* Orchestration logic mixed with execution
* Client forced to repeat execution plumbing
* Hard to support different execution modes (interactive vs batch)
* No standardized way to carry state across executions

---

### 3.2 Why This Matters

Clients:

* Generate seed → loop → refine → evaluate
* Parse logs in batches
* Resume long-running workflows

These are **domain flows**, but they all require:

* Shared execution state
* Consistent execution semantics
* Simple APIs

---

### 3.3 Proposed Solution

#### 3.3.1 Registry (Unchanged)

Passive registry holding:

* Agents
* Tasks
* Optional pipeline ordering hints

No execution logic.

---

#### 3.3.2 Orchestrator Protocol (`IOrchestrator`)

* Builds framework-specific objects
* Executes requested agents/tasks
* Emits lifecycle events

Still **no flow logic**.

---

#### 3.3.3 ExecutionSession (Expanded Responsibility)

`ExecutionSession` becomes the **primary client-facing API**.

It now:

* Accepts execution mode
* Injects state
* Returns execution handles
* Applies monitoring automatically

This is **execution abstraction**, not workflow abstraction.

---

### 3.4 Guardrails

* No implicit looping
* No conditional execution
* No domain inference
* Pipelines are optional and declarative only

---

---

## 4. Module: Execution State (NEW – Infrastructure Module)

> This is a **new module**, added because state management is **cross-cutting** and should not leak into Crew Forge or Monitor.

---

### 4.1 Problem

* Agent systems have implicit state (memory, outputs, context)
* No standard way to:

  * Persist state
  * Resume execution
  * Replay runs
* Clients reimplement fragile glue

---

### 4.2 Why This Matters

Without standardized state:

* Long-running jobs are brittle
* Crashes lose progress
* Evaluation and replay are impossible
* Human-in-the-loop workflows break

---

### 4.3 Proposed Solution

#### 4.3.1 `ExecutionState`

A general-purpose, opaque state container:

* Key–value store
* JSON-serializable
* Versioned
* Engine-agnostic

Amsha does **not** interpret contents.

---

#### 4.3.2 State Persistence

Amsha supports:

* `save() → JSON`
* `load() ← JSON`
* Snapshotting during execution

---

#### 4.3.3 State Injection

State can be:

* Passed into executions
* Shared across multiple runs
* Used in interactive or batch modes

But **never used for control flow by Amsha**.

---

### 4.4 Guardrails

* No state-based branching
* No “auto-resume” logic
* No semantic interpretation of keys

---

---

## 5. Module: Execution Runtime 

> This module defines **execution behavior**, not infrastructure.

---

### 5.1 Problem

* Need to support:

  * Streaming LLM calls
  * Background/batch jobs
* Without introducing:

  * FastAPI
  * Cron
  * Workers
  * Schedulers

---

### 5.2 Why This Matters

Amsha must work equally well in:

* CLI tools
* Web apps
* Workers
* Scheduled jobs
* Notebooks

---

### 5.3 Proposed Solution

#### 5.3.1 Execution Modes

Amsha defines execution **semantics**:

* `INTERACTIVE`

  * Streaming enabled
  * Cancelable
  * Token-by-token output

* `BACKGROUND`

  * Detached execution
  * Pollable result
  * Serializable state

---

#### 5.3.2 ExecutionHandle

Every execution returns a handle:

* `status()`
* `result()`
* `stream()` 
* `cancel()`

This abstracts:

* Sync vs async
* Streaming vs non-streaming
* Provider differences

---

### 5.4 Guardrails

* No threads, queues, or schedulers
* No servers or APIs
* Clients decide deployment

---

---

## 6. Module: Crew Monitor 

### 6.1 Problem

* Manual monitoring is noisy
* Failures lose metrics
* Streaming and background runs need consistent observability

---

### 6.2 Proposed Solution (Unchanged, Extended)

* Observer-based instrumentation
* Automatically wraps execution
* Works for:

  * Streaming
  * Background
  * Resumed executions

All metrics normalized into `AmshaMetrics`.

---

### 6.3 Guardrails

* Monitor sees only inputs/outputs
* No dependency on internal state meaning

---

---

## 7. Client Responsibility (Explicitly Restated)

Clients:

* Loop
* Branch
* Batch
* Decide retries
* Interpret results
* Decide what to run next

Amsha:

* Executes
* Observes
* Stores state
* Streams output
* Persists artifacts

---

## 8. Final Architectural Summary

| Capability                       | Owned By |
| -------------------------------- | -------- |
| Execution semantics              | Amsha    |
| State storage & replay           | Amsha    |
| Streaming abstraction            | Amsha    |
| Background execution abstraction | Amsha    |
| Scheduling                       | Client   |
| Workflow logic                   | Client   |
| Domain meaning                   | Client   |

---

## 9. Final North Star 

> **Amsha is an execution substrate with memory and observability —
> not a workflow engine, not a scheduler, not a domain brain.**

---
