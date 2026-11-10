## ADDED Requirements

### Requirement: Azure providers are unsupported

The factory SHALL reject an explicitly Azure-qualified model before constructing a provider, and SHALL NOT change global LiteLLM behavior for it. See [LLM Factory knowledge](../../../../../knowledge/features/llm-factory.md).

#### Scenario: Azure model is requested

- **GIVEN** a model identifier beginning with `azure/` or `azure_ai/`, regardless of case
- **WHEN** the factory builds the model
- **THEN** it reports an unsupported-provider error without creating an LLM client.

#### Scenario: Another model contains the word Azure

- **GIVEN** a model identifier that contains but is not qualified by an Azure provider prefix
- **WHEN** the factory builds the model
- **THEN** it uses the normal provider construction path.

### Requirement: Custom endpoints are not forced to stream

The factory SHALL not force streaming when a custom base URL is supplied, while preserving standard endpoint behavior. See [LLM Factory knowledge](../../../../../knowledge/features/llm-factory.md).

#### Scenario: Custom base URL

- **GIVEN** a supported model with a custom base URL
- **WHEN** the factory constructs its LLM client
- **THEN** the base URL is passed without forcing the stream option.

#### Scenario: Default endpoint

- **GIVEN** a supported model without a custom base URL
- **WHEN** the factory constructs its LLM client
- **THEN** streaming is requested.
