# LLM Factory: Architecture & Design

## 1. Architectural Overview

The `llm_factory` module implements the **Abstract Factory** pattern extended with **Strategy-based Configuration**. It abstracts the complexity of instantiating different LLM providers (OpenAI, Gemini, Local/LM Studio) behind a unified interface.

### Class Diagram

```mermaid
%%{init: {'theme': 'base'}}%%
classDiagram
    class LLMBuilder {
        -settings: LLMSettings
        +build(type: LLMType, key: str): Result
        +build_creative(): Result
        +build_evaluation(): Result
    }

    class LLMSettings {
        +llm: Dict[str, Config]
        +get_model_config(use_case, key): Config
        +get_parameters(use_case): Params
    }

    class LLMUtils {
        +disable_telemetry()
        +extract_model_name(str): str
    }

    class LLMType {
        <<enumeration>>
        CREATIVE
        EVALUATION
    }

    LLMBuilder --> LLMSettings : uses
    LLMBuilder --> LLMUtils : uses
    LLMBuilder ..> LLMType : depends on
```

## 2. Instantiation Flow

The sequence ensures privacy (disabling telemetry) before instantiating the heavy LLM object.

### Sequence Diagram

```mermaid
%%{init: {'theme': 'base'}}%%
sequenceDiagram
    autonumber
    participant Client
    participant Builder as LLMBuilder
    participant Utils as LLMUtils
    participant Settings as LLMSettings
    participant CrewLLM as CrewAI.LLM

    Client->>Builder: build_creative(model_key="gemini-pro")
    
    rect rgb(240, 240, 240)
        note right of Builder: Privacy Step
        Builder->>Utils: disable_telemetry()
        Utils-->>Builder: void
    end

    Builder->>Settings: get_model_config("creative", "gemini-pro")
    Settings-->>Builder: ModelConfig(api_key, base_url...)

    Builder->>Settings: get_parameters("creative")
    Settings-->>Builder: QueryParams(temp, tokens...)

    alt is_local_model (base_url != None)
        Builder->>CrewLLM: init(base_url, ...params)
    else is_cloud_model
        Builder->>CrewLLM: init(...params)
    end

    Builder-->>Client: LLMBuildResult
```

## 3. Design Patterns Implemented

| Pattern | Implementation | Benefit |
| :--- | :--- | :--- |
| **Simple Factory** | `LLMBuilder.build` | Centralizes object creation logic. |
| **Configuration Object** | `LLMSettings` | Decouples code from environment variables. |
| **Monkey Patching** | `LLMUtils` | Modifies external library behavior at runtime for privacy. |
