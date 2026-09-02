#  Amsha Prerequisite: Capability Selection

## Purpose

The previous prerequisite stages established:

```text
Problem
   ↓
Goal & Boundary
   ↓
Processes
   ↓
Process Contracts
   ↓
Process Validation
   ↓
Flow & State
   ↓
Corner Cases & Failure Planning
````

This document determines **what capabilities are actually required to implement the approved architecture**.

The central objective is:

> **Select the least powerful mechanism that can reliably satisfy each architectural requirement.**

Amsha should not begin with:

> "Should we use Agents, Crews, Flows, Knowledge, Memory, MCP, or Planning?"

Instead begin with:

> "What capability does this Process or transition actually require?"

Only then select the implementation mechanism.

---

# 1. Position in the Architecture Process

The prerequisite sequence is:

```text
00 Problem Definition
        ↓
01 Goal & Boundary Definition
        ↓
02 Process Decomposition
        ↓
03 Process Contracts & Atomicity
        ↓
04 Process Validation & Human Review
        ↓
05 Flow & State Planning
        ↓
06 Corner Cases & Failure Planning
        ↓
07 Capability Selection
        ↓
08 Architecture Validation
```

This is the first stage where implementation mechanisms are intentionally considered.

However, capability selection is still **architecture-level reasoning**, not code generation.

---

# 2. What Is a Capability?

A capability is a mechanism available to implement part of the approved architecture.

Examples include:

```text
Deterministic Python
Agent
Task
Crew
Flow
Tool
Knowledge
Memory
Reasoning
Planning
MCP
Human Review
Checkpointing
Observability
```

These mechanisms solve different classes of problems.

They should not be treated as interchangeable building blocks.

---

# 3. Core Principle: Least Powerful Sufficient Mechanism

Amsha should prefer:

```text
Simplest mechanism
        ↓
that reliably satisfies
        ↓
the actual requirement
```

For example:

```text
Requirement:
Calculate a score
```

Use:

```text
Python
```

not:

```text
Agent → Task → Crew
```

Similarly:

```text
Requirement:
Generate a creative interpretation
```

may require:

```text
Agent + Task
```

while:

```text
Requirement:
Have multiple specialists analyze competing dimensions
```

may justify:

```text
Crew
```

And:

```text
Requirement:
Coordinate a known multi-step workflow
```

may justify:

```text
Flow
```

---

# 4. Capability Selection Is Not Capability Maximization

A common architecture failure is:

```text
Problem
 ↓
Use every available feature
```

For example:

```text
Flow
 + Crew
 + multiple Agents
 + Planning
 + Reasoning
 + Memory
 + Knowledge
 + Tools
 + MCP
```

may look sophisticated but can be unnecessarily expensive and difficult to maintain.

Amsha should instead produce:

```text
Problem
 ↓
Required capabilities
 ↓
Minimum sufficient architecture
```

Complexity must be justified by requirements.

---

# 5. Capability Selection Inputs

Capability selection consumes:

* validated Processes
* Process contracts
* Flow structure
* State model
* transition conditions
* human review points
* failure plan
* external dependencies
* recovery requirements
* quality requirements
* determinism requirements

Conceptually:

```text
Validated Architecture
        ↓
Capability Analysis
        ↓
Capability Requirements
        ↓
Implementation Mechanisms
```

---

# 6. Capability Decision Hierarchy

Use the following reasoning order.

```text
1. Can deterministic logic solve it?
        ↓
2. Does it require LLM intelligence?
        ↓
3. Does it require one professional capability?
        ↓
4. Does it require multiple collaborating specialists?
        ↓
5. Does it require workflow orchestration?
        ↓
6. Does it require persistent domain knowledge?
        ↓
7. Does it require retained historical information?
        ↓
8. Does it require explicit reasoning/planning?
        ↓
9. Does it require external capabilities?
        ↓
10. Does it require human judgment?
```

This order is not a rigid execution sequence.

It is a **reasoning discipline** that prevents premature complexity.

---

# 7. Deterministic Python

Use deterministic Python when the requirement can be reliably expressed as deterministic computation or control logic.

Examples:

```text
schema validation
data transformation
sorting
filtering
calculation
aggregation
branch selection
state validation
format conversion
file operations
deterministic business rules
```

Example:

```text
Requirement:
Determine whether score >= 80.

Capability:
Python
```

There is no reason to use an LLM for this.

---

# 8. Agent

An Agent is appropriate when the Process requires an autonomous professional capability involving judgment, interpretation, generation, or reasoning.

Typical characteristics:

```text
ambiguous information
semantic interpretation
creative generation
domain judgment
complex reasoning
professional perspective
```

Example:

```text
Process:
Analyze character psychology

Capability:
Specialized professional Agent
```

The Agent should be modeled as a real professional role rather than a generic technical function.

For example:

```text
Senior Character Psychologist
```

is a professional capability.

Whereas:

```text
Character Analyzer Agent
```

is primarily an implementation label.

---

# 9. Agent Is Not Automatically Required for Every LLM Operation

An LLM call does not necessarily imply a complex Agent architecture.

The question is:

> Does this operation require a persistent professional capability?

If not, a simpler LLM-backed Task or deterministic mechanism may be sufficient depending on the implementation architecture.

Avoid:

```text
Every Process
    ↓
Create Agent
```

Agent creation should be justified by capability requirements.

---

# 10. Task

A Task represents a bounded unit of work assigned to an Agent or Crew.

Use Task-level decomposition when the work:

* has a clear input
* has a clear output
* has a defined purpose
* can be evaluated independently

The Process architecture should remain the higher-level semantic boundary.

Conceptually:

```text
Process
   ↓
Implementation
   ↓
Agent
   ↓
Task
```

A Process may map to:

```text
one Task
```

or:

```text
multiple Tasks
```

depending on implementation needs.

Do not redesign the Process simply because it requires multiple Tasks.

---

# 11. Crew

A Crew is justified when one professional capability is insufficient and the Process benefits from multiple specialized roles collaborating.

Typical indicators:

```text
multiple distinct expert perspectives
independent analysis
cross-review
debate
specialist synthesis
complex collaborative reasoning
```

Example:

```text
Process:
Evaluate a screenplay from multiple professional perspectives

Capability:
Crew

Agents:
- Story Editor
- Character Specialist
- Cinematography Specialist
- Production Analyst
```

A Crew is not justified merely because:

```text
the task is large
```

or:

```text
multiple steps exist
```

Multiple steps alone are normally a Flow or Task concern.

---

# 12. Flow

Flow is appropriate when the architecture requires explicit workflow orchestration.

Indicators include:

```text
multiple Processes
state transitions
conditional branches
iteration
parallel execution
human gates
checkpointing
long-running execution
failure recovery
```

Example:

```text
P1
 ↓
P2
 ↓
Decision
 ├── P3
 └── P4
```

This is fundamentally a Flow problem.

A Crew should not be used as a substitute for deterministic workflow orchestration.

---

# 13. Flow vs Crew

This distinction is fundamental.

## Flow

Controls:

```text
when
where
condition
state
transition
iteration
recovery
```

## Crew

Controls:

```text
who
collaborates
how specialists reason together
```

Therefore:

```text
Flow = orchestration
Crew = collaboration
```

They may be combined:

```text
Flow
  ↓
Process
  ↓
Crew
```

when the architecture requires both.

---

# 14. Flow + Crew

Use Flow + Crew when:

```text
the workflow itself is structured
```

and:

```text
one or more Processes require collaborative intelligence
```

Example:

```text
Flow
 │
 ├── Python validation
 │
 ├── Crew: Analyze Story
 │
 ├── Python decision
 │
 ├── Crew: Generate Chapter
 │
 └── Human Approval
```

This is often preferable to making the entire workflow a single autonomous Crew.

---

# 15. Knowledge

Knowledge is appropriate when an Agent or Process requires domain/reference information that is not reliably contained in its static instructions.

Examples:

```text
story bible
character definitions
world rules
technical documentation
domain reference material
production standards
historical source material
```

Knowledge answers:

> What reference information should the capability know?

It does not answer:

> What should the workflow do next?

That is Flow/state responsibility.

---

# 16. Knowledge Selection Test

Ask:

> Would the Process still have the necessary domain information if the reference material were not provided?

If no:

```text
Knowledge is likely required.
```

If yes:

```text
Do not add Knowledge merely because reference material exists.
```

The goal is relevant retrieval, not maximum context.

---

# 17. Knowledge vs Context

Knowledge should not automatically become Process context.

```text
Knowledge Repository
        ↓
Relevant Retrieval
        ↓
Process Context
```

Only the relevant information should be supplied.

This prevents:

* excessive token usage
* irrelevant context
* duplicated information
* degraded reasoning

---

# 18. Memory

Memory is appropriate when information should be retained across interactions or executions for future use.

Examples:

```text
historical decisions
past interactions
learned preferences
previously established facts
long-term workflow history
```

Memory answers:

> What should this capability remember?

It is not a substitute for Flow state.

---

# 19. Memory Selection Test

Ask:

> Does the workflow need information from previous executions or interactions that cannot be reliably supplied as current input or Knowledge?

If yes:

```text
Memory may be justified.
```

If the information is only needed during the current execution:

```text
Use Flow state or Process output.
```

---

# 20. Reasoning

Explicit reasoning capability may be useful when a Process requires structured multi-step reasoning that benefits from deliberate reasoning behavior.

However:

> Do not add reasoning capability merely because the task uses an LLM.

Many LLM operations already perform sufficient reasoning implicitly.

Use explicit reasoning mechanisms when the requirement demonstrates a meaningful benefit.

---

# 21. Planning

Planning is appropriate when the workflow or Agent must dynamically determine a sequence of actions that cannot be reliably predefined.

Example:

```text
Goal
 ↓
Determine required actions
 ↓
Choose actions dynamically
 ↓
Execute plan
 ↓
Evaluate result
```

This differs from a known deterministic workflow:

```text
P1 → P2 → P3
```

If the sequence is already known, use Flow orchestration rather than introducing autonomous planning.

---

# 22. Flow vs Planning

This is an important distinction.

### Known workflow

```text
P1 → P2 → P3
```

Use:

```text
Flow
```

### Unknown sequence

```text
Goal
 ↓
Determine actions dynamically
 ↓
Execute selected actions
```

Planning may be justified.

Therefore:

> **Do not use autonomous planning where deterministic orchestration is already known.**

---

# 23. Tools

A Tool is appropriate when a Process or Agent must perform an action that cannot be accomplished through reasoning alone.

Examples:

```text
database query
file operation
API call
calculation service
search
asset generation
external command
system operation
```

A Tool answers:

> What action can this capability perform?

Tools should be:

* minimal
* relevant
* appropriately scoped
* permission-controlled

Avoid exposing unnecessary tools to an Agent.

---

# 24. Tool Selection Principle

Use the smallest tool surface that satisfies the Process.

Bad:

```text
Agent
 ↓
50 unrelated tools
```

Better:

```text
Agent
 ↓
3 task-relevant tools
```

Excessive tool access increases:

* decision complexity
* token usage
* risk
* ambiguity
* potential failure modes

---

# 25. MCP

MCP should be considered when the required capability belongs to an external system or needs a standardized external tool boundary.

Examples:

```text
ComfyUI
Unreal Engine
external application
external service
shared enterprise tool system
```

Conceptually:

```text
Flow / Agent
      ↓
MCP
      ↓
External Capability
```

MCP is not simply a replacement word for Tool.

It is an integration boundary for accessing external capabilities.

---

# 26. Tool vs MCP

Use a direct Tool when:

```text
capability is local
simple
tightly coupled
owned by the application
```

Consider MCP when:

```text
capability belongs to an external system
multiple clients may consume it
standardized tool exposure is useful
system boundary should remain separate
```

Do not introduce MCP merely because it is available.

---

# 27. Human Capability

Human interaction is itself a capability.

Use it when the architecture requires:

```text
subjective judgment
approval
ambiguous interpretation
high-impact decisions
creative acceptance
exception handling
```

Example:

```text
Automated Evaluation
        ↓
Ambiguous
        ↓
Human Review
```

Human review should be placed at meaningful decision boundaries.

---

# 28. Checkpointing

Checkpointing is appropriate when workflow recovery requires preserving execution state.

Indicators:

```text
long-running workflow
expensive computation
human pauses
external operations
failure recovery
resumable execution
```

Example:

```text
P1
 ↓
Checkpoint
 ↓
P2
 ↓
Human Review
 ↓
Checkpoint
 ↓
P3
```

Checkpointing should not be added everywhere.

---

# 29. Observability and Tracing

Observability is required when the workflow needs visibility into:

```text
execution
latency
errors
Process outcomes
LLM calls
tool calls
state transitions
cost/token usage
performance
```

For Amsha, observability should be treated as an engineering capability rather than a reason to introduce an additional orchestration mechanism.

The architecture should determine:

```text
What must be observed?
Where?
At what granularity?
For what purpose?
```

The implementation can then select the appropriate tracing infrastructure.

---

# 30. Capability Decision Table

A useful initial decision matrix is:

| Requirement                      | Preferred Capability |
| -------------------------------- | -------------------- |
| deterministic calculation        | Python               |
| deterministic validation         | Python               |
| deterministic transformation     | Python               |
| semantic interpretation          | Agent / LLM          |
| professional judgment            | Agent                |
| bounded LLM work                 | Agent + Task         |
| multiple specialist perspectives | Crew                 |
| known multi-step orchestration   | Flow                 |
| stateful workflow                | Flow + State         |
| conditional workflow             | Flow                 |
| iteration                        | Flow                 |
| parallel Processes               | Flow                 |
| domain reference information     | Knowledge            |
| historical retained information  | Memory               |
| dynamic action sequencing        | Planning             |
| deliberate complex reasoning     | Reasoning            |
| local external action            | Tool                 |
| external-system capability       | MCP                  |
| subjective approval              | Human Review         |
| resumable long-running workflow  | Checkpointing        |
| execution visibility             | Observability        |

This is a starting decision framework, not a rigid mapping.

---

# 31. Capability Selection Per Process

Each Process should receive a capability assessment.

Conceptually:

```yaml
process_capability:
  process_id: ""
  requirement:
    deterministic: false
    semantic_reasoning: false
    professional_judgment: false
    collaboration: false
    external_action: false
    human_decision: false

  selected:
    primary: ""
    supporting: []

  rationale: ""

  rejected:
    - capability: ""
      reason: ""
```

The `rejected` section is valuable.

It records why more powerful mechanisms were intentionally not selected.

---

# 32. Capability Selection Per Transition

Capabilities are not limited to Processes.

Transitions may require capabilities.

Example:

```text
P1
 ↓
score >= 80?
```

The decision can be:

```text
Python
```

rather than:

```text
Agent
```

Another:

```text
P1
 ↓
Is this interpretation acceptable?
```

may require:

```text
Human Review
```

Therefore evaluate:

```text
Process capability
+
Transition capability
+
State capability
+
External capability
```

---

# 33. Capability Selection for State

State requirements may imply capabilities such as:

```text
state persistence
checkpointing
artifact storage
memory
observability
```

The question should be:

> What state behavior does the architecture require?

not:

> Should we use Memory?

For example:

```text
Current execution state
```

does not automatically require Memory.

It may only require Flow state.

---

# 34. Capability Selection for Failure Handling

Failure planning may create capability requirements.

Examples:

```text
Need deterministic retry logic
    → Flow/Python

Need external operation status
    → Tool/MCP

Need resumability
    → Checkpointing

Need human escalation
    → Human Review

Need dynamic fallback selection
    → possibly Agent/Planning
```

Failure architecture therefore contributes directly to capability selection.

---

# 35. Capability Selection for Human Review

If the previous stage identified:

```text
Human Approval Required
```

the capability requirement is:

```text
Human interaction / approval gate
```

Do not replace human judgment with an LLM simply because an automated alternative exists.

Likewise, do not add human approval when deterministic validation is sufficient.

---

# 36. Capability Escalation Ladder

Amsha should reason from simpler to more powerful mechanisms.

A useful conceptual ladder is:

```text
Level 0
Deterministic Logic
        ↓
Level 1
Single LLM Capability
        ↓
Level 2
Agent + Task
        ↓
Level 3
Crew
        ↓
Level 4
Flow
        ↓
Level 5
Flow + Crew
        ↓
Additional capabilities
Knowledge / Memory / Tools / MCP /
Reasoning / Planning / Human / Checkpointing
```

This is not a hierarchy of "better" technologies.

It represents increasing architectural complexity.

Use the lowest level that satisfies the requirement.

---

# 37. Avoid Capability Cargo Cult

Do not add a capability because:

```text
it is modern
it is available
another project uses it
the framework supports it
the workflow sounds complex
```

Every capability should answer:

```text
What requirement does this satisfy?
```

If there is no good answer:

```text
Do not select it.
```

---

# 38. Capability Rejection Is Valuable

A high-quality architecture should record not only what it uses but what it intentionally does not use.

Example:

```yaml
capabilities:
  selected:
    - Flow
    - Crew
    - Knowledge
    - Python

  rejected:
    - Memory:
        reason: "No cross-execution information is required."

    - Planning:
        reason: "Workflow sequence is deterministic."

    - MCP:
        reason: "No external capability boundary is required."

    - Reasoning:
        reason: "Existing Agent reasoning is sufficient."
```

This prevents later architecture drift.

---

# 39. Capability Minimality

A capability set is minimal when removing any selected capability would cause an architectural requirement to become unsatisfied.

Conceptually:

```text
Selected Capabilities
        ↓
Remove one
        ↓
Requirement still satisfied?
   ├── YES → capability may be unnecessary
   └── NO  → capability justified
```

This is a useful Amsha validation principle.

---

# 40. Capability Sufficiency

Minimality alone is not enough.

The selected capabilities must also be sufficient.

```text
Capability Set
       ↓
Can it implement every approved Process?
       ↓
Can it implement Flow transitions?
       ↓
Can it satisfy state requirements?
       ↓
Can it handle required failure paths?
       ↓
Can it satisfy human/external requirements?
```

If not:

```text
Capability set is incomplete.
```

---

# 41. Capability Complexity Budget

Capability selection should consider the complexity introduced by each mechanism.

For example:

```text
Python
  complexity: low

Agent
  complexity: moderate

Crew
  complexity: higher

Flow + Crew + Memory + MCP + Planning
  complexity: high
```

The exact values are not important.

The principle is:

> **Additional architectural machinery must provide corresponding value.**

---

# 42. Token and Runtime Cost

Capability selection should also consider:

* prompt tokens
* context size
* LLM calls
* latency
* tool calls
* memory retrieval
* model cost
* execution overhead

Example:

```text
Requirement:
Calculate deterministic score.
```

Using an LLM introduces unnecessary:

```text
token cost
latency
nondeterminism
```

Python is therefore superior.

For LLM-required work, choose the smallest sufficient prompt/context and capability structure.

---

# 43. Reliability Consideration

Capability selection should consider determinism.

Prefer deterministic mechanisms for:

```text
rules
validation
calculations
routing
state transitions
schema checks
```

Use LLMs where:

```text
interpretation
generation
semantic reasoning
creative judgment
```

is genuinely required.

This creates:

```text
Deterministic Control
+
Probabilistic Intelligence
```

rather than an entirely probabilistic workflow.

---

# 44. Security and Permission Boundaries

Capability selection should consider what each capability is allowed to do.

For example:

```text
Agent
 ↓
Tool
 ↓
External System
```

creates a permission boundary.

The architecture should ask:

* Does the Process really need this capability?
* What data can it access?
* What actions can it perform?
* Can access be restricted?
* Can destructive operations be isolated?

Least capability is also a security principle.

---

# 45. Capability Selection Example

Suppose the approved workflow is:

```text
P1 Analyze Source
P2 Define Requirements
P3 Generate Chapter
P4 Evaluate Chapter
P5 Improve Chapter
H1 Human Approval
```

Flow:

```text
P1
 ↓
P2
 ↓
P3
 ↓
P4
 ↓
Pass?
 ├── NO → P5 → P4
 └── YES → H1
              ↓
           APPROVED
              ↓
             END
```

Capability analysis:

### P1 Analyze Source

Requires semantic analysis.

```text
Agent + Task
Knowledge
```

### P2 Define Requirements

Requires structured reasoning based on source analysis.

```text
Agent + Task
```

### P3 Generate Chapter

Requires creative generation.

```text
Agent + Task
Knowledge
```

### P4 Evaluate Chapter

Requires multi-dimensional professional evaluation.

Potentially:

```text
Crew
```

if multiple independent specialist perspectives are genuinely required.

### P5 Improve Chapter

Requires creative revision.

```text
Agent + Task
```

### Pass Decision

If based on deterministic evaluation criteria:

```text
Python
```

### Human Approval

```text
Human Review
```

### Workflow

```text
Flow
```

### State

```text
Flow State
```

### Memory

Not required unless cross-execution history is needed.

### Planning

Not required because the workflow sequence is known.

### MCP

Not required unless external systems are involved.

The resulting architecture might therefore be:

```text
Flow
 ├── Agent + Task
 ├── Agent + Task
 ├── Agent + Task
 ├── Crew
 ├── Python
 ├── Agent + Task
 └── Human Review

Knowledge
Flow State
Observability
```

rather than automatically enabling every CrewAI capability.

---

# 46. Capability Selection Output

The output should be machine-readable.

Conceptual schema:

```yaml
capability_selection:
  principles:
    minimality: true
    sufficiency: true
    deterministic_first: true

  capabilities:
    - id: ""
      capability: ""
      scope: ""
      reason: ""
      required_for: []

  process_mapping:
    - process_id: ""
      primary: ""
      supporting: []
      rationale: ""

  transition_mapping:
    - transition_id: ""
      capability: ""
      rationale: ""

  state_requirements:
    flow_state: true
    memory: false
    checkpointing: false

  external_requirements:
    tools: []
    mcp: []

  human_requirements:
    gates: []

  rejected:
    - capability: ""
      reason: ""

  cost_considerations:
    token: []
    runtime: []
    operational: []

  open_questions: []
```

---

# 47. Capability Selection Validation

Before proceeding to final architecture validation, verify:

## Sufficiency

* [ ] Every Process has sufficient implementation capability.
* [ ] Every transition can be implemented.
* [ ] State requirements are covered.
* [ ] Human requirements are covered.
* [ ] External dependencies are covered.
* [ ] Failure requirements are covered.

## Minimality

* [ ] No unnecessary Crew exists.
* [ ] No unnecessary Agent exists.
* [ ] No unnecessary Flow exists.
* [ ] No unnecessary Memory exists.
* [ ] No unnecessary Knowledge exists.
* [ ] No unnecessary Planning exists.
* [ ] No unnecessary Reasoning exists.
* [ ] No unnecessary Tool exists.
* [ ] No unnecessary MCP integration exists.

## Determinism

* [ ] Deterministic logic uses deterministic mechanisms where possible.
* [ ] LLMs are used where semantic intelligence is actually required.
* [ ] State transitions are not unnecessarily delegated to LLMs.

## Cost

* [ ] Token-heavy capabilities have justification.
* [ ] Context requirements are minimal.
* [ ] Iterative LLM execution is bounded.
* [ ] Expensive capabilities are used only where necessary.

## Security

* [ ] Tool access is scoped.
* [ ] External access is justified.
* [ ] Destructive capabilities are controlled.
* [ ] Human approval is used where required.

---

# 48. Anti-Patterns

## 48.1 Crew for Everything

```text
Every Process
    ↓
Crew
```

Wrong unless every Process genuinely requires collaboration.

---

## 48.2 Agent for Deterministic Logic

```text
Calculate total
    ↓
Agent
```

Use Python.

---

## 48.3 Flow for One Simple Operation

```text
One calculation
    ↓
Flow
```

A Flow adds unnecessary orchestration.

---

## 48.4 Memory for Current State

```text
Pass Process output
    ↓
Memory
```

Use Flow state or Process context.

---

## 48.5 Knowledge Dump

```text
Entire knowledge base
    ↓
Every Agent
```

Use relevant retrieval.

---

## 48.6 Planning a Known Workflow

```text
Known:
P1 → P2 → P3

Implementation:
Autonomous Planner
```

Use Flow.

---

## 48.7 MCP Everywhere

```text
Local function
    ↓
MCP server
```

Do not introduce an external integration boundary without a reason.

---

## 48.8 LLM for Routing

```text
score = 95
    ↓
LLM decides "pass"
```

Use deterministic logic.

---

## 48.9 Capability by Framework Availability

Bad reasoning:

```text
CrewAI supports X
        ↓
Use X
```

Correct reasoning:

```text
Architecture requires X
        ↓
Use X
```

---

# 49. Capability Selection Decision Procedure

For each architectural requirement:

```text
1. What exactly must be done?
        ↓
2. Is it deterministic?
        ↓
   YES → deterministic mechanism
   NO
        ↓
3. Does it require semantic intelligence?
        ↓
   NO → simpler mechanism
   YES
        ↓
4. Does it require one professional capability?
        ↓
   YES → Agent / Task
   NO
        ↓
5. Does it require multiple specialists collaborating?
        ↓
   YES → Crew
        ↓
6. Does the overall workflow require explicit orchestration?
        ↓
   YES → Flow
        ↓
7. Does it require external capabilities?
        ↓
   Tool / MCP
        ↓
8. Does it require reference information?
        ↓
   Knowledge
        ↓
9. Does it require historical retention?
        ↓
   Memory
        ↓
10. Does it require dynamic planning?
        ↓
   Planning
        ↓
11. Does it require explicit human judgment?
        ↓
   Human Review
```

At every step ask:

> Can a simpler mechanism already satisfy the requirement?

---

# 50. Relationship to Architecture Validation

Capability selection does not mean the architecture is finished.

The next stage must validate:

```text
Problem
Goal
Processes
Contracts
Flow
State
Failure Handling
Capabilities
```

as one coherent architecture.

The final validation should detect situations such as:

```text
Process requires Crew
but selected Agent

Process requires external capability
but no Tool/MCP exists

Flow requires persistent recovery
but no checkpoint strategy exists

Workflow requires historical context
but Memory is absent

Deterministic decision
implemented through unnecessary LLM reasoning
```

---

# 51. Final Capability Model

At the end of this stage, Amsha should have a mapping:

```text
ARCHITECTURAL REQUIREMENT
        ↓
CAPABILITY REQUIRED
        ↓
MINIMUM SUFFICIENT MECHANISM
```

For example:

```text
Calculate score
    ↓
Deterministic computation
    ↓
Python

Generate chapter
    ↓
Professional creative capability
    ↓
Agent + Task

Multi-specialist evaluation
    ↓
Collaborative expertise
    ↓
Crew

Coordinate workflow
    ↓
Explicit orchestration
    ↓
Flow

Story reference
    ↓
Domain knowledge
    ↓
Knowledge

Previous decisions
    ↓
Historical retention
    ↓
Memory

External asset generation
    ↓
External capability
    ↓
MCP / Tool

Final creative approval
    ↓
Human judgment
    ↓
Human Review
```

---

# 52. Core Amsha Rules

### Rule 1

> **Select capabilities from requirements, not from framework features.**

### Rule 2

> **Use the least powerful mechanism that reliably satisfies the requirement.**

### Rule 3

> **Prefer deterministic mechanisms for deterministic work.**

### Rule 4

> **Use Agents for professional intelligence, not as generic wrappers around every operation.**

### Rule 5

> **Use Crews when genuine multi-specialist collaboration is required.**

### Rule 6

> **Use Flow for orchestration, state, transitions, iteration, parallelism, and workflow control.**

### Rule 7

> **Do not use Crew as a substitute for Flow.**

### Rule 8

> **Do not use Memory as a substitute for Flow state.**

### Rule 9

> **Do not use Planning when the workflow sequence is already known.**

### Rule 10

> **Do not use LLMs for deterministic routing, validation, or calculation when deterministic logic is sufficient.**

### Rule 11

> **Knowledge provides reference information; Context determines what is relevant now.**

### Rule 12

> **MCP is an external capability boundary, not automatically a replacement for local Tools.**

### Rule 13

> **Human review is a capability for decisions that genuinely require human judgment.**

### Rule 14

> **Every selected capability should have an explicit architectural justification.**

### Rule 15

> **Intentional non-selection is part of architecture quality.**

### Rule 16

> **Capability selection must satisfy the entire Process, Flow, State, and Failure architecture.**

---

# 53. Final Architecture Boundary

The prerequisite architecture can now be represented as:

```text
USER PROBLEM
     ↓
GOAL & BOUNDARY
     ↓
PROCESS DECOMPOSITION
     ↓
PROCESS CONTRACTS
     ↓
PROCESS VALIDATION
     ↓
FLOW & STATE
     ↓
CORNER CASES & FAILURE
     ↓
CAPABILITY SELECTION
     ↓
┌─────────────────────────────────────┐
│ Minimum Sufficient Implementation   │
│                                     │
│ Python                              │
│ Agent                               │
│ Task                                │
│ Crew                                │
│ Flow                                │
│ Knowledge                           │
│ Memory                              │
│ Reasoning                           │
│ Planning                            │
│ Tools                               │
│ MCP                                 │
│ Human Review                        │
│ Checkpointing                       │
│ Observability                       │
└─────────────────────────────────────┘
     ↓
08 Architecture Validation
```

The key architectural transformation is:

```text
Problem
   ↓
Required Work
   ↓
Required Execution Structure
   ↓
Required Failure Behavior
   ↓
Required Capabilities
   ↓
Minimum Sufficient Architecture
```

This is the point where Amsha moves from **problem/process reasoning** into **implementation architecture reasoning**.

The next stage, `08-architecture-validation.md`, should validate the complete architecture as a whole before Amsha begins Agent, Task, Crew, Flow, Knowledge, Memory, Tool, MCP, and implementation engineering.

```
```
