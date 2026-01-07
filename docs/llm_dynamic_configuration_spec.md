# Pravaha & Amsha: Dynamic LLM Configuration Specification

## 1. Overview
This document outlines the technical specification for enabling **Dynamic LLM Configuration** in the `Amsha` library and `Akashavani` application. The goal is to allow the Application layer (and UI) to pass explicit Model Configuration and LLM Parameters for a task, overriding the default file-based configuration.

## 2. Core Concept: `LLMConfigurationInput`

We introduce a uniform contract for passing LLM details through the stack.

### Domain Model
**Location**: `src/bavans/akashvani/bala/kadha/application/domain/common/llm_configuration_input.py`

```python
from pydantic import BaseModel
from typing import Optional
from amsha.llm_factory.domain.model.llm_model_config import LLMModelConfig
from amsha.llm_factory.domain.model.llm_parameters import LLMParameters

class LLMConfigurationInput(BaseModel):
    """
    Encapsulates specific LLM configuration to be used for a task, 
    bypassing default file-based lookups.
    """
    model_config: LLMModelConfig
    llm_parameters: LLMParameters
```

---

## 3. Amsha Library Implementation

The `Amsha` library must be updated to accept and prioritize these explicit configuration objects.

### 3.1 LLMBuilder
**File**: `amsha/llm_factory/service/llm_builder.py`

**Change**: Update `build` method to accept overrides.

```python
    def build(self, llm_type: LLMType, model_key: str = None, 
              model_config_override: Optional[LLMModelConfig] = None, 
              params_override: Optional[LLMParameters] = None) -> LLMBuildResult:
        
        # 1. Use overrides if provided
        if model_config_override and params_override:
            model_config = model_config_override
            params = params_override
        else:
            # 2. Fallback to settings (Old behavior)
            model_config = self.settings.get_model_config(llm_type.value, model_key)
            params = self.settings.get_parameters(llm_type.value)

        # ... (rest of the logic remains the same, using model_config and params)
```

### 3.2 SharedLLMInitializationService
**File**: `amsha/crew_forge/service/shared_llm_initialization_service.py`

**Change**: Update `initialize_llm` to accept explicit config objects.

```python
    @staticmethod
    def initialize_llm(llm_config_path: Optional[str] = None, 
                       llm_type: LLMType = None,
                       model_config: Optional[LLMModelConfig] = None,
                       llm_params: Optional[LLMParameters] = None) -> Tuple[Any, str]:
        
        # Logic Loop:
        # 1. If model_config and llm_params are present -> Use them (Mode A)
        # 2. If not, validate llm_config_path -> Load settings -> Proceed (Mode B)
        
        llm_container = LLMContainer()
        # If Mode A: Configure container/builder to use overrides
        llm_builder = llm_container.llm_builder()
        
        if llm_type == LLMType.CREATIVE:
            build_llm = llm_builder.build_creative(
                model_config_override=model_config, 
                params_override=llm_params
            )
        # ... logic for EVALUATION
```

### 3.3 AmshaCrewFileApplication & DBApplication
**File**: `amsha/crew_forge/orchestrator/file/amsha_crew_file_application.py`

**Change**: 
1. Update `__init__` to accept `llm_config_override` (dict or object).
2. Refactor `_initialize_llm` to resolve the config.

```python
    def _initialize_llm(self, llm_config_override: Optional[Dict] = None):
        if llm_config_override:
            # Parse dict to objects
            model_config = LLMModelConfig(**llm_config_override['model_config'])
            llm_params = LLMParameters(**llm_config_override['llm_parameters'])
            
            return SharedLLMInitializationService.initialize_llm(
                llm_type=self.llm_type,
                model_config=model_config,
                llm_params=llm_params
            )
        else:
            # Default behavior loading from YAML
             return SharedLLMInitializationService.initialize_llm(
                llm_config_path=self.config_paths['llm'],
                llm_type=self.llm_type
            )
```

---

## 4. Application Layer Implementation (Akashavani)

The application stack acts as the conduit for passing the `LLMConfigurationInput` from the API/UI down to `Amsha`.

### 4.1 BotManager
**File**: `src/bavans/akashvani/bala/kadha/application/manager/bot_manager.py`

Update `stream_run` to accept the new argument.

```python
    def stream_run(self, application_task: ApplicationType, inputs=None, 
                   llm_config: Optional[LLMConfigurationInput] = None):
        
        # ... validation ...
        
        return ApplicationManager.stream_run(application_task, inputs, llm_config)
```

### 4.2 ApplicationManager
**File**: `src/bavans/akashvani/bala/kadha/application/manager/application_manager.py`

Update signatures to propagate `llm_config`.

```python
    @staticmethod
    def stream_run(config_type: ApplicationType, inputs=None, 
                   llm_config: Optional[LLMConfigurationInput] = None):
        # ... switch case ...
        return ApplicationManager.generate_fantasy_application(inputs, llm_config)

    @staticmethod
    def generate_fantasy_application(inputs=None, llm_config=None):
        # ... configs ...
        # Explicitly pass llm_config (as dict if needed by Amsha, or object)
        app = GenerateFantasyApplication(
            config_paths=configs, 
            llm_type=LLMType.CREATIVE, 
            inputs=inputs,
            llm_config_override=llm_config.dict() if llm_config else None
        )
        return app.run()
```

### 4.3 Domain Applications
**File**: e.g., `GenerateFantasyApplication`

Update constructors to accept and pass the override.

```python
class GenerateFantasyApplication(AmshaCrewFileApplication):
    def __init__(self, config_paths, llm_type, inputs=None, llm_config_override=None):
        super().__init__(config_paths, llm_type, inputs, llm_config_override)
```

---

## 5. Verification
1. **Unit Tests (Amsha)**: Ensure `LLMBuilder` correctly prioritizes overrides.
2. **Integration (Akashavani)**: Verify `ApplicationManager` successfully passes the config down to the initialized `LLM` instance.
