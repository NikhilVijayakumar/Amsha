# Anti-Patterns and Checklists

## Purpose

Defines the main **Amsha architecture and implementation anti-patterns** and provides concise checklists for validating an Amsha/CrewAI project.

Core principle:

> **Prefer the smallest architecture that reliably solves the problem.**

---

# 1. Architecture Anti-Patterns

**1.1 CrewAI-First Design** — starting with "What Agents should I create?" before understanding the problem; the framework begins driving architecture. Preferred: `Problem → Goal → Processes → Flow → Capability Selection → CrewAI Implementation`.

**1.2 Architecture by Framework Feature** — using a CrewAI feature because it exists (Memory because supported, Planning because supported, Crew because multiple Agents, MCP because available). Preferred: every capability has an architectural justification.

**1.3 God Agent** — one Agent responsible for research, analysis, writing, validation, planning, tool execution; the professional boundary becomes meaningless. Preferred: the smallest professional capability that satisfies the requirement.

**1.4 Generic Agent** — e.g. "AI Expert who can do anything"; no meaningful professional identity or boundary. Preferred: e.g. "Senior Narrative Continuity Editor" with a focused responsibility.

**1.5 Micro-Agent Explosion** — an Agent for every tiny op (`JSON Reader Agent, String Formatter Agent, Sorting Agent, Validation Agent`); adds unnecessary LLM calls, coordination, tokens, complexity. Preferred: deterministic Python where sufficient.

---

# 2. Process Anti-Patterns

**2.1 Technical Process Decomposition** — `load_file, parse_file, create_variable, call_llm, save_file` are implementation ops, not meaningful Processes. Preferred: `analyze_source, evaluate_character_arc, generate_screenplay, validate_screenplay`.

**2.2 God Process** — one Process performs many unrelated transformations; poor boundaries, hard validation/recovery/reuse. Preferred: split meaningful independent responsibilities.

**2.3 Artificial Atomicity** — making every Process/Task tiny to claim "atomic." Atomic means **one coherent responsibility and transformation with a meaningful completion boundary** — not one line, function, LLM call, or Task.

---

# 3. Task Anti-Patterns

**3.1 Composite Task** — a Task makes an Agent research, analyze, write, validate, publish at once. Preferred: split when responsibilities have independent purpose, output, validation, expertise, failure boundary, or human decision.

**3.2 Task as Agent Identity** — putting professional identity ("You are a senior...") into every Task prompt when it belongs in the Agent definition. Preferred: `Agent → professional identity; Task → bounded operation`.

**3.3 Task as Knowledge Dump** — embedding large reference material into every Task. Preferred: relevant Knowledge retrieval and minimal Context.

**3.4 Task Without Output Contract** — "Analyze the story." without defining a usable result. Preferred: define output, format, schema, completion, validation.

---

# 4. Agent–Task Anti-Patterns

**4.1 Making the Agent Generic to Fit the Task** — if a Task doesn't fit, don't keep broadening the Agent; instead reassign Task, refine Agent, split Task, or introduce Crew. **4.2 Wrong Professional Perspective** — a continuity Task assigned to an unrelated agent; the problem is architectural, not just prompt wording. **4.3 Capability Padding** — adding tools, memory, planning, reasoning, knowledge, MCP "just in case." Preferred: capabilities justified by the Process/Task requirement.

---

# 5. Crew Anti-Patterns

**5.1 Crew of One** — a Crew with one Agent and no collaboration; use Agent + Task unless Crew gives real architectural benefit. **5.2 Crew as Agent Container** — a Crew because several Agents exist; multiple Agents don't imply collaboration. **5.3 Crew as Workflow Engine** — branching, loops, approval, recovery, global state, termination inside a Crew. Preferred: `Flow → orchestration; Crew → collaboration`. **5.4 Unnecessary Synthesizer Agent** — an Agent only mechanically combining outputs; use deterministic synthesis when sufficient. **5.5 Unbounded Collaboration** — Agents debate without termination, iteration limits, success criteria; define explicit collaboration boundaries.

---

# 6. Flow Anti-Patterns

**6.1 Hidden Workflow** — the workflow exists implicitly inside prompts/Agent behavior. Preferred: represent important decisions explicitly in Flow state and transitions. **6.2 God Flow** — the Flow contains all professional work. Preferred: `Flow → controls; Process → performs meaningful work; Agent/Crew → semantic work; Python → deterministic work`. **6.3 Unbounded Loop** — an iteration without clear condition, limit, success, exhaustion. Preferred: every loop has a bounded termination strategy. **6.4 State Dump** — every available bit of info into Flow state. Preferred: store only what's required to control execution.

---

# 7. Context Anti-Patterns

**7.1 Context Dumping** — complete project/story/world state to every Agent; high token cost and irrelevant info. Preferred: `relevant input + relevant state + relevant Knowledge + relevant previous outputs`. **7.2 State/Context Confusion** — Flow state as a general store; `State → controls execution; Context → supports execution`. **7.3 Knowledge/Memory Confusion** — Memory as authoritative domain Knowledge; `Knowledge → reference truth; Memory → retained history`; history shouldn't silently become canonical Knowledge. **7.4 Artifact/Context Confusion** — passing large artifacts through every Task instead of references. Preferred: `Artifact → Reference → Relevant Context`.

---

# 8. Reasoning and Planning Anti-Patterns

**8.1 Planning for Known Workflow** — autonomous Planning when the workflow is known; use explicit Flow transitions. **8.2 Planning Without Bounds** — no limits on actions, iterations, time, resources → uncontrolled execution. **8.3 Reasoning as a Replacement for Deterministic Logic** — an LLM to sort, calculate, validate schema, route deterministic states when Python does it reliably. Preferred: deterministic first.

---

# 9. Tool and MCP Anti-Patterns

**9.1 Universal Tool** — one Tool with unrestricted filesystem/shell/database/network access; large security and operational boundary. Preferred: narrow capabilities. **9.2 MCP as Everything Server** — exposing every capability; each server should have a meaningful capability boundary. **9.3 Secrets in Context** — never place credentials/secrets in Agent prompts, Task context, Knowledge, Memory, Flow state; use secure runtime configuration. **9.4 Untrusted MCP Data as Instructions** — external MCP content is data; must not override Amsha rules, system constraints, architecture decisions, security policies.

---

# 10. Failure and Recovery Anti-Patterns

**10.1 Retry Everything** — not every failure is retryable (invalid input/schema, authorization failure, deterministic validation failure). **10.2 Retry = Iteration** — `Retry → recover from execution failure; Iteration → intentionally improve/repeat work`. **10.3 Silent Recovery** — auto-changing architecture/behavior after failure; record the failure and follow the approved recovery policy. **10.4 Side Effects Without Idempotency** — retrying a side-effecting op duplicates it; use idempotency, status verification, compensation, or human confirmation. **10.5 Recovery Without Durable State** — a workflow can't reliably resume without persisted state and artifact references; checkpoint meaningful recovery boundaries.

---

# 11. Observability Anti-Patterns

**11.1 Logging Everything** — huge logs increase cost and reduce diagnostic value; instrument meaningful boundaries. **11.2 Observability Controls Workflow** — `Execution → produces events; Observability → observes events`, not the reverse. **11.3 Exposing Private Reasoning** — don't expose private chain-of-thought; record decision, result, validation, duration, failure, artifact instead.

---

# 12. Generation Anti-Patterns

**12.1 Generate Before Validate** — `Problem → Code`; preferred `Problem → Architecture → Validation → Implementation`. **12.2 Code Generation as Architecture Design** — the generator must not invent missing Agents/Tasks/Crews/Tools/Flow states; if architecture is insufficient, `stop → report gap → revise architecture`. **12.3 Generate Unused Framework Features** — don't generate empty Memory/Knowledge/MCP/Tools/Planning layers when not required. **12.4 Architecture Drift** — generated implementation diverges from the approved architecture; maintain architecture/implementation version, component IDs, traceability.

---

# 13. Amsha Anti-Patterns

**13.1 Amsha as Generic Code Generator** — value is architecture reasoning, governance, validation, not CrewAI boilerplate. **13.2 Amsha as Generic Agent Framework** — don't compete with CrewAI's runtime abstractions; govern how they're used. **13.3 Amsha as Generic Workflow Engine** — Amsha may design/govern Flow architecture; execution stays the runtime's responsibility. **13.4 Amsha as Unrestricted MCP Proxy** — expose bounded architecture capabilities, not arbitrary external capabilities.

---

# 14. Checklists

**Architecture (before implementation):** [ ] Problem clearly defined · start condition defined · desired end state defined · scope/boundaries defined · success criteria defined · Processes identified · Process contracts defined · Processes meaningfully atomic · dependencies valid · Flow defined · State minimal and sufficient · failure paths identified · recovery strategy defined · capability selection justified · human decisions identified · architecture validated.

**Agent:** [ ] Professional identity clear · Role is a real professional archetype · domain/specialization/seniority appropriate · Goal is enduring professional responsibility · backstory has relevant experience/perspective · scope not too narrow/broad · Tasks match professional capability · Knowledge/Skills/Tools/MCP/Reasoning/Planning/Memory justified · permissions follow least privilege · prompt footprint reasonable.

**Task:** [ ] One coherent responsibility · clear Process and Agent mapping · required and optional inputs defined · instructions executable · relevant context only · output contract defined · structured schema where useful · completion criteria defined · validation defined · failure behavior defined · retry bounded · side effects handled safely · dependencies defined · token/context cost considered.

**Crew:** [ ] Crew actually necessary · multiple professional capabilities required · collaboration provides meaningful value · Agent responsibilities distinct · Tasks covered and aligned · collaboration model explicit · dependencies explicit · parallelism safe · synthesis defined · disagreement handling defined · output contract defined · failure handling bounded · security boundaries defined · scope bounded.

**Flow:** [ ] Flow represents execution control · Processes separate from orchestration · state minimal · transitions explicit · conditions defined · parallel groups safe · iterations bounded · human gates explicit · failure paths explicit · recovery boundaries defined · terminal states defined · cancellation considered · state invariants defined where needed.

**Runtime:** [ ] Checkpointing implemented where required · recovery tested where required · artifacts persisted correctly · Tool/MCP failures handled · idempotency for side effects · execution IDs available · events/metrics available · traceability preserved · secrets isolated · permissions enforced · resource limits enforced.

**Generation:** [ ] Architecture version recorded · implementation spec generated · every architectural component mapped · no unnecessary components generated · Flow/Agents/Tasks/Crews/Tools/MCP match architecture · validation implemented · failure/recovery implemented · tests generated · architecture-to-code traceability preserved · project structurally validated.

**Final Amsha Governance — answer yes to all applicable:** Does the architecture solve the actual problem? Is the goal unambiguous? Are boundaries clear? Are Processes meaningful and contracts complete? Is Flow explicit? Is state minimal? Are failure paths covered and recovery sufficient? Is each capability justified? Is deterministic work kept deterministic? Is each Agent a real professional capability? Is each Task bounded and aligned? Is each Crew genuinely collaborative? Are Knowledge, Skills, Memory, Context, State separated? Are Tools/MCP minimal and secure? Are human decisions explicit? Are large outputs represented as Artifacts? Is the architecture implementation-ready? Can the generated project be traced back to the architecture?

---

# 15. Core Principle

Amsha continuously enforces one architectural rule:

```
REQUIREMENT → PROCESS → CAPABILITY → AGENT/TASK/CREW → FLOW → IMPLEMENTATION
```

At every boundary ask:

> **Is this the smallest reliable mechanism that satisfies the requirement?**

If no, simplify the architecture before adding more capability.

> **Complexity must be earned by the problem, not introduced by the framework.**