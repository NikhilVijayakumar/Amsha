"""
CrewForge module for CrewAI orchestration.

This module provides Protocol-based interfaces for crew orchestration,
enabling flexible implementations and easy testing through structural typing.
The module follows Clean Architecture principles with clear separation
between interfaces and implementations.

## Migration Guide

### For New Projects
Use the Protocol-based implementations directly:

```python
from amsha.crew_forge import FileCrewApplication, DbCrewApplication
from amsha.crew_forge import create_file_crew_application, create_db_crew_application
from amsha.llm_factory.domain.model.llm_type import LLMType

# Using factory functions (recommended)
app = create_file_crew_application(config_paths, LLMType.CREATIVE)

# Or direct instantiation
app = FileCrewApplication(config_paths, LLMType.CREATIVE)
```

### For Existing Projects
Minimal changes required - only update imports:

```python
# OLD (still works for backward compatibility)
from amsha.crew_forge import AmshaCrewFileApplication, AmshaCrewDBApplication

# NEW (recommended)
from amsha.crew_forge import FileCrewApplication, DbCrewApplication
```

### Protocol-Based Extension
Create custom implementations by conforming to Protocol interfaces:

```python
from amsha.crew_forge import CrewApplication
from typing import Dict, Any, Union, Optional
from amsha.execution_runtime.domain.execution_mode import ExecutionMode

class MyCustomApplication:
    def run_crew(self, crew_name: str, inputs: Dict[str, Any], 
                mode: ExecutionMode = ExecutionMode.INTERACTIVE) -> Union[Any, ExecutionHandle]:
        # Your implementation
        pass
    
    def prepare_inputs_for(self, crew_name: str) -> Dict[str, Any]:
        # Your implementation
        pass
    
    # ... implement other Protocol methods
```
"""

from typing import Dict, Any
from amsha.llm_factory.domain.model.llm_type import LLMType

# Protocol interfaces - primary public API
from .protocols import (
    CrewApplication,
    CrewOrchestrator,
    CrewManager,
    InputPreparationService
)

# Protocol-based implementations (new architecture)
from .orchestrator.file.file_crew_application import FileCrewApplication
from .orchestrator.db.db_crew_application import DbCrewApplication

# Backward compatibility imports - existing concrete implementations
from .orchestrator.file.amsha_crew_file_application import AmshaCrewFileApplication
from .orchestrator.db.amsha_crew_db_application import AmshaCrewDBApplication

# Exception hierarchy
from .exceptions import (
    CrewForgeException,
    CrewConfigurationException,
    CrewExecutionException,
    CrewManagerException,
    InputPreparationException
)

# Factory functions for creating Protocol implementations
def create_file_crew_application(config_paths: Dict[str, str], llm_type: LLMType) -> FileCrewApplication:
    """
    Factory function for creating file-based crew applications.
    
    This function provides a convenient way to create FileCrewApplication instances
    with proper error handling and validation. It's the recommended way to create
    file-based crew applications.
    
    Args:
        config_paths: Dictionary containing paths to configuration files
                     Expected keys: "job", "app", "llm"
        llm_type: Type of LLM to initialize (CREATIVE or EVALUATION)
        
    Returns:
        Configured FileCrewApplication instance ready for use
        
    Raises:
        CrewConfigurationException: If configuration is invalid or files are missing
        
    Example:
        ```python
        from amsha.crew_forge import create_file_crew_application
        from amsha.llm_factory.domain.model.llm_type import LLMType
        
        config_paths = {
            "job": "path/to/job_config.yaml",
            "app": "path/to/app_config.yaml", 
            "llm": "path/to/llm_config.yaml"
        }
        
        app = create_file_crew_application(config_paths, LLMType.CREATIVE)
        result = app.run_crew("my_crew", {"input": "data"})
        ```
    """
    return FileCrewApplication(config_paths, llm_type)


def create_db_crew_application(config_paths: Dict[str, str], llm_type: LLMType) -> DbCrewApplication:
    """
    Factory function for creating database-based crew applications.
    
    This function provides a convenient way to create DbCrewApplication instances
    with proper error handling and validation. It's the recommended way to create
    database-based crew applications.
    
    Args:
        config_paths: Dictionary containing paths to configuration files
                     Expected keys: "job", "app", "llm"
        llm_type: Type of LLM to initialize (CREATIVE or EVALUATION)
        
    Returns:
        Configured DbCrewApplication instance ready for use
        
    Raises:
        CrewConfigurationException: If configuration is invalid or files are missing
        
    Example:
        ```python
        from amsha.crew_forge import create_db_crew_application
        from amsha.llm_factory.domain.model.llm_type import LLMType
        
        config_paths = {
            "job": "path/to/job_config.yaml",
            "app": "path/to/app_config.yaml",
            "llm": "path/to/llm_config.yaml"
        }
        
        app = create_db_crew_application(config_paths, LLMType.CREATIVE)
        result = app.run_crew("my_crew", {"input": "data"})
        ```
    """
    return DbCrewApplication(config_paths, llm_type)


def create_crew_application(backend: str, config_paths: Dict[str, str], llm_type: LLMType) -> CrewApplication:
    """
    Generic factory function for creating crew applications with different backends.
    
    This function provides a unified interface for creating crew applications
    regardless of the backend implementation. It returns instances that conform
    to the CrewApplication Protocol interface.
    
    Args:
        backend: Backend type ("file" or "db")
        config_paths: Dictionary containing paths to configuration files
                     Expected keys: "job", "app", "llm"
        llm_type: Type of LLM to initialize (CREATIVE or EVALUATION)
        
    Returns:
        CrewApplication Protocol-compliant instance
        
    Raises:
        ValueError: If backend type is not supported
        CrewConfigurationException: If configuration is invalid or files are missing
        
    Example:
        ```python
        from amsha.crew_forge import create_crew_application
        from amsha.llm_factory.domain.model.llm_type import LLMType
        
        # Create file-based application
        app = create_crew_application("file", config_paths, LLMType.CREATIVE)
        
        # Create database-based application  
        app = create_crew_application("db", config_paths, LLMType.EVALUATION)
        
        # Both return CrewApplication Protocol-compliant instances
        result = app.run_crew("my_crew", {"input": "data"})
        ```
    """
    if backend == "file":
        return create_file_crew_application(config_paths, llm_type)
    elif backend == "db":
        return create_db_crew_application(config_paths, llm_type)
    else:
        raise ValueError(f"Unsupported backend type: {backend}. Supported types: 'file', 'db'")


# Backward compatibility factory functions
def create_amsha_file_application(config_paths: Dict[str, str], llm_type: LLMType) -> AmshaCrewFileApplication:
    """
    Backward compatibility factory for creating legacy file-based applications.
    
    This function creates instances of the original AmshaCrewFileApplication class
    for backward compatibility with existing client code. New projects should use
    create_file_crew_application() instead.
    
    Args:
        config_paths: Dictionary containing paths to configuration files
        llm_type: Type of LLM to initialize
        
    Returns:
        AmshaCrewFileApplication instance
        
    Deprecated:
        Use create_file_crew_application() for new projects
    """
    return AmshaCrewFileApplication(config_paths, llm_type)


def create_amsha_db_application(config_paths: Dict[str, str], llm_type: LLMType) -> AmshaCrewDBApplication:
    """
    Backward compatibility factory for creating legacy database-based applications.
    
    This function creates instances of the original AmshaCrewDBApplication class
    for backward compatibility with existing client code. New projects should use
    create_db_crew_application() instead.
    
    Args:
        config_paths: Dictionary containing paths to configuration files
        llm_type: Type of LLM to initialize
        
    Returns:
        AmshaCrewDBApplication instance
        
    Deprecated:
        Use create_db_crew_application() for new projects
    """
    return AmshaCrewDBApplication(config_paths, llm_type)


__all__ = [
    # Protocol interfaces (primary API)
    'CrewApplication',
    'CrewOrchestrator',
    'CrewManager',
    'InputPreparationService',
    
    # Protocol-based implementations (new architecture)
    'FileCrewApplication',
    'DbCrewApplication',
    
    # Factory functions (recommended)
    'create_file_crew_application',
    'create_db_crew_application', 
    'create_crew_application',
    
    # Backward compatibility implementations
    'AmshaCrewFileApplication',
    'AmshaCrewDBApplication',
    
    # Backward compatibility factory functions
    'create_amsha_file_application',
    'create_amsha_db_application',
    
    # Exception hierarchy
    'CrewForgeException',
    'CrewConfigurationException',
    'CrewExecutionException',
    'CrewManagerException',
    'InputPreparationException'
]