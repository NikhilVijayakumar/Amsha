# Execution State

## Purpose

Models the lifecycle of a single Amsha execution and persists it through an
injected repository, so that any component can read what a run is currently
doing without holding a reference to the orchestrator. This capability covers
the status set, the state aggregate, and the repository boundary that makes
the backing store swappable.

Knowledge concept: [`knowledge/features/execution-state.md`](../../../knowledge/features/execution-state.md)

## Requirements

### Requirement: Execution status is drawn from a fixed set of states

An execution's status MUST be one of pending, running, completed, failed,
cancelled, or paused. No other status may be represented, because downstream
consumers switch on these values.

#### Scenario: A new execution is created

- **WHEN** an execution is created with no prior status supplied
- **THEN** its status is pending

#### Scenario: Status is reported during a run

- **WHEN** a caller reads the status of an execution
- **THEN** the value is one of pending, running, completed, failed, cancelled, or paused
- **AND** the value is directly serialisable without a custom encoder

#### Scenario: An unknown status value is supplied

- **WHEN** a status outside the fixed set is supplied
- **THEN** it is rejected
- **AND** the rejection is explicit rather than silently coerced

### Requirement: State carries outputs and metadata alongside its status

An execution's state MUST support recording a status together with optional
metadata, storing named outputs, and accumulating metadata entries. Storing an
output and changing status are distinct operations, so a caller MAY record
progress without overwriting results.

#### Scenario: Status is updated with metadata

- **WHEN** a caller updates an execution's status and supplies metadata
- **THEN** the status reflects the new value
- **AND** the supplied metadata is recorded with the update

#### Scenario: Output is recorded

- **WHEN** a caller stores an output under a name
- **THEN** the output is retrievable under that name
- **AND** the status is unchanged by the operation

#### Scenario: Metadata accumulates

- **WHEN** a caller records metadata more than once
- **THEN** the recorded entries are all retained

### Requirement: State is persisted through an injected repository

State persistence MUST go through a repository supplied to the state manager
at construction. The repository contract MUST be satisfiable structurally, so
a client can supply a database-backed implementation without inheriting from
Amsha.

#### Scenario: Manager is constructed with a repository

- **WHEN** a state manager is constructed with a repository
- **THEN** saves and reads are delegated to that repository
- **AND** the manager holds no store of its own

#### Scenario: Client supplies an implementation that does not inherit from Amsha

- **WHEN** a client supplies a repository that structurally satisfies the contract without inheriting any Amsha type
- **THEN** the manager accepts and uses it

#### Scenario: State is read for an unknown execution

- **WHEN** a caller requests an execution that was never created
- **THEN** the read reports that no such execution exists
- **AND** it does not return a default state

### Requirement: The manager can create, update, and checkpoint an execution

The state manager MUST be able to create a new execution, retrieve it by
identifier, update its status, and attach a checkpoint reference.

#### Scenario: Execution is created and retrieved

- **WHEN** a caller creates an execution and then retrieves it by the returned identifier
- **THEN** the retrieved execution is the one that was created
- **AND** its inputs are the inputs supplied at creation

#### Scenario: Checkpoint is attached

- **WHEN** a caller attaches a checkpoint reference to an execution
- **THEN** the reference is retained on that execution's state

#### Scenario: Status update targets an unknown execution

- **WHEN** a caller updates the status of an execution that does not exist
- **THEN** the update reports that no such execution exists
- **AND** no state is created as a side effect
