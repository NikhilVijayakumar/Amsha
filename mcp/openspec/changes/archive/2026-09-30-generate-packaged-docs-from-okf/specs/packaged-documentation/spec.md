# Spec Delta

## Purpose

Defines the contract of the Amsha MCP server's packaged methodology documents:
the filenames and directory layout its loaders depend on, the absence of
frontmatter in the shipped form, and the requirement that this knowledge remain
available with no repository registered. These are the invariants that make the
standalone wheel a self-sufficient product.

## ADDED Requirements

### Requirement: Packaged methodology documents carry no frontmatter

The methodology documents shipped inside the `amsha_mcp` package MUST NOT
contain YAML frontmatter, so that no frontmatter delimiter or lifecycle field
can appear in text the server returns to an agent.

The server's preview function does not strip frontmatter; it preserves every
non-empty line that is not a table row or a fenced block. Frontmatter is
therefore not a cosmetic concern but a correctness one.

#### Scenario: Preview of a packaged document

- **GIVEN** a packaged methodology document
- **WHEN** the server returns a preview of that document
- **THEN** the preview contains no frontmatter delimiter
- **AND** it contains no lifecycle field name such as `type`, `status`, or `created`

#### Scenario: Frontmatter present in the authored source

- **GIVEN** an authored methodology concept that carries OKF frontmatter
- **WHEN** the server serves the packaged form of that concept
- **THEN** the frontmatter is absent from the packaged form
- **AND** the document body is otherwise unchanged

### Requirement: Packaged document layout is fixed and loader-addressable

The packaged methodology tree MUST use the directory layout and filenames the
server's loaders address. The prerequisite stage filenames are referenced by
name in code and MUST NOT be renamed, moved, or re-cased.

#### Scenario: Prerequisite stage resolved by name

- **GIVEN** a prerequisite stage identifier between `00` and `09`
- **WHEN** the server resolves that stage's document
- **THEN** it resolves to a file that exists in the packaged tree
- **AND** its filename is the one the stage identifier is mapped to in code

#### Scenario: Implementation topics enumerated

- **WHEN** the server enumerates the packaged implementation documents
- **THEN** it returns exactly 24 documents
- **AND** each is a direct child of the implementation directory

### Requirement: Packaged knowledge is available with no repository registered

The packaged methodology documents MUST be served from the installed package
without consulting a target repository. A standalone installation that has no
repository configured MUST still answer methodology questions in full.

#### Scenario: Standalone install, no repository

- **GIVEN** no target repository is configured and none can be discovered
- **WHEN** the server enumerates the packaged methodology documents
- **THEN** it returns 10 prerequisite documents and 24 implementation documents
- **AND** it does not report a missing repository

#### Scenario: Repository registered

- **GIVEN** a target repository is configured
- **WHEN** the server enumerates the packaged methodology documents
- **THEN** the packaged results are the same as when no repository is configured
- **AND** repository-plane content is served in addition, not instead
