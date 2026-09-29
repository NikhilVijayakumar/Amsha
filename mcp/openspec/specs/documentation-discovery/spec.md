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

The server's runtime module inventory MUST list every supported Amsha
runtime module. The inventory MAY exclude a module only when the exclusion
is stated in code with its rationale.

#### Scenario: Configuration module is listed

- **WHEN** a caller lists the Amsha runtime modules
- **THEN** `configuration` is present in the result
- **AND** a one-line purpose is returned for it

#### Scenario: Configuration module is explained

- **WHEN** a caller requests an explanation of the `configuration` module
- **THEN** the server returns its purpose, documentation pointers, and source files
- **AND** it does not report the module as unknown

#### Scenario: Internal module is excluded

- **GIVEN** `common` is excluded because it is not a user-facing capability
- **WHEN** a caller lists the Amsha runtime modules
- **THEN** `common` is absent from the result
- **AND** the exclusion is documented in the inventory declaration

#### Scenario: Module absent from the source tree

- **GIVEN** an inventory entry names a module that is not present under `src/nikhil/amsha/`
- **WHEN** a caller lists the Amsha runtime modules
- **THEN** the missing module is omitted from the result rather than returned

### Requirement: Knowledge plane independence

Repository-sourced documentation MUST degrade to empty when no repository
is registered, and packaged documentation MUST never depend on repository
documentation being present.

#### Scenario: Repository documentation is requested with no repository

- **WHEN** a caller requests repository documentation and no repository is registered
- **THEN** the server returns an empty result for repository-sourced entries
- **AND** packaged methodology documentation remains fully available

#### Scenario: Packaged documentation is requested with a repository registered

- **GIVEN** a repository is registered
- **WHEN** a caller requests packaged methodology documentation
- **THEN** the result is identical to the result returned with no repository registered
