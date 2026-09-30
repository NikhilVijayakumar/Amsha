# Documentation Discovery

## Purpose

Defines how the Amsha MCP server locates and serves its bundled methodology
information, how it resolves the target repository lazily for repo-plane
lookups, and how it enumerates the Amsha runtime modules it can explain.
These rules prevent silent empty responses caused by path drift, incomplete
module inventory, or an uninitialized repository root.

Knowledge context: [mcp/knowledge/methodology/index.md](../../../knowledge/methodology/index.md) and [mcp/knowledge/records/index.md](../../../knowledge/records/index.md)

## Requirements

### Requirement: Target repository resolves without an eager initializer

Every repository-plane accessor MUST resolve the target repository through
the documented lazy accessor, so that its behaviour does not depend on
whether a server module happened to be imported first. A process that
configures a target repository and calls a repository-plane tool directly
MUST receive repository content.

#### Scenario: Repository-plane tool used as a library

- **GIVEN** a target repository is configured
- **WHEN** a caller invokes a repository-plane tool without importing the server module
- **THEN** the tool returns content from that repository
- **AND** it does not report the repository as unregistered

#### Scenario: No repository configured

- **GIVEN** no target repository is configured and none can be discovered
- **WHEN** a caller invokes a repository-plane tool
- **THEN** the tool reports the absence of a repository
- **AND** it does not raise an error

#### Scenario: Resolution is idempotent

- **WHEN** resolution is triggered more than once for the same target repository
- **THEN** the resolved repository is unchanged

#### Scenario: Explicitly cleared repository

- **GIVEN** the target repository was previously configured and then explicitly cleared
- **WHEN** a caller invokes a repository-plane tool
- **THEN** the tool reports the absence of a repository

### Requirement: Packaged documentation resolution

The server MUST resolve bundled methodology documentation through the
packaged `docs_loader` accessors, and MUST NOT reconstruct a documentation
path from the repository directory layout. Resolution MUST continue to work
when no repository is registered, because the documentation ships inside
the wheel.

#### Scenario: Prerequisite documentation is available in the package

- **WHEN** the server resolves the methodology documentation for prerequisite stage `03`
- **THEN** it returns the content of the packaged `03-process-contracts-and-atomicity.md`
- **AND** the returned content is the same whether or not a repository is registered

#### Scenario: Server is installed as a standalone wheel

- **WHEN** no repository is registered and a caller requests prerequisite stage `00`
- **THEN** the server returns the packaged problem-definition document
- **AND** it does not return an empty string

#### Scenario: Repository layout differs from package layout

- **GIVEN** the repository contains a `mcp/docs/` directory that does not hold the methodology documents
- **WHEN** the server resolves prerequisite documentation
- **THEN** it resolves against the packaged location
- **AND** the unrelated repository directory is not consulted

#### Scenario: Requested stage has no packaged document

- **WHEN** a stage identifier has no corresponding packaged document
- **THEN** the server reports the absence explicitly
- **AND** it does not present an empty string as a successful lookup

### Requirement: Runtime module inventory completeness

The server's runtime module inventory MUST list every supported Amsha runtime
module. The inventory MAY exclude a module only when the exclusion is stated in
code with its rationale.

The inventory and each module's purpose MUST be served from packaged product
knowledge, because the set of modules Amsha provides is a property of the
product and does not vary with whichever repository the server is pointed at. A
registered repository MAY narrow the list to the modules that checkout actually
contains, since a pinned or vendored Amsha may differ from the current release,
but narrowing MUST NOT be the reason a module has a purpose.

A repository-specific capability such as a source-file listing MUST remain
repository-scoped, and an empty result for it is correct when no repository is
registered.

#### Scenario: Configuration module is listed

- **WHEN** a caller lists the Amsha runtime modules
- **THEN** `configuration` is present in the result
- **AND** a one-line purpose is returned for it

#### Scenario: Configuration module is explained

- **WHEN** a caller requests an explanation of the `configuration` module
- **THEN** the server returns its purpose, documentation pointers, and source files
- **AND** it does not report the module as unknown

#### Scenario: Inventory is complete with no repository registered

- **GIVEN** no target repository is registered
- **WHEN** a caller lists the Amsha runtime modules
- **THEN** every declared module is present
- **AND** each purpose comes from its packaged product concept

#### Scenario: Internal module is excluded

- **GIVEN** `common` is excluded because it is not a user-facing capability
- **WHEN** a caller lists the Amsha runtime modules
- **THEN** `common` is absent from the result
- **AND** the exclusion is documented in the inventory declaration

#### Scenario: Module absent from the source tree

- **GIVEN** an inventory entry names a module that is not present under the
  registered repository's `src/nikhil/amsha/`
- **WHEN** a caller lists the Amsha runtime modules
- **THEN** the missing module is omitted from the result rather than returned
- **AND** the remaining modules keep their packaged purposes

#### Scenario: Procedure references are not modules

- **GIVEN** the product plane contains procedure references alongside module concepts
- **WHEN** a caller lists the Amsha runtime modules
- **THEN** no procedure reference appears as a module

### Requirement: Knowledge plane independence

Repository-sourced documentation MUST degrade to empty when no repository is
registered, and packaged documentation MUST never depend on repository
documentation being present.

A question about the Amsha product — which modules it has, what one does, how to
install and start it — MUST NOT be answered by a repository-plane read. Where a
packaged concept and a repository document both address such a question, the
packaged concept is the answer and the repository document MAY supply additional
detail.

#### Scenario: Repository documentation is requested with no repository

- **WHEN** a caller requests repository documentation and no repository is registered
- **THEN** the server returns an empty result for repository-sourced entries
- **AND** packaged methodology documentation remains fully available

#### Scenario: Packaged documentation is requested with a repository registered

- **GIVEN** a repository is registered
- **WHEN** a caller requests packaged methodology documentation
- **THEN** the result is identical to the result returned with no repository registered

#### Scenario: Product questions do not depend on a repository read

- **GIVEN** no target repository is registered
- **WHEN** a caller asks which modules Amsha provides, what one does, or how to
  install and start it
- **THEN** the server answers from packaged product knowledge
- **AND** it does not return an empty result or a pointer to documentation the
  process does not have

#### Scenario: Repository document preferred when present

- **GIVEN** a registered target repository containing a richer per-module page
- **WHEN** a caller asks about that module
- **THEN** the server returns the repository's page
- **AND** where the repository has no such page, the packaged concept is returned
  instead

### Requirement: Product knowledge is searchable under a distinct namespace

Product knowledge MUST be included in documentation search, and its hits MUST
identify which plane they came from, so that two groups sharing a filename
cannot mask one another or mis-attribute a hit.

#### Scenario: Product knowledge is discoverable

- **GIVEN** no target repository is registered
- **WHEN** a caller searches for a term that appears only in product knowledge
- **THEN** the product document is among the hits

#### Scenario: Shared filenames do not collide

- **GIVEN** a product bundle and a repository knowledge bundle that both contain a
  document of the same name
- **WHEN** a caller searches the documentation
- **THEN** each hit identifies its own plane
- **AND** neither document masks the other
