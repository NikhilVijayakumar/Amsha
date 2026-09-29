# Documentation Surface

## Purpose

documentation is either covered as a live capability, represented as durable
Defines how repository documentation is represented after the migration of the
legacy `docs/feature/`, `docs/proposal/`, and `docs/archived/` trees into the
OKF knowledge bundle and OpenSpec current-state specs, while preserving
`docs/research/` as an intentional exception.

Knowledge concept: [knowledge/decisions/documentation-coverage.md](../../../knowledge/decisions/documentation-coverage.md)

## Requirements

### Requirement: Legacy product-doc trees are migrated out of docs/

Legacy product-documentation trees for features, proposals, and archived
historical notes MUST be represented in `knowledge/` and `openspec/specs/`
rather than remaining as active trees under `docs/`.

#### Scenario: Live feature content is migrated

- **WHEN** a live runtime capability is represented after migration
- **THEN** a matching concept exists in `knowledge/features/`
- **AND** a matching current-state spec exists in `openspec/specs/`
- **AND** no separate `docs/feature/` tree is required for it

#### Scenario: Retired feature content remains visible

- **WHEN** a retired capability is represented after migration
- **THEN** a deprecated knowledge concept or retirement record preserves it
- **AND** a current-state spec records its retired status rather than treating it as live behaviour

#### Scenario: Proposal and archived trees are removed

- **WHEN** the repository no longer keeps `docs/proposal/` or `docs/archived/`
- **THEN** their durable migration targets remain represented in knowledge or specs
- **AND** removing the legacy trees does not leave product behaviour unmapped

### Requirement: Reference documentation is represented as OKF reference surfaces

Documentation used for onboarding, operator guidance, skills, rules, testing,
or execution reporting MUST be represented in the OKF bundle as reference
surfaces. These reference documents MUST NOT require one OpenSpec runtime spec
per file when they do not define product behaviour directly.

#### Scenario: Integration guide is represented

- **WHEN** `docs/integration-guide/` is reviewed
- **THEN** it is represented by an OKF reference concept
- **AND** its underlying module behaviours remain specified by the relevant capability specs

#### Scenario: Agent and testing references are represented

- **WHEN** `docs/reference/` and `docs/test-execution/` are reviewed
- **THEN** they are represented by OKF reference concepts
- **AND** they are classified as reference documentation rather than live runtime capabilities

### Requirement: Research documentation remains outside the migration

`docs/research/` MUST remain intact and MUST be treated as intentionally
outside the OKF/OpenSpec migration because it serves paper and research work,
not current product or repository-governance behaviour.

#### Scenario: Research documentation is reviewed

- **WHEN** the repository documentation tree is reviewed for OpenSpec/OKF coverage
- **THEN** `docs/research/` is treated as intentionally excluded
- **AND** it is not required to have matching OKF concepts or OpenSpec specs
