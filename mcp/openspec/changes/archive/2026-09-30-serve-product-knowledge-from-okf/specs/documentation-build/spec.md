# Documentation Build

## MODIFIED Requirements

### Requirement: The build produces the product plane

Every packaging path MUST materialize every shipped knowledge plane from the
bundle before an artifact is produced. No shipped artifact may contain a plane
that diverges from the bundle, and no source checkout needs generated docs under
`src/` to answer queries.

The shipped planes are the crew-design methodology and the Amsha product
knowledge. The build MUST declare an explicit mapping from each shipped plane to
its source directory, so that adding a plane is a declared act rather than an
accident of directory layout. Packaged documents MUST be emitted without YAML
frontmatter, because the server returns their text to agents and the frontmatter
is build metadata.

Machine metadata the runtime needs MUST survive that stripping. Where a plane
depends on fields the frontmatter carried, the build MUST ship them as an
explicitly declared sidecar, because they may not be re-derivable from the
packaged body.

#### Scenario: Standalone build from a clean tree

- **GIVEN** a source tree with no generated docs under `src/`
- **WHEN** a standalone build runs
- **THEN** every shipped plane is materialized before packaging
- **AND** the resulting artifact contains all 34 methodology documents and all 10
  product documents

#### Scenario: Source checkout without packaged docs

- **GIVEN** a source checkout with no `src/amsha_mcp/docs/` tree
- **WHEN** the server answers a methodology query from source
- **THEN** it serves the authored methodology content with frontmatter removed
- **AND** no pre-generation step is required

#### Scenario: Build with a divergent product plane

- **GIVEN** a plane document that does not match the bundle
- **WHEN** a build runs
- **THEN** the build fails
- **AND** it reports which document diverged

#### Scenario: Packaged documents carry no frontmatter

- **GIVEN** a built artifact
- **WHEN** a packaged document is read from it
- **THEN** the document contains no frontmatter delimiter

#### Scenario: The build does not require the Amsha repository

- **GIVEN** only the `mcp/` directory
- **WHEN** the artifact is built
- **THEN** the build succeeds

## ADDED Requirements

### Requirement: The build reads machine-local configuration from the environment

The standalone build MUST read machine-local settings — at minimum the output
directory and the virtualenv directory — from environment variables, so that one
committed configuration file works on multiple machines. A committed
configuration file MUST NOT contain machine-specific absolute paths.

Settings MUST resolve in a defined order, most specific first: the environment,
then the current platform's block in the configuration, then the top-level
configuration.

When a required machine-local setting is absent from both the environment and the
configuration file, the build MUST fail and name the environment variable that
would supply it, rather than proceeding with a default that writes to an
unexpected location.

The environment variable name for a setting MUST be a stable public contract and
MUST NOT be derived mechanically from the configuration key, so that a setting
keeps a natural name when its configuration key is renamed.

#### Scenario: Environment overrides the committed output directory

- **GIVEN** a committed build configuration with no output directory
- **WHEN** the build runs with an output directory set in the environment
- **THEN** the artifact is written to the directory named in the environment

#### Scenario: Layers resolve most specific first

- **GIVEN** a setting present in all three layers
- **WHEN** the build resolves it
- **THEN** the environment value is used
- **AND** with no environment value, the platform block is used
- **AND** with neither, the top-level value is used

#### Scenario: A required machine-local setting is missing

- **GIVEN** a build configuration that specifies no output directory
- **WHEN** the build runs with no output directory in the environment
- **THEN** the build stops
- **AND** the message names the environment variable that supplies it

#### Scenario: Committed configuration carries no machine-specific paths

- **GIVEN** the committed build configuration
- **WHEN** it is inspected
- **THEN** it contains no absolute path belonging to a particular machine

#### Scenario: Every supported platform is selectable

- **WHEN** the build configuration is inspected
- **THEN** a configuration block exists for each supported operating system
