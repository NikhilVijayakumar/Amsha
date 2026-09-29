# Spec Delta

## Purpose

Defines how the 43 product-plane methodology documents are authored and how
they reach the installed package: a repo-side OKF bundle is the single source of
truth, a generator materializes it into the package tree with frontmatter
removed, and a check mode makes divergence between the two a build failure
rather than a silent degradation.

## ADDED Requirements

### Requirement: Methodology documents are authored as OKF concepts

Every product-plane methodology document MUST have exactly one authored source
in the MCP-local OKF bundle, carrying valid OKF frontmatter. No document may be
authored or hand-edited inside the package tree.

#### Scenario: Every product-plane document has one authored source

- **WHEN** the generator enumerates the OKF bundle
- **THEN** it accounts for exactly 43 concepts
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

### Requirement: Drift between bundle and package is detectable

The generator MUST provide a check mode that compares the bundle against the
packaged tree without modifying anything, and MUST exit non-zero when the
packaged tree is missing, stale, or contains files the bundle does not produce.

#### Scenario: Packaged tree up to date

- **WHEN** the check mode runs and the packaged tree matches the bundle
- **THEN** it exits zero
- **AND** it reports the number of files verified

#### Scenario: Packaged document edited after generation

- **GIVEN** a packaged document has been modified by hand
- **WHEN** the check mode runs
- **THEN** it exits non-zero
- **AND** it names the diverging file

#### Scenario: Packaged tree absent

- **GIVEN** the packaged documentation tree does not exist
- **WHEN** the check mode runs
- **THEN** it exits non-zero
- **AND** it reports that the tree is missing rather than reporting per-file diffs

#### Scenario: Unexpected file in the packaged tree

- **GIVEN** the packaged tree contains a file the bundle does not produce
- **WHEN** the check mode runs
- **THEN** it exits non-zero
- **AND** it names the unexpected file

### Requirement: The build produces the product plane

Every packaging path MUST materialize the product plane from the bundle before
an artifact is produced. No shipped artifact may contain a product plane that
diverges from the bundle.

#### Scenario: Standalone build from a clean tree

- **GIVEN** a source tree with no generated product plane
- **WHEN** a standalone build runs
- **THEN** the product plane is generated before packaging
- **AND** the resulting artifact contains all 43 documents

#### Scenario: Build with a divergent product plane

- **GIVEN** a product-plane document that does not match the bundle
- **WHEN** a build runs
- **THEN** the build fails
- **AND** it reports which document diverged
