# Documentation Discovery

## MODIFIED Requirements

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

## ADDED Requirements

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
