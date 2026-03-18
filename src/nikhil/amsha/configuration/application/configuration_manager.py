from pathlib import Path
from typing import Union, Dict, Any, Type, TypeVar
import json
import yaml

from pydantic import BaseModel
from amsha.configuration.infrastructure.strict_validator import StrictConfigValidator
from amsha.configuration.exceptions.amsha_configuration_exception import AmshaConfigurationException

T = TypeVar('T', bound=BaseModel)

class ConfigurationManager:
    """
    Manages loading and strict validation of Amsha Configurations.
    Requires configurations to be perfectly valid to proceed.
    """
    
    @staticmethod
    def load_from_dict(model_class: Type[T], data: Dict[str, Any], config_name: str = "Configuration") -> T:
        """
        Load configuration from a dictionary strictly.
        """
        validator = StrictConfigValidator()
        # This will raise an AmshaConfigurationException if it fails
        validated_model = validator.validate_strictly(model_class, data, config_name)
        
        # Optionally log auditor traces
        import logging
        logger = logging.getLogger(__name__)
        for log_entry in validator.audit_log:
             logger.debug(log_entry)
             
        return validated_model

    @staticmethod
    def load_from_json(model_class: Type[T], path: Union[str, Path], config_name: str = "Configuration") -> T:
        """Load configuration from a JSON file strictly."""
        path = Path(path)
        if not path.exists():
            raise AmshaConfigurationException(f"Configuration file not found: {path}")
            
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        return ConfigurationManager.load_from_dict(model_class, data, config_name)

    @staticmethod
    def load_from_yaml(model_class: Type[T], path: Union[str, Path], config_name: str = "Configuration") -> T:
        """Load configuration from a YAML file strictly."""
        path = Path(path)
        if not path.exists():
            raise AmshaConfigurationException(f"Configuration file not found: {path}")
            
        with open(path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            
        return ConfigurationManager.load_from_dict(model_class, data, config_name)
