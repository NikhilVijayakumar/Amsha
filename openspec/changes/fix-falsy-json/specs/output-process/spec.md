## ADDED Requirements

### Requirement: Valid JSON values retain their meaning

The cleaner MUST preserve valid falsy JSON values rather than reporting a parsing failure. See [Output Process knowledge](../../../../../knowledge/features/output-process.md).

#### Scenario: Falsy JSON values

- **GIVEN** a JSON input containing an empty object, empty array, false, zero or null
- **WHEN** the cleaner processes the input
- **THEN** it SHALL write the same JSON value and report success.

#### Scenario: Invalid JSON

- **GIVEN** input that cannot be parsed as JSON
- **WHEN** the cleaner processes the input
- **THEN** it SHALL report failure and not write a result.
