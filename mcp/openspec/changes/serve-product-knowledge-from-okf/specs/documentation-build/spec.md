# Documentation Build

## MODIFIED Requirements

### Requirement: The build materializes both shipped knowledge planes

The wheel MUST contain the methodology documents and the Amsha product
knowledge, materialized from the committed `mcp/knowledge/` tree at build time
rather than authored inside the package source. The build MUST declare an
explicit mapping from each shipped plane to its source directory, so that adding
a shipped plane is a declared act and not an accident of directory layout.

Packaged documents MUST be emitted without YAML frontmatter, because the server
returns their text to agents and the frontmatter is build metadata.

#### Scenario: Both planes are present in the built wheel

- **GIVEN** a built wheel
- **WHEN** its contents are inspected
- **THEN** it contains the prerequisite and implementation methodology documents
- **AND** it contains the product concept and procedure documents

#### Scenario: No frontmatter in the built wheel

- **GIVEN** a built wheel
- **WHEN** a packaged document is read from it
- **THEN** the document contains no frontmatter delimiter

#### Scenario: The build does not require the Amsha repository

- **GIVEN** only the `mcp/` directory
- **WHEN** the wheel is built
- **THEN** the build succeeds

### Requirement: The build reads machine-local configuration from the environment

The standalone build MUST read machine-local settings — at minimum the output
directory and the virtualenv directory — from environment variables, so that one
committed configuration file works on multiple machines. A committed
configuration file MUST NOT contain machine-specific absolute paths.

When a required machine-local setting is absent from both the environment and the
configuration file, the build MUST fail with a message naming the environment
variable that would supply it, rather than proceeding with a default that would
write to an unexpected location.

#### Scenario: Environment overrides the committed output directory

- **GIVEN** a committed build configuration with no output directory
- **WHEN** the build runs with an output directory set in the environment
- **THEN** the artifact is written to the directory named in the environment

#### Scenario: A required machine-local setting is missing

- **GIVEN** a build configuration that specifies no output directory
- **WHEN** the build runs with no output directory in the environment
- **THEN** the build stops
- **AND** the message names the environment variable that supplies it

#### Scenario: Committed configuration carries no machine-specific paths

- **GIVEN** the committed build configuration
- **WHEN** it is inspected
- **THEN** it contains no absolute path belonging to a particular machine
