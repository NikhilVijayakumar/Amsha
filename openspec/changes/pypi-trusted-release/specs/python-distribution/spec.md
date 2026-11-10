## ADDED Requirements

### Requirement: Distributable Python package

Amsha SHALL provide a wheel and source distribution containing its Python library, metadata and license while preserving the `amsha` import namespace and declared dependencies. See [Python distribution knowledge](../../../../../knowledge/features/python-distribution.md).

#### Scenario: Consumer installs a wheel

- **GIVEN** a built wheel and compatible Python environment
- **WHEN** a consumer installs the wheel
- **THEN** the `amsha` package resolves from that environment without a source checkout.

### Requirement: Verified trusted release

The publishing workflow SHALL validate the tag and run tests and distribution checks before uploading the built artifacts through PyPI trusted publishing.

#### Scenario: Release tag does not match

- **GIVEN** a tag that differs from the package version
- **WHEN** the release workflow runs
- **THEN** it SHALL fail before upload.

#### Scenario: Maintainer approval before PyPI upload

- **GIVEN** a configured `pypi` GitHub environment with required approval
- **WHEN** a validated release awaits the publish job
- **THEN** the upload SHALL wait until the environment approval is granted.
