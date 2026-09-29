# Common

## Purpose

Provides the structured logging and metrics instrumentation that every Amsha
module uses, built on the standard library so it adds no runtime dependency.
This is an internal capability, not served to clients as a documentation
module. It covers record formatting, logger provisioning, execution tracing,
and the reset hook that makes logging state testable.

Knowledge concept: [`knowledge/features/common.md`](../../../knowledge/features/common.md)

## Requirements

### Requirement: Log records carry structured fields, not concatenated strings

The formatter MUST append fields supplied alongside a log record to the
rendered message as named key-value pairs. A caller MUST be able to attach
identifiers and measurements to a log event without pre-formatting them into
the message text.

#### Scenario: A record carries extra fields

- **WHEN** a caller logs with additional fields attached to the record
- **THEN** the rendered output contains the base message
- **AND** it contains each supplied field rendered as a named key-value pair

#### Scenario: A record carries no extra fields

- **WHEN** a caller logs with no additional fields
- **THEN** the rendered output contains the base message alone
- **AND** no empty field section is appended

#### Scenario: Fields are rendered deterministically

- **WHEN** the same record is formatted more than once
- **THEN** the fields appear in a stable order
- **AND** the output is comparable across runs

### Requirement: Logger provisioning is idempotent within a process

Requesting a logger MUST configure the logging tree at most once per process,
and MUST return the same logger for repeated requests with the same module
name. Repeated provisioning MUST NOT accumulate duplicate output handlers.

#### Scenario: Logger is requested repeatedly

- **WHEN** a caller requests a logger for the same module name more than once
- **THEN** the same logger is returned each time
- **AND** output is not duplicated by an added handler

#### Scenario: A module logger is requested for the first time

- **WHEN** a caller requests a logger for a module name not requested before
- **THEN** a logger scoped to that module is returned

#### Scenario: No module name is supplied

- **WHEN** a caller requests a logger without a module name
- **THEN** a root-scoped logger is returned

### Requirement: Execution tracing reports entry, duration, and outcome

The execution decorator MUST record when an operation starts, how long it
took, and whether it succeeded or failed, WITHOUT the caller adding that
instrumentation by hand. A failing operation MUST re-raise so tracing never
swallows an error.

#### Scenario: A traced operation succeeds

- **WHEN** a decorated operation completes without raising
- **THEN** its entry and completion are recorded
- **AND** the recorded duration is the operation's elapsed time
- **AND** the return value is passed back to the caller unchanged

#### Scenario: A traced operation fails

- **WHEN** a decorated operation raises
- **THEN** its failure is recorded with the elapsed time and the error type
- **AND** the original exception is re-raised to the caller
- **AND** the exception is not swallowed by the decorator

#### Scenario: The decorated operation is inspected

- **WHEN** a caller inspects a decorated operation
- **THEN** it reports the original operation's identity rather than the wrapper's

### Requirement: Metrics are logged through named metric shapes

Metrics MUST be logged through dedicated metric shapes for execution
measurements, model configuration, and file operations, so that consumers can
read a consistent field set instead of free-form messages.

#### Scenario: Execution metrics are recorded

- **WHEN** a caller records metrics for a completed execution
- **THEN** the crew name, execution identifier, and elapsed time are recorded
- **AND** token and host resource measurements are recorded when present

#### Scenario: Model configuration is recorded

- **WHEN** a caller records an applied model configuration
- **THEN** the model name and the applied generation parameters are recorded
- **AND** the presence of a custom endpoint is recorded as a flag rather than its value

#### Scenario: File operation is recorded

- **WHEN** a caller records a file operation
- **THEN** the operation, the file path, and the outcome status are recorded

### Requirement: Logging state can be reset for testing

The capability MUST expose a reset that removes installed handlers and clears
cached module loggers, so that one test's logging configuration does not leak
into the next.

#### Scenario: Logger state is reset

- **WHEN** logging state is reset
- **THEN** previously installed handlers are removed
- **AND** cached module loggers are cleared
- **AND** a later request re-provisions logging as if the process were new

### Requirement: Logging configuration is externally overridable

Log level and log directory MUST be overridable from the environment, with a
documented default when unset, so operators can adjust diagnostics without
code changes.

#### Scenario: Log level is set in the environment

- **WHEN** a log level is supplied from the environment
- **THEN** that level is applied to the logging tree

#### Scenario: Log level is not set

- **WHEN** no log level is supplied from the environment
- **THEN** the documented default level is applied

#### Scenario: Log directory is set in the environment

- **WHEN** a log directory is supplied from the environment
- **THEN** log files are written under that directory
- **AND** the directory is created if it does not exist
