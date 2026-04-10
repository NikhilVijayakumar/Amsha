# Dynamic LLM Configuration Guide

## Overview
Dynamic LLM Configuration allows applications to override the default file-based LLM settings at runtime. This is useful when the LLM model or parameters need to be determined dynamically by the application logic or user input (e.g., via a UI), rather than being hardcoded in YAML files.

## Usage

The `AmshaCrewDbApplication` and `AmshaCrewFileApplication` classes now accept an optional `llm_config_override` argument in their constructors.

### Dictionary Structure
The `llm_config_override` dictionary supports two top-level keys:
- `model_config`: Overrides model connection details.
- `llm_parameters`: Overrides generation parameters.

```python
llm_config_override = {
    "model_config": {
        "model": "gpt-4-turbo",       # Model name
        "api_key": "sk-...",          # Optional: API Key
        "base_url": "...",            # Optional: Base URL
        "api_version": "..."          # Optional: API Version
    },
    "llm_parameters": {
        "temperature": 0.7,
        "max_completion_tokens": 4096,
        "top_p": 1.0,
        "frequency_penalty": 0.0,
        "presence_penalty": 0.0,
        "stop": ["STOP"]
    }
}
```

### Example Usage

```python
from amsha.crew_forge.orchestrator.file.amsha_crew_file_application import AmshaCrewFileApplication
from amsha.llm_factory.domain.model.llm_type import LLMType

# ... define config_paths ...

app = AmshaCrewFileApplication(
    config_paths=config_paths,
    llm_type=LLMType.CREATIVE,
    llm_config_override={
        "model_config": {"model": "gpt-4-custom"},
        "llm_parameters": {"temperature": 0.2}
    }
)
```

## Migration Guide for Downstream Libraries

If you have created a custom application class that extends `AmshaCrewDbApplication` or `AmshaCrewFileApplication` (formerly `DbCrewApplication` / `FileCrewApplication`), you need to update your class to propagate the `llm_config_override` argument.

### Before
```python
class MyCustomApp(AmshaCrewDbApplication):
    def __init__(self, config_paths, llm_type, inputs=None):
        # ... custom logic ...
        super().__init__(config_paths, llm_type)
```

### After
Update your `__init__` method to accept `llm_config_override` (and potentially other args like `runtime` or `state_manager` if you use them) and pass it to the super constructor.

```python
from typing import Optional, Dict

class MyCustomApp(AmshaCrewDbApplication):
    def __init__(self, config_paths, llm_type, inputs=None, 
                 llm_config_override: Optional[Dict] = None):
        
        # ... custom logic ...
        
        super().__init__(
            config_paths=config_paths, 
            llm_type=llm_type,
            llm_config_override=llm_config_override
        )
```

### Important Note on Compatibility
The `Amsha` library maintains backward compatibility. If `llm_config_override` is not provided (or is `None`), the application will continue to load configuration from the `llm` YAML file specified in `config_paths`, just as before.
