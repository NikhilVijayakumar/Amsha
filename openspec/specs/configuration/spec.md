# Configuration

## Purpose

Defines the declarative schema of an Amsha run — the application, job, and
LLM configurations that every other module reads instead of declaring its own
inputs. This capability covers what those schemas require, how they are
loaded from dict, JSON, and YAML, and how invalid configuration is reported.

Knowledge concept: [`knowledge/features/configuration.md`](../../../knowledge/features/configuration.md)

## Requirements

### Requirement: Application configuration declares its paths

Application configuration MUST require a domain root path and an output
directory path. Both identify filesystem locations the run depends on, so
neither may be defaulted; an application whose root path is unknown cannot
resolve its crew definitions.

#### Scenario: Valid application configuration loads

- **WHEN** application configuration supplies both a domain root path and an output directory path
- **THEN** the configuration is accepted
- **AND** both paths are available to the application that declared it

#### Scenario: Application configuration omits a required path

- **WHEN** application configuration omits the domain root path or the output directory path
- **THEN** validation fails
- **AND** the failure names the missing field

### Requirement: Job configuration pairs tasks with agents

Job configuration MUST express each crew as a list of steps, and every step
MUST name both a task reference and an agent reference. The pairing is what
makes a job executable without code, so a step missing either side cannot be
resolved to an actor.

#### Scenario: Well-formed job configuration loads

- **WHEN** job configuration supplies crew steps that each name a task key and an agent key
- **THEN** the configuration is accepted
- **AND** each step resolves to a task and an agent

#### Scenario: Step omits its task or agent

- **WHEN** a crew step omits the task key or the agent key
- **THEN** validation fails
- **AND** the failure identifies the incomplete step

#### Scenario: Optional job attributes are absent

- **WHEN** job configuration omits knowledge sources, crew input, or memory
- **THEN** the configuration is still accepted
- **AND** the absent attributes take their documented defaults

### Requirement: LLM configuration carries a model and its credentials by reference

LLM configuration MUST require a model identifier. Credentials MAY be supplied
directly or as the name of an environment variable, so a configuration file
can be shared without embedding a secret.

#### Scenario: Model identifier is supplied

- **WHEN** LLM configuration supplies a model identifier
- **THEN** the configuration is accepted
- **AND** the model identifier is available to the LLM factory

#### Scenario: Model identifier is absent

- **WHEN** LLM configuration omits the model identifier
- **THEN** validation fails
- **AND** the failure names the model identifier as the missing field

#### Scenario: Credential is referenced by environment variable

- **WHEN** LLM configuration supplies an environment variable name instead of a credential
- **THEN** the configuration is accepted
- **AND** no credential is stored in the configuration itself

### Requirement: Configuration loads from dict, JSON, and YAML

Configuration MUST be loadable from a mapping, a JSON file, and a YAML file
through one manager, and each load MUST validate against the target schema.

#### Scenario: Configuration is loaded from a YAML file

- **WHEN** a caller loads configuration from a YAML file for a given schema
- **THEN** the parsed document is validated against that schema
- **AND** a validated instance of the schema is returned

#### Scenario: Configuration is loaded from a mapping or a JSON file

- **WHEN** a caller loads configuration from a mapping or a JSON file
- **THEN** the same schema validation is applied as for a YAML file
- **AND** the same failure reporting is used

#### Scenario: Source file cannot be read

- **WHEN** a configuration source is missing or unreadable
- **THEN** the load fails
- **AND** the failure is reported as a configuration exception naming the source

### Requirement: Invalid configuration is reported as a configuration error

Every configuration failure MUST be reported as a component configuration
exception, and MUST identify the configuration being processed. A malformed
configuration MUST fail at load time rather than surfacing later as an
unrelated error during orchestration.

#### Scenario: Configuration violates its schema

- **WHEN** a configuration document does not satisfy the target schema
- **THEN** the load raises a configuration exception
- **AND** the exception names the configuration being processed

#### Scenario: Failure is raised at load time

- **WHEN** a configuration is structurally invalid
- **THEN** the failure is raised by the load call
- **AND** no partially validated configuration is returned
