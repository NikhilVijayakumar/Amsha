# Crew Forge

## Purpose

Turns declarative crew definitions into runnable CrewAI crews and flows, and
executes them. This is the capability client applications build on: it covers
parsing crew definitions from their storage, assembling agents and tasks into
a crew, the file-backed orchestration base class, and the repository
boundaries through which a client supplies stored definitions.

Knowledge concept: [`knowledge/features/crew-forge.md`](../../../knowledge/features/crew-forge.md)

## Requirements

### Requirement: Crew definitions are assembled from separately stored agents and tasks

Crew construction MUST take agent definitions and task definitions from
supplied sources and combine them into a runnable crew, rather than requiring
a single pre-merged document.

#### Scenario: Definitions are supplied separately

- **WHEN** agent definitions and task definitions are supplied independently
- **THEN** a runnable crew is assembled from them
- **AND** each task is bound to its referenced agent

#### Scenario: A referenced definition is absent

- **WHEN** a task references an agent that the supplied sources do not contain
- **THEN** assembly fails
- **AND** the failure names the missing reference

### Requirement: Stored definitions are reached through injected repository contracts

Access to stored agent and task definitions MUST go through repository
contracts supplied at construction. This capability MUST NOT select a concrete
storage backend by inspecting a type at runtime, and MUST NOT construct a
storage adapter internally.

#### Scenario: Repositories are supplied at construction

- **WHEN** a builder service is constructed with repository dependencies
- **THEN** it uses those dependencies for all definition lookups
- **AND** it constructs no storage adapter of its own

#### Scenario: A different storage backend is introduced

- **WHEN** a client supplies an implementation backed by a different database
- **THEN** the builder uses it without modification
- **AND** no branch on storage technology is introduced

#### Scenario: Builder would construct its own adapter

- **WHEN** a builder service is about to instantiate a storage adapter
- **THEN** that construction does not occur
- **AND** the dependency is required to be supplied instead

### Requirement: Building a crew and running a crew are separate responsibilities

Crew construction and crew execution MUST be provided by separate components,
so that a caller MAY assemble a crew without executing it.

#### Scenario: Crew is assembled without execution

- **WHEN** a caller assembles a crew
- **THEN** no execution is started
- **AND** the assembled crew is returned for the caller to inspect or run

#### Scenario: Execution is requested

- **WHEN** a caller submits an assembled crew for execution
- **THEN** execution is performed by the execution component
- **AND** the assembly component is not responsible for running it

### Requirement: Domain failures are reported as component exceptions

Every domain failure in crew assembly MUST be raised as an exception from this
capability's own exception set, and MUST NOT be raised as a bare generic error
or a bare value error.

#### Scenario: A definition cannot be resolved

- **WHEN** assembly fails because a definition is missing or malformed
- **THEN** a component exception is raised
- **AND** it descends from the capability's common exception base

#### Scenario: A generic error would be raised

- **WHEN** a domain condition fails
- **THEN** no bare generic exception is used for it
- **AND** no bare value error is used for it

### Requirement: File-backed orchestration loads configuration at run time

The file-backed orchestration base class MUST load job, application, and LLM
configuration from the filesystem when it is constructed, and MUST select its
model by work purpose supplied as configuration.

#### Scenario: Application is constructed over configuration paths

- **WHEN** a client constructs a file-backed application over a set of configuration paths and a work purpose
- **THEN** the job, application, and LLM configuration are read from those paths
- **AND** the model is initialised for the supplied work purpose

#### Scenario: Work purpose is not supplied by the client

- **WHEN** a client constructs a file-backed application without naming a work purpose
- **THEN** the factory applies its documented default
- **AND** the application still initialises successfully

### Requirement: Structured output is post-processed for the caller

The file-backed orchestration base class MUST expose output post-processing
that removes surrounding decoration from structured output, so a caller does
not parse fences or prose itself.

#### Scenario: Decorated structured output is passed in

- **WHEN** a caller passes model output containing fences or surrounding prose around structured content
- **THEN** post-processing returns the structured content alone
- **AND** the caller receives content it can parse directly

#### Scenario: Output is already clean

- **WHEN** a caller passes output that contains no decoration
- **THEN** post-processing returns the content unchanged
