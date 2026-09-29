# Utils

## Purpose

Holds the small, dependency-light helpers Amsha uses to read and write the
file formats its configurations and outputs are expressed in. This capability
covers JSON reading and writing, YAML reading, and in-place text-encoding
conversion.

Knowledge concept: [`knowledge/features/utils.md`](../../../knowledge/features/utils.md)

## Requirements

### Requirement: JSON files are read and written by content, not by convention

JSON helpers MUST read a JSON document from a path and write a document to a
path, creating the parent directory when writing. Written documents MUST be
human-readable and MUST preserve non-ASCII characters rather than escaping
them.

#### Scenario: A document is written

- **WHEN** a caller writes a mapping or a list to a path
- **THEN** the document is written as valid JSON at that path
- **AND** its parent directory exists afterwards, having been created if needed
- **AND** non-ASCII characters are written as themselves rather than escape sequences

#### Scenario: A written path has no parent directory component

- **WHEN** a caller writes to a path that has no parent directory to create
- **THEN** the write succeeds

#### Scenario: Writing fails

- **WHEN** a write cannot be completed
- **THEN** the helper reports that the write failed
- **AND** it reports no success for that write

#### Scenario: A document is read

- **WHEN** a caller reads an existing JSON file
- **THEN** the parsed document is returned
- **AND** an object or array document is returned as its corresponding structure

### Requirement: Absent, invalid, and unrequested JSON reads are distinguishable outcomes

A JSON read MUST report distinctly when the file is missing, when the file is
not valid JSON, and when no path was supplied at all. A read MUST NOT return a
partially parsed document in any of these cases.

#### Scenario: No path is supplied

- **WHEN** a caller reads JSON without supplying a path
- **THEN** no read is attempted
- **AND** the absence is reported

#### Scenario: The file is missing

- **WHEN** a caller reads JSON from a path that does not exist
- **THEN** the result reports that the file was not found
- **AND** it is distinguishable from an invalid document

#### Scenario: The file is not valid JSON

- **WHEN** a caller reads JSON from a file that cannot be parsed
- **THEN** the result reports that the content is invalid
- **AND** no partially parsed content is returned

### Requirement: YAML is read through a safe loader

YAML configuration MUST be parsed with a safe loader, so that constructing a
configuration document cannot instantiate arbitrary Python objects.

#### Scenario: A YAML configuration is read

- **WHEN** a caller reads an existing YAML configuration file
- **THEN** the parsed document is returned as a mapping
- **AND** the document is parsed with a safe loader rather than a permissive one

#### Scenario: The configuration file is missing

- **WHEN** a caller reads YAML from a path that does not exist
- **THEN** the failure is reported as a configuration error naming that path
- **AND** the host process is not terminated

#### Scenario: The configuration file cannot be parsed

- **WHEN** a caller reads YAML from a file that is not valid YAML
- **THEN** the failure is reported as a configuration error naming that path
- **AND** the host process is not terminated

### Requirement: Text encoding conversion is in place and reversible-safe

Encoding conversion MUST rewrite the target file as UTF-8 in place, and MUST
write through a temporary file so that a failed conversion does not leave the
original corrupted.

#### Scenario: A file is converted

- **WHEN** a caller converts a file whose encoding is detected reliably
- **THEN** the file is rewritten in place as UTF-8
- **AND** its decoded content is preserved

#### Scenario: Encoding detection is not reliable

- **WHEN** a caller converts a file whose encoding cannot be detected with sufficient confidence
- **THEN** a documented fallback encoding is used
- **AND** the fallback is reported rather than applied silently

#### Scenario: Decoding fails for the detected encoding

- **WHEN** the detected encoding cannot decode the file
- **THEN** conversion proceeds with undecodable bytes replaced
- **AND** the fallback is reported

#### Scenario: Conversion fails

- **WHEN** a conversion cannot be completed
- **THEN** the failure is reported
- **AND** the original file is not left partially written
