---
type: Module
title: Python distribution
description: The package boundary and release considerations for the Amsha Python library.
tags: [amsha, packaging, pypi, release]
generated: { by: "openai/codex", at: 2026-11-10T00:00:00Z }
stale_after: 2027-05-10T00:00:00Z
sources:
  - id: pyproject
    resource: ../../pyproject.toml
    title: Python package metadata
    author: team:amsha
---

# Python distribution

Amsha is a Python library distributed under the `amsha` project name, with the
`amsha` import namespace rooted in `src/nikhil`. Its package metadata defines
the supported Python versions, runtime dependencies, and optional extras; a
consumer does not need the source repository to install a wheel. Wheel and
source distribution contents, dependency resolution, and clean-environment
imports require verification for each release.

A trusted publisher connects an authenticated GitHub workflow to PyPI without
a stored upload token. A PyPI pending publisher can create a new project on
first upload, but it does not reserve the project name. Unlike a staged npm
release, a successful PyPI upload publishes the release. The release workflow uses
direct trusted publishing after checks, without a GitHub reviewer requirement;
PyPI may independently validate a release.

The library distribution is separate from the MCP distribution; see
[Two knowledge planes](../decisions/knowledge-planes.md).
