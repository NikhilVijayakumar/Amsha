# LLM Factory

## Purpose

Builds configured language-model instances for any supported provider from a
single configuration, so that no module other than this one needs to know how
a provider is addressed. This capability covers the purpose profiles that
distinguish creative from evaluation work, the provider-independent build
contract, and the boundary that keeps provider specifics in adapters.

Knowledge concept: [`knowledge/features/llm-factory.md`](../../../knowledge/features/llm-factory.md)

## Requirements

### Requirement: Model instances are built from configuration, not constructed ad hoc

A caller MUST obtain a configured model by supplying configuration through
the factory. No module outside this capability may construct a provider client
directly, so that provider configuration stays in one place.

#### Scenario: Caller supplies configuration

- **WHEN** a caller supplies LLM configuration to the factory
- **THEN** a configured model instance is returned
- **AND** the caller did not construct a provider client itself

#### Scenario: Configuration is incomplete

- **WHEN** a caller supplies configuration that does not satisfy the LLM schema
- **THEN** the build fails
- **AND** the failure is reported rather than a partially configured model being returned

### Requirement: Work purpose is selected as configuration, not by branching in code

A caller MUST be able to select a work purpose — creative or evaluation — and
the factory MUST apply the corresponding configuration. Callers MUST NOT
branch on work purpose in orchestration code.

#### Scenario: Caller selects a work purpose

- **WHEN** a caller selects a work purpose when building a model
- **THEN** the returned model is configured for that purpose

#### Scenario: Caller does not select a work purpose

- **WHEN** a caller builds a model without selecting a work purpose
- **THEN** the build succeeds
- **AND** the factory applies the documented default

#### Scenario: Orchestration code varies behaviour by work purpose

- **WHEN** a client's orchestration code branches on work purpose
- **THEN** the branching is outside this capability
- **AND** the difference is expressed through configuration instead

### Requirement: Provider-specific behaviour is confined to adapters

Provider addressing, endpoint lifecycle, and capability differences MUST be
implemented in adapters, so adding a provider does not change the build
contract.

#### Scenario: A provider requires endpoint lifecycle management

- **WHEN** a provider needs its endpoint started or stopped around a build
- **THEN** that behaviour is implemented in an adapter
- **AND** the build contract is unchanged

#### Scenario: A new provider is added

- **WHEN** support for a new provider is added
- **THEN** a new adapter implements the existing contract
- **AND** the build logic is not branched on provider identity

### Requirement: Model capabilities are described by configuration, not discovered at build time

Capabilities of a model — such as whether it supports tool use or structured
output — MUST be described in configuration and surfaced to the caller, so
that a caller can adapt without probing the provider.

#### Scenario: Capabilities are supplied

- **WHEN** configuration describes a model's capabilities
- **THEN** those capabilities are returned alongside the built model
- **AND** the caller can branch on them without contacting the provider

#### Scenario: Capabilities are not supplied

- **WHEN** configuration omits capability information
- **THEN** the build still succeeds
- **AND** the caller is told capabilities are unspecified rather than being given a default guess

### Requirement: Deprecated construction paths remain callable for one minor version

Where a construction path has been superseded, the previous path MUST remain
callable for one minor version and MUST direct the caller to its replacement.
Removal MUST NOT occur before a major version.

#### Scenario: Caller uses a deprecated construction path

- **WHEN** a caller uses a construction path that has been superseded
- **THEN** the call still succeeds
- **AND** the caller is directed to the replacement

#### Scenario: Deprecation window has not yet closed

- **WHEN** a minor version has not yet passed since the deprecation
- **THEN** the deprecated path remains available
- **AND** it is not removed in the same minor version that deprecated it
