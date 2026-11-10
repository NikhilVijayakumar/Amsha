# Proposal: PyPI trusted release

## Why

Amsha needs a standard, versioned Python distribution and an auditable release path rather than relying on source checkouts.

## What Changes

- Add public package metadata and an MIT license, and correct the installed-package import examples.
- Build and validate wheel and source distributions. Run CI on pushes to `master` and publish matching version tags through a protected PyPI environment using trusted publishing.
- Keep the existing `amsha` import namespace, declared dependencies and extras.

This changes externally visible distribution behavior for the whole library; it does not modify runtime modules. The MCP distribution is out of scope. Actual registry access, environment protection and initial publication require external setup.

## Capabilities

- `python-distribution`: built artifacts, validation and PyPI release behavior.

## Impact

Metadata, documentation, GitHub Actions and distributable archives. Knowledge: `knowledge/features/python-distribution.md`.
