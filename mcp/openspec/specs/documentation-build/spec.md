# Documentation Build

## Purpose

Defines how the MCP-local OKF bundle is the single authored source of the
runtime methodology documents, how generation materializes that bundle into the
packaged product plane with frontmatter removed, and how build-time staging
works without requiring generated docs under `src/`. These rules keep
authoring, shipping, and wheel validation deterministic.

Knowledge context: [mcp/knowledge/index.md](../../../knowledge/index.md) and [mcp/knowledge/records/index.md](../../../knowledge/records/index.md)

## Requirements

### Requirement: Methodology documents are authored as OKF concepts

Every product-plane methodology document MUST have exactly one authored source
in the MCP-local OKF bundle, carrying valid OKF frontmatter. No document may be
authored or hand-edited inside the package tree.

#### Scenario: Every product-plane document has one authored source

- **WHEN** the generator enumerates the OKF bundle
- **THEN** it accounts for exactly 34 methodology concepts
- **AND** each concept maps to exactly one packaged destination
- **AND** no destination is produced by more than one source

#### Scenario: Source bundle conforms to OKF

- **WHEN** the OKF linter is run against the MCP-local bundle
- **THEN** every concept declares a non-empty `type` and a recognized `status`
- **AND** its `created` and `updated` fields are valid ISO timestamps
- **AND** the bundle's index files declare no lifecycle fields

### Requirement: Generation is deterministic and reversible

The generator MUST produce, for any given bundle, the same packaged tree on
every run, and MUST preserve each document body byte-for-byte from its authored
source apart from frontmatter removal.

#### Scenario: Repeated generation is stable

- **WHEN** the generator is run twice in succession against an unchanged bundle
- **THEN** the second run reports no change
- **AND** the packaged tree is byte-identical to the first run's output

#### Scenario: Body preservation

- **GIVEN** an authored concept whose body is arbitrary markdown
- **WHEN** the generator materializes it
- **THEN** the packaged body is byte-identical to the authored body
- **AND** only the frontmatter block is omitted

#### Scenario: Deterministic ordering

- **WHEN** the generator writes the packaged tree
- **THEN** the outcome does not depend on filesystem iteration order
- **AND** the same bundle produces the same result on any machine

### Requirement: Generation can be validated from a clean checkout

The generator MUST provide a check mode that validates the authored bundle can
be materialized without modifying anything. When a staged tree is present, the
check MUST compare against it and MUST exit non-zero when the staged tree is
stale or contains files the bundle does not produce.

#### Scenario: Packaged tree up to date

- **WHEN** the check mode runs and the packaged tree matches the bundle
- **THEN** it exits zero
- **AND** it reports the number of files verified

#### Scenario: Clean checkout with no staged tree

- **GIVEN** no staged product-plane tree exists yet
- **WHEN** the check mode runs
- **THEN** it exits zero
- **AND** it reports that the bundle is build-ready

#### Scenario: Packaged document edited after generation

- **GIVEN** a packaged document has been modified by hand
- **WHEN** the check mode runs
- **THEN** it exits non-zero
- **AND** it names the diverging file

#### Scenario: Unexpected file in the packaged tree

- **GIVEN** the packaged tree contains a file the bundle does not produce
- **WHEN** the check mode runs
- **THEN** it exits non-zero
- **AND** it names the unexpected file

### Requirement: The build produces the product plane

Every packaging path MUST materialize the product plane from the bundle before
an artifact is produced. No shipped artifact may contain a product plane that
diverges from the bundle, and no source checkout needs generated docs under
`src/` to answer methodology queries.

#### Scenario: Standalone build from a clean tree

- **GIVEN** a source tree with no generated product plane
- **WHEN** a standalone build runs
- **THEN** the product plane is generated before packaging
- **AND** the resulting artifact contains all 34 methodology documents

#### Scenario: Source checkout without packaged docs

- **GIVEN** a source checkout with no `src/amsha_mcp/docs/` tree
- **WHEN** the server answers a methodology query from source
- **THEN** it serves the authored methodology content with frontmatter removed
- **AND** no pre-generation step is required

#### Scenario: Build with a divergent product plane

- **GIVEN** a product-plane document that does not match the bundle
- **WHEN** a build runs
- **THEN** the build fails
- **AND** it reports which document diverged
