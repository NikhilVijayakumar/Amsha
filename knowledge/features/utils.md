---
type: Module
title: Utils
description: Small format helpers for JSON, YAML, and UTF-8 handling, shared across modules.
tags: [amsha, capability, utilities, internal]
generated: { by: "opencode/big-pickle", at: 2026-09-29T00:00:00Z }
stale_after: 2027-03-29T00:00:00Z
sources:
  - id: utils-src
    resource: ../../src/nikhil/amsha/utils
    title: Utils source tree
    author: team:amsha
---

# Utils

Three single-class modules with no dependencies of their own:

| Module | Class | Concern |
|---|---|---|
| `json_utils.py` | `JsonUtils` | JSON parsing, cleaning, serialisation |
| `yaml_utils.py` | `YamlUtils` | YAML loading, including the fenced-YAML handling agent and task files need |
| `utf8_utils.py` | `Utf8Utils` | Encoding-safe text handling |

These are leaf dependencies. Nothing in the codebase should import a module
that imports `utils` in a cycle — the value of these classes is that they are
small enough to depend on from anywhere.

## Boundary note

`utils` holds format helpers. It does not hold business logic, and code that
grows domain meaning here has outgrown its name. [Output
Process](./output-process.md) is the nearby example of a helper that did grow
into a module: `JsonCleanerUtils` there is output-specific, not a general
utility, and lives in its own module for that reason.

## Related

- [Output Process](./output-process.md)
- [Common](./common.md) — logging, the other cross-cutting concern
