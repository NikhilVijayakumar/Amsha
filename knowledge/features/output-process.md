---
type: Module
title: Output Process
description: Post-processes structured crew output — currently JSON cleaning only; the evaluation and validation subpackages are unbuilt stubs.
tags: [amsha, capability, output, incomplete]
generated: { by: "opencode/big-pickle", at: 2026-09-29T00:00:00Z }
stale_after: 2026-12-29T00:00:00Z
sources:
  - id: output-process-src
    resource: ../../src/nikhil/amsha/output_process
    title: Output Process source tree
    author: team:amsha
---

# Output Process

Handles crew output after generation. It is the smallest documented surface in
Amsha and the one furthest from its intended shape.

## What exists

One implementation, 179 lines: `optimization/json_cleaner_utils.py`.

`JsonCleanerUtils(input_file_path, output_folder=None)` strips markdown
fences and surrounding prose from LLM output that is meant to be JSON. It
derives an output path, de-duplicates collisions via `_get_unique_filepath`,
and ensures the output directory exists. This is the `clean_json()` behaviour
that `AmshaCrewFileApplication` exposes to clients.

## What does not exist

Five non-`__init__` files in this module are **0 bytes**:

```
evaluation/evaluation_aggregate_tool.py
evaluation/evaluation_processing_tool.py
evaluation/evaluation_report_tool.py
validation/crew_validator.py
validation/json_output_validator.py
```

The directory structure therefore promises three capabilities — optimisation,
evaluation, and validation — of which only optimisation is implemented. The
`evaluation/` and `validation/` subpackages import cleanly and expose nothing.

This is recorded here rather than left to be discovered, because the module
name and layout suggest completeness that the code does not have. Anything
depending on output evaluation or output validation will find empty modules.

`stale_after` on this concept is set to three months rather than six: it is
the concept most likely to change, precisely because the gaps are known and
outstanding.

## Related

- [Crew Forge](./crew-forge.md) — produces the output this module processes
- [Utils](./utils.md) — JSON helpers used alongside
