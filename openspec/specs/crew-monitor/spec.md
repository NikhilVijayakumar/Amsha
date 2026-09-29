# Crew Monitor

## Purpose

Observes crew executions that are already running: resource consumption,
event lifecycle, and how much each agent contributed to the result. This
capability covers what a monitor records, how it attaches to a running
execution, and how observations are turned into reports.

Knowledge concept: [`knowledge/features/crew-monitor.md`](../../../knowledge/features/crew-monitor.md)

## Requirements

### Requirement: Monitoring is attached to a running execution and stopped explicitly

Resource monitoring MUST be started before the work of interest and stopped
after it, so that samples describe a bounded window rather than the whole
process lifetime.

#### Scenario: Monitoring is started then stopped

- **WHEN** a caller starts monitoring, performs work, and stops monitoring
- **THEN** the recorded samples cover that interval
- **AND** samples from outside the interval are not included

#### Scenario: Metrics are read before monitoring is started

- **WHEN** a caller requests metrics before monitoring has been started
- **THEN** the result reports that no measurements exist
- **AND** no zero-valued metrics are presented as measurements

#### Scenario: Model usage is recorded against a named model

- **WHEN** a caller records usage for a named model
- **THEN** the usage is attributed to that model
- **AND** it is distinguishable from host resource metrics

### Requirement: Execution events are observed from the runtime event bus

The event listener MUST subscribe to the execution event bus to record
lifecycle events, and MUST derive an elapsed duration for the work it
observes.

#### Scenario: Listener is attached to an event bus

- **WHEN** a listener is attached to an execution event bus
- **THEN** it subscribes to the events it records
- **AND** it does not require the execution to be driven by this capability

#### Scenario: Execution completes

- **WHEN** a completion event is observed
- **THEN** the completion is recorded
- **AND** the elapsed duration for the observed work is derivable

#### Scenario: An event carries no usable timestamp

- **WHEN** an observed event does not carry enough information to compute a duration
- **THEN** no duration is reported for it
- **AND** the absence is not presented as a zero duration

### Requirement: Contribution is attributed to the agent that produced it

Contribution analysis MUST attribute output to the agent or step responsible
for it, so a caller can see which parts of a crew earned their cost.

#### Scenario: Analysis runs over a completed job

- **WHEN** contribution analysis is run over a completed job
- **THEN** output is attributed to the agents and steps that produced it
- **AND** the attribution is reported per agent

#### Scenario: A step produced no attributable output

- **WHEN** a step contributed nothing to the output
- **THEN** it appears with no contribution
- **AND** it is not silently omitted from the analysis

### Requirement: Reports are generated per job and combined on demand

Reporting MUST support generating a report for a single job and combining
generated reports, so contribution analysis can be re-run over existing
reports without regenerating them.

#### Scenario: A single job report is generated

- **WHEN** a report is generated for one job
- **THEN** a report for that job is produced
- **AND** other jobs' reports are unaffected

#### Scenario: Generated reports are combined

- **WHEN** a caller combines the reports that have been generated
- **THEN** a combined report is produced from them
- **AND** the individual reports remain available

#### Scenario: Contribution analysis is re-run over existing reports

- **WHEN** contribution analysis is run again for a job whose report already exists
- **THEN** report generation is not required again
- **AND** analysis reads the existing report

### Requirement: Monitoring configuration is supplied, not discovered

Monitoring components MUST take their configuration from a caller-supplied
configuration path, so that what is monitored is declared rather than inferred
from the environment.

#### Scenario: Configuration path is supplied

- **WHEN** a monitoring component is constructed with a configuration path
- **THEN** it uses that configuration
- **AND** it does not fall back to an environment-derived default

#### Scenario: Configuration path is absent

- **WHEN** a monitoring component is required but no configuration is available
- **THEN** it reports that configuration is missing
- **AND** it does not proceed with an empty configuration
