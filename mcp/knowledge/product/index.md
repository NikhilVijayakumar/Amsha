# Product knowledge

Generated projections of Amsha's own knowledge: **8** runtime
module concepts and **2** procedure references.

## Runtime modules

| Module | Concept |
|---|---|
| `configuration` | [configuration](configuration.md) |
| `crew_forge` | [crew-forge](crew-forge.md) |
| `crew_monitor` | [crew-monitor](crew-monitor.md) |
| `execution_runtime` | [execution-runtime](execution-runtime.md) |
| `execution_state` | [execution-state](execution-state.md) |
| `llm_factory` | [llm-factory](llm-factory.md) |
| `output_process` | [output-process](output-process.md) |
| `utils` | [utils](utils.md) |

`common` is intentionally absent: it is cross-cutting internal
infrastructure and the server does not serve it. `crew-gen` is retired and
has no source module.

## Procedures

| Reference | Covers |
|---|---|
| [installation](installation.md) | Installing Amsha, including the optional docling extra |
| [quickstart](quickstart.md) | The first runnable crew |

## Generated, not authored

Every field here is copied or mechanically derived from an existing
Amsha artifact: `knowledge/features/*.md`, `openspec/specs/*/spec.md`, and the
README's Installation and Quick Start sections. Nothing is written by hand,
so this bundle cannot drift silently from the source:

```bash
python3 scripts/project_product_knowledge.py --check   # fails on drift
```

These concepts are packaged into the wheel, which is what lets the server
answer product questions with no repository registered.
