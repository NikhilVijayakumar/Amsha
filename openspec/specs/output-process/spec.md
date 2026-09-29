# Output Process

## Purpose

Normalises model output into artifacts a caller can consume directly, and
documents the boundary of what this capability currently does not provide. It
covers stripping decoration from structured output, deriving a safe output
location, and the current absence of output evaluation and output validation.

Knowledge concept: [`knowledge/features/output-process.md`](../../../knowledge/features/output-process.md)

## Requirements

### Requirement: Decoration is stripped from structured output

The cleaner MUST remove code fences and surrounding prose from model output so
that the structured content can be parsed by the caller. Output that carries
no decoration MUST pass through unchanged.

#### Scenario: Output is wrapped in code fences

- **WHEN** a caller cleans output whose structured content is wrapped in code fences
- **THEN** the fences are removed
- **AND** the structured content remains
- **AND** the result is parseable without further extraction

#### Scenario: Output has prose around the structured content

- **WHEN** a caller cleans output that contains explanatory prose surrounding structured content
- **THEN** the surrounding prose is removed
- **AND** only the structured content remains

#### Scenario: Output is already clean

- **WHEN** a caller cleans output that contains no decoration
- **THEN** the output is returned unchanged

#### Scenario: Output contains no structured content

- **WHEN** a caller cleans output from which no structured content can be extracted
- **THEN** the absence is reported
- **AND** no partial or invented content is returned

### Requirement: The output location is derived from the input and made unique

The cleaner MUST derive an output path from the input path when no explicit
destination is given, MUST create the output directory, and MUST NOT overwrite
an existing file. On collision it MUST choose a unique path instead.

#### Scenario: No destination is supplied

- **WHEN** a caller cleans a file without supplying an output location
- **THEN** the output path is derived from the input path
- **AND** the derived name reflects the cleaned content rather than the raw file

#### Scenario: Destination is supplied

- **WHEN** a caller cleans a file and supplies an output location
- **THEN** output is written to that location

#### Scenario: Output directory does not exist

- **WHEN** the derived or supplied output directory does not exist
- **THEN** it is created before writing

#### Scenario: The target file already exists

- **WHEN** the derived output path already contains a file
- **THEN** the existing file is not overwritten
- **AND** a unique path is chosen instead

#### Scenario: Two inputs clean to the same derived name

- **WHEN** two inputs are cleaned and their derived output paths collide
- **THEN** each result is written to a distinct path
- **AND** neither input's result is lost

### Requirement: Content can be cleaned without going through a file

The cleaner MUST expose a content-level entry point, so a caller holding a
string does not have to write it to disk in order to clean it.

#### Scenario: A string is cleaned directly

- **WHEN** a caller cleans a string it already holds
- **THEN** the cleaned content is returned
- **AND** no intermediate file is required for the cleaning step

#### Scenario: A file is cleaned

- **WHEN** a caller cleans a file
- **THEN** the cleaned result is written to a resolved output path
- **AND** the caller is told whether the operation succeeded

### Requirement: Output evaluation and output validation are not currently provided

This capability MUST NOT be relied upon to evaluate output quality or to
validate output against a schema. No output evaluation or output validation
capability is currently implemented, and a caller MUST be told so rather than
receiving an apparently successful but empty result.

#### Scenario: Caller requires output evaluation

- **WHEN** a caller requires output evaluation from this capability
- **THEN** the requirement is reported as unavailable
- **AND** no empty evaluation result is returned as though it succeeded

#### Scenario: Caller requires output validation

- **WHEN** a caller requires output validation from this capability
- **THEN** the requirement is reported as unavailable
- **AND** no passing validation result is returned as though it succeeded

#### Scenario: Capability is later implemented

- **WHEN** output evaluation or output validation is implemented
- **THEN** this requirement is modified rather than satisfied silently
- **AND** the new behaviour is specified before it is treated as available
