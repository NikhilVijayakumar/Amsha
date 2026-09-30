# Documentation Discovery

## MODIFIED Requirements

### Requirement: Source-only groups contribute nothing without a repository

The discovery tools MUST distinguish the knowledge planes rather than treating
all of them uniformly. Packaged groups — the prerequisite and implementation
methodology, and the Amsha product knowledge — MUST be served from the installed
package, with no target repository required. Repository-only groups — the target
repository's top-level Markdown, its `docs/feature/` pages, and the Amsha
`knowledge/` bundle when it is read from a checkout rather than packaged — MUST
contribute nothing when no repository is registered.

Discovery MUST NOT make a product-plane answer depend on a repository-plane read.
Where a packaged concept and a repository document both exist for the same
question, the packaged concept is the answer and the repository document may
supply additional detail.

#### Scenario: Packaged groups are always searchable

- **GIVEN** no target repository is registered
- **WHEN** a caller searches the documentation
- **THEN** methodology documents and product knowledge are searched
- **AND** the repository-only groups contribute no hits

#### Scenario: Product knowledge is discoverable under its own namespace

- **GIVEN** a search that matches both a product concept and a knowledge-bundle
  index
- **WHEN** the caller receives the hits
- **THEN** each hit identifies which plane it came from
- **AND** one group's file does not mask another group that shares a filename

### Requirement: A registered repository enriches rather than gates

When a target repository is registered, its documents may be preferred over, or
merged with, the corresponding packaged answer. A registered repository MUST NOT
be the reason a product question has no answer.

#### Scenario: Repository document preferred when present

- **GIVEN** a registered target repository containing a richer per-module page
- **WHEN** the caller asks about that module
- **THEN** the server returns the repository's page
- **AND** if the repository has no such page, the packaged concept is returned
  instead
