# Execution Runtime

## Purpose

Provides Amsha's concurrency boundary: a bounded worker pool that accepts
callables and returns a handle the caller can poll, await, or cancel. This
capability covers submission, handle semantics, and the execution modes that
decide how submitted work is scheduled.

Knowledge concept: [`knowledge/features/execution-runtime.md`](../../../knowledge/features/execution-runtime.md)

## Requirements

### Requirement: Submitted work is bounded by a configured worker pool

Submissions MUST be served by a worker pool whose size is configurable, and
the default size MUST be conservative. Work in Amsha is largely
input/output-bound around model calls, so an unbounded or large default would
raise memory pressure and rate-limit exposure without improving throughput.

#### Scenario: Engine is constructed without a size

- **WHEN** an execution engine is constructed without an explicit worker count
- **THEN** it runs with a conservative default worker count
- **AND** submissions beyond that count are queued rather than spawning further workers

#### Scenario: Engine is constructed with an explicit size

- **WHEN** an execution engine is constructed with an explicit worker count
- **THEN** it runs with exactly that many workers

#### Scenario: Engine is shut down

- **WHEN** the engine is shut down
- **THEN** its workers are released
- **AND** no further submission is accepted

### Requirement: Submission returns a handle describing the work

Every submission MUST return a handle exposing an identifier, the current
status, a blocking result accessor, and a cancellation request. The handle
MUST be satisfiable structurally so a client MAY substitute a distributed
implementation without inheriting from Amsha.

#### Scenario: Work is submitted

- **WHEN** a caller submits a callable to the engine
- **THEN** a handle is returned immediately, without waiting for the work to finish
- **AND** the handle exposes an identifier and the current status

#### Scenario: Result is awaited

- **WHEN** a caller reads the result from a handle and the work has not finished
- **THEN** the read blocks until the work completes or the supplied timeout elapses

#### Scenario: Client supplies its own handle implementation

- **WHEN** a caller relies on the handle contract without inheriting any Amsha type
- **THEN** the contract is satisfiable by the caller's own implementation

### Requirement: Status of a handle reflects the work it describes

A handle's status MUST report whether its work is pending, running, or has
terminated, and MUST reflect the outcome once the work has terminated.

#### Scenario: Work has not started

- **WHEN** a handle's status is read before its work begins
- **THEN** the status is pending

#### Scenario: Work is in progress

- **WHEN** a handle's status is read while its work is executing
- **THEN** the status is running

#### Scenario: Work has finished

- **WHEN** a handle's status is read after its work has terminated
- **THEN** the status reflects the outcome, successful or failed

### Requirement: Cancellation is a request whose outcome is reported

Cancellation MUST be expressed as a request that reports whether it was
accepted, and MUST NOT be reported as successful when the work has already
completed or cannot be interrupted.

#### Scenario: Pending work is cancelled

- **WHEN** a caller cancels a handle whose work has not started
- **THEN** cancellation is accepted
- **AND** the work does not run

#### Scenario: Cancellation is requested too late

- **WHEN** a caller cancels a handle whose work has already completed
- **THEN** cancellation reports that it was not accepted
- **AND** the completed result remains available

### Requirement: Execution mode decides how a submission is scheduled

A submission MUST accept an execution mode, and the mode MUST default to
background execution so a caller who does not choose is never blocked by
subsequent work.

#### Scenario: Mode is not specified

- **WHEN** a caller submits work without naming an execution mode
- **THEN** the submission is scheduled as background execution
- **AND** the caller regains control immediately

#### Scenario: Mode is specified

- **WHEN** a caller submits work naming an execution mode
- **THEN** the submission is scheduled according to that mode
