# LLM Factory Module - Architecture & Design

## Overview
This document visualizes the architecture of the `llm_factory` module, which implements the Factory Pattern for multi-provider LLM instantiation with configuration-driven model selection.

---

## 1. Factory Pattern - Class Diagram

```mermaid
---
config:
  theme: base
---
classDiagram
    class LLMType {
        <<enumeration>>
        CREATIVE
        EVALUATION
    }
    
    class LLMSettings {
        +llm: Dict~str, LLMUseCaseConfig~
        +llm_parameters: Dict~str, LLMParameters~
        +get_model_config(use_case: str, model_key: Optional~str~) LLMModelConfig
        +get_parameters(use_case: str) LLMParameters
    }
    
    class LLMUseCaseConfig {
        +default: str
        +models: Dict~str, LLMModelConfig~
    }
    
    class LLMModelConfig {
        +model: str
        +api_key: str
        +api_version: str
        +base_url: Optional~str~
    }
    
    class LLMParameters {
        +temperature: float
        +top_p: float
        +max_completion_tokens: int
        +presence_penalty: float
        +frequency_penalty: float
        +stop: Optional~list~
    }
    
    class LLMBuilder {
        -settings: LLMSettings
        +__init__(settings: LLMSettings)
        +build(llm_type: LLMType, model_key: Optional~str~) LLMBuildResult
        +build_creative(model_key: Optional~str~) LLMBuildResult
        +build_evaluation(model_key: Optional~str~) LLMBuildResult
    }
    
    class LLMBuildResult {
        +llm: LLM
        +model_name: str
    }
    
    class LLMUtils {
        <<utility>>
        +noop(*args, **kwargs) void$
        +disable_telemetry() void$
        +extract_model_name(model_string: str) str$
    }
    
    LLMSettings "1" *-- "2..*" LLMUseCaseConfig : contains
    LLMUseCaseConfig "1" *-- "1..*" LLMModelConfig : defines
    LLMSettings "1" *-- "2..*" LLMParameters : configures
    
    LLMBuilder --> LLMSettings : uses
    LLMBuilder --> LLMType : accepts
    LLMBuilder ..> LLMUtils : delegates
    LLMBuilder --> LLMBuildResult : returns
```

**Caption:** Figure 1.1 - Factory pattern class hierarchy showing configuration-driven model selection. `LLMBuilder` uses `LLMSettings` to resolve the appropriate model configuration based on `LLMType`.

**Source:**
- [`llm_builder.py`](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/llm_factory/service/llm_builder.py)
- [`llm_settings.py`](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/llm_factory/settings/llm_settings.py)
- [`llm_type.py`](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/llm_factory/domain/llm_type.py)

---

## 2. LLM Instantiation Flow - Sequence Diagram

```mermaid
---
config:
  theme: base
---
sequenceDiagram
    autonumber
    participant Client
    participant Builder as LLMBuilder
    participant Settings as LLMSettings
    participant Utils as LLMUtils
    participant CrewAI as LLM (CrewAI)
    
    Client->>Builder: build_creative(model_key="gemini_pro")
    Builder->>Utils: disable_telemetry()
    Utils-->>Builder: telemetry disabled
    
    Builder->>Settings: get_model_config("creative", "gemini_pro")
    Settings-->>Builder: LLMModelConfig
    
    Builder->>Settings: get_parameters("creative")
    Settings-->>Builder: LLMParameters
    
    Builder->>Utils: extract_model_name("gemini/gemini-1.5-pro")
    Utils-->>Builder: "gemini-1.5-pro"
    
    alt base_url is None
        Builder->>CrewAI: LLM(api_key, model, params)
    else base_url exists
        Builder->>CrewAI: LLM(base_url, api_key, model, params)
    end
    
    CrewAI-->>Builder: llm_instance
    Builder-->>Client: LLMBuildResult(llm, model_name)
```

**Caption:** Figure 2.1 - Sequence diagram showing LLM instantiation flow with conditional path selection based on `base_url` presence (cloud vs. local providers).

**Source:** [`llm_builder.py:50-52`](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/llm_factory/service/llm_builder.py#L50-L52)

---

## 3. Configuration Resolution - Flowchart

```mermaid
---
config:
  theme: base
---
flowchart TD
    classDef decision fill:#ffe66d,stroke:#333,stroke-width:2px
    classDef process fill:#95e1d3,stroke:#333,stroke-width:2px
    classDef error fill:#ff6b6b,stroke:#333,stroke-width:2px
    
    Start([Client calls build]):::process
    Start --> GetUseCase[Get use_case config]:::process
    
    GetUseCase --> CheckUseCase{Use case exists?}:::decision
    CheckUseCase -->|No| ErrorUseCase[Raise ValueError]:::error
    CheckUseCase -->|Yes| SelectKey[Select model_key or default]:::process
    
    SelectKey --> GetModel[Get model config]:::process
    GetModel --> CheckModel{Model exists?}:::decision
    CheckModel -->|No| ErrorModel[Raise ValueError]:::error
    CheckModel -->|Yes| GetParams[Get parameters]:::process
    
    GetParams --> ExtractName[Extract clean model name]:::process
    ExtractName --> CheckBaseURL{base_url is None?}:::decision
    
    CheckBaseURL -->|Yes| BuildCloud[Build cloud LLM]:::process
    CheckBaseURL -->|No| BuildLocal[Build local LLM]:::process
    
    BuildCloud --> Return[Return LLMBuildResult]:::process
    BuildLocal --> Return
    Return --> End([End]):::process
```

**Caption:** Figure 3.1 - Configuration resolution flowchart showing validation steps and conditional instantiation paths. Error handling ensures invalid configurations are caught early.

**Source:** [`llm_builder.py:15-48`](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/llm_factory/service/llm_builder.py#L15-L48)

---

## 4. Dependency Injection Container - Component Diagram

```mermaid
---
config:
  theme: base
---
graph LR
    classDef container fill:#a8dadc,stroke:#333,stroke-width:2px
    classDef config fill:#f1faee,stroke:#333,stroke-width:2px
    classDef service fill:#e63946,stroke:#333,stroke-width:2px
    
    Container[LLMContainer]:::container
    YAMLConfig[YAML Config]:::config
    
    Settings[LLM Settings]:::service
    Builder[LLM Builder]:::service
    Utils[LLM Utils]:::service
    
    YAMLConfig -->|parse| Settings
    Container --> Settings
    Container --> Builder
    Builder --> Settings
    Builder --> Utils
```

**Caption:** Figure 4.1 - Dependency injection container managing LLM factory instantiation. YAML configuration drives model provider selection.

**Source:** [`llm_container.py`](file:///home/dell/PycharmProjects/Amsha/src/nikhil/amsha/llm_factory/dependency/llm_container.py)

---

## 5. Multi-Provider Support - Architecture Diagram

```mermaid
---
config:
  theme: base
---
graph TB
    classDef client fill:#4ecdc4,stroke:#333,stroke-width:2px
    classDef factory fill:#ff6b6b,stroke:#333,stroke-width:2px
    classDef provider fill:#ffe66d,stroke:#333,stroke-width:2px
    
    subgraph "Client Layer"
        CrewForge[Crew Forge]:::client
        OutputProcess[Output Process]:::client
    end
    
    subgraph "Factory Layer"
        LLMBuilder:::factory
    end
    
    subgraph "Provider Layer"
        OpenAI[OpenAI GPT-4]:::provider
        Gemini[Google Gemini]:::provider
        LMStudio[LM Studio<br/>base_url: localhost]:::provider
        Azure[Azure OpenAI]:::provider
    end
    
    CrewForge --> LLMBuilder
    OutputProcess --> LLMBuilder
    
    LLMBuilder -->|base_url=None| OpenAI
    LLMBuilder -->|base_url=None| Gemini
    LLMBuilder -->|base_url=custom| LMStudio
    LLMBuilder -->|base_url=None| Azure
```

**Caption:** Figure 5.1 - Multi-provider architecture showing how `LLMBuilder` abstracts different LLM providers. Local providers require explicit `base_url`, while cloud providers use defaults.

---

## 6. Performance Metrics

### Table 6.1: LLM Factory Module Metrics

| S.No | Metric | Value | Unit | Source |
|:----:|:-------|------:|:-----|:-------|
| 1 | Total Files | 14 | files | `find` command |
| 2 | Domain Models | 3 | classes | `domain/` |
| 3 | Service Classes | 1 | class | `service/llm_builder.py` |
| 4 | Configuration Classes | 4 | Pydantic models | `domain/state.py` |
| 5 | Supported Providers | 4+ | providers | OpenAI, Gemini, LM Studio, Azure |
| 6 | Use Cases | 2 | types | Creative, Evaluation |
| 7 | Utility Functions | 3 | functions | `utils/llm_utils.py` |

**Caption:** Table 6.1 - Code organization metrics for the `llm_factory` module showing lightweight implementation with high flexibility.

---

## 7. Configuration Schema Example

### Table 7.1: Example LLM Configuration

| S.No | Use Case | Model Key | Model String | Base URL | Temperature |
|:----:|:---------|:----------|:-------------|:---------|------------:|
| 1 | creative | gemini_pro | `gemini/gemini-1.5-pro` | None | 0.8 |
| 2 | creative | gpt4 | `open_ai/gpt-4o` | None | 0.9 |
| 3 | evaluation | gemini_flash | `gemini/gemini-1.5-flash` | None | 0.3 |
| 4 | creative | local_llama | `lm_studio/llama-3-8b` | `http://localhost:1234/v1` | 0.7 |

**Caption:** Table 7.1 - Example configuration showing multi-provider support with different use cases. Note the explicit `base_url` for local models.

---

## Summary

**Total Diagrams:** 5 (class, sequence, flowchart, component, architecture)  
**Total Tables:** 2 (metrics, configuration example)

All diagrams verified against source code. All component names match actual file paths.
