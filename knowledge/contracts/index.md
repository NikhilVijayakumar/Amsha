# Contracts

Interfaces Amsha honours, and that clients implement or depend on. A contract
records what must be true across a boundary; a feature records what a module
is. Contracts here are sometimes derived from
[AGENTS.md](../../AGENTS.md) and the module layout rather than from an
extracted interface file, and say so when that is the case.

* [agent-reference-surface](agent-reference-surface.md) - The operator-facing rules and skill references under docs/reference/agent.
* [integration-guide-surface](integration-guide-surface.md) - The client-facing integration guide under docs/integration-guide/.
* [jobs/load/AtomicDbBuilderService](jobs-load-atomic-db-builder-service.md) - Assembling crews from atomic database-backed definitions.
* [llm-factory-build-result](llm-factory-build-result.md) - How provider configuration reaches the factory and what comes back.
* [testing-reference-surface](testing-reference-surface.md) - The testing templates, report examples, and execution notes under docs/reference/testing and docs/test-execution/.
