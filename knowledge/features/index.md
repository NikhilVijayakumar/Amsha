# Features

One concept per module under `src/nikhil/amsha/`. Nine live, one retired.

* [common](common.md) - Structured logging and execution metrics. Internal, not a selectable capability.
* [configuration](configuration.md) - Job, app, and LLM configuration schemas.
* [crew-forge](crew-forge.md) - Turns crew definitions into runnable CrewAI crews and flows. The entry point for most clients.
* [crew-gen](crew-gen.md) - Retired. Kept to record intent and history; no source remains.
* [crew-monitor](crew-monitor.md) - Resource usage, event lifecycle, agent contribution, Excel reporting.
* [execution-runtime](execution-runtime.md) - Bounded thread pool with a cancellable handle protocol.
* [execution-state](execution-state.md) - Execution lifecycle model with an injected state repository.
* [llm-factory](llm-factory.md) - Builds provider-agnostic LLM instances from one configuration.
* [output-process](output-process.md) - JSON cleaning. The evaluation and validation subpackages are unbuilt stubs.
* [utils](utils.md) - JSON, YAML, and UTF-8 format helpers.
