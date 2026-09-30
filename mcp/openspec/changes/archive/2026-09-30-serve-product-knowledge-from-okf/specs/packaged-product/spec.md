# Packaged Product Knowledge

## ADDED Requirements

### Requirement: Product knowledge is projected from existing repository artifacts

The MCP server MUST answer Amsha product questions from knowledge that is
projected mechanically from artifacts already present in the Amsha repository,
rather than from documentation authored inside the MCP package.

The projection sources are the Amsha `knowledge/features/` concepts, the
`openspec/specs/` behaviour specs, the README's Installation and Quick Start
sections, and the `requires-python` constraint from `pyproject.toml`. Every value
in a projected concept MUST be copied from, or mechanically derived from, one of
those sources. Authoring a second, independent statement of the same fact in the
MCP tree is a defect, not a fallback.

The projection output MUST be committed, so that `mcp/` can be built and
distributed without the Amsha repository present.

#### Scenario: A projected module concept

- **GIVEN** an Amsha module that has a `knowledge/features/` concept
- **WHEN** the projection runs
- **THEN** `mcp/knowledge/product/<module>.md` exists
- **AND** its description is taken from that concept, not reworded

#### Scenario: A declared version constraint

- **GIVEN** an Amsha `pyproject.toml` declaring `requires-python`
- **WHEN** the projection runs
- **THEN** the projected installation concept carries that exact constraint
- **AND** the constraint is not hardcoded anywhere in the server's tool code

### Requirement: Projection drift is detectable

Running the projection in check mode MUST fail when the committed product
knowledge differs from what the current repository artifacts would generate, so
that a change to Amsha's documentation cannot leave the MCP bundle silently
stale.

#### Scenario: Source documentation changes without reprojection

- **GIVEN** a committed product concept
- **AND** a repository artifact that concept was generated from has changed
- **WHEN** the projection is run in check mode
- **THEN** it exits non-zero
- **AND** it reports which concept is out of date

### Requirement: Packaged product documents carry no frontmatter

The product documents shipped inside the `amsha_mcp` package MUST NOT contain
YAML frontmatter, so that no frontmatter delimiter or lifecycle field can appear
in text the server returns to an agent. Machine-readable product metadata
required at runtime MUST be derivable from the packaged form — from the filename
and body — rather than from a header that has been stripped.

#### Scenario: Preview of a packaged product concept

- **GIVEN** a packaged product concept
- **WHEN** the server returns a preview of that document
- **THEN** the preview contains no frontmatter delimiter

#### Scenario: Module purpose from a packaged concept

- **GIVEN** a packaged product concept for a module
- **WHEN** the server needs that module's purpose
- **THEN** it derives the module identity from the concept's filename
- **AND** it takes the purpose from the concept's prose, not from a header

### Requirement: Product questions are answerable with no repository registered

The server MUST answer what modules Amsha provides, what a given module does, and
how to install and start Amsha, with no target repository registered. These are
properties of the Amsha product and do not vary with whichever repository the
server is pointed at.

The declared module inventory and the per-module purposes MUST come from the
packaged product knowledge.

#### Scenario: Listing modules standalone

- **GIVEN** no target repository is registered
- **WHEN** the server lists Amsha's modules
- **THEN** it returns every declared module
- **AND** each carries the purpose from its packaged product concept

#### Scenario: Explaining a module standalone

- **GIVEN** no target repository is registered
- **WHEN** the server explains a declared module
- **THEN** it returns the module's purpose
- **AND** it returns documentation for it from the packaged product concept

#### Scenario: Installation instructions standalone

- **GIVEN** no target repository is registered
- **WHEN** the server returns installation instructions
- **THEN** it returns the install command, the optional extra, and the Python
  version constraint
- **AND** it does not fall back to a string that refers to a README the process
  does not have

#### Scenario: Quick Start standalone

- **GIVEN** no target repository is registered
- **WHEN** the server returns the Quick Start
- **THEN** it returns the procedure from the packaged product knowledge
- **AND** the returned procedure contains no editorial or provenance prose

### Requirement: A registered repository narrows but never empties the module list

When a target repository is registered, it MAY narrow the module list to the
modules that checkout actually contains, because a pinned or vendored Amsha may
differ from the current release. Narrowing MUST NOT remove the source of the
purposes, and MUST NOT depend on a repository existing for the product questions
above to have answers.

A repository-specific capability such as a source-file listing MUST remain
repository-scoped, and an empty result for it is correct when no repository is
registered.

#### Scenario: Repository contains a subset of modules

- **GIVEN** a registered target repository that contains fewer modules than the
  declared inventory
- **WHEN** the server lists Amsha's modules
- **THEN** it returns the intersection
- **AND** the returned purposes still come from the packaged product concepts

#### Scenario: Source files with no repository

- **GIVEN** no target repository is registered
- **WHEN** the server explains a module
- **THEN** its source-file list is empty
- **AND** its purpose and documentation are still populated

### Requirement: Procedure concepts contain no editorial preamble

A projected procedure concept's body MUST be the source section verbatim. The
projector MUST NOT prepend explanatory or provenance prose to the body, because
the server serves the body as the procedure itself and any added prose would be
returned to the caller as an instruction to follow. Provenance MUST be recorded
in the concept's frontmatter instead.

#### Scenario: Served Quick Start fidelity

- **GIVEN** a projected Quick Start concept generated from a README section
- **WHEN** the server returns the Quick Start with no repository registered
- **THEN** the returned text is the source section
- **AND** it does not begin with a sentence describing how the document was
  generated
