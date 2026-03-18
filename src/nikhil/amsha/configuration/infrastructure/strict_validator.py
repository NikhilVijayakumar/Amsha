import logging
from typing import Type, Any, Dict, List
from pydantic import BaseModel, ValidationError

from amsha.configuration.exceptions.amsha_configuration_exception import AmshaConfigurationException

logger = logging.getLogger(__name__)

class StrictConfigValidator:
    """
    Validator that checks input data against a Pydantic model.
    Unlike RobustConfigValidator, this validator strictly enforces 
    that all required fields are present and valid. Any failure 
    will accumulate errors and raise an AmshaConfigurationException
    to terminate execution early and prevent silent crashes.
    """
    def __init__(self):
        self.audit_log: List[str] = []

    def validate_strictly(self, model_class: Type[BaseModel], input_data: Dict[str, Any], config_name: str = "Configuration") -> BaseModel:
        """
        Validates input_data against model_class.
        Raises AmshaConfigurationException if any validation fails.
        """
        if input_data is None:
             raise AmshaConfigurationException(f"{config_name} cannot be empty or None.")
             
        if not isinstance(input_data, dict):
             raise AmshaConfigurationException(f"Expected dictionary for {config_name}, got {type(input_data).__name__}.")

        try:
            # Pydantic will perform strict validation based on the model.
            # Missing fields configured with `Field(...)` will throw ValidationErrors.
            validated_model = model_class(**input_data)
            self.audit_log.append(f"[VALID] {config_name} passed strict validation.")
            return validated_model
            
        except ValidationError as e:
            # Extract detailed errors from Pydantic
            detailed_errors = []
            for err in e.errors():
                loc = ".".join([str(x) for x in err.get("loc", [])])
                msg = err.get("msg", "")
                detailed_errors.append(f"Field '{loc}': {msg}")
            
            error_msg = f"❌ Strict Validation Failed for {config_name}."
            logger.error(error_msg)
            
            # Immediately raise our custom exception with the accumulated details
            raise AmshaConfigurationException(error_msg, errors=detailed_errors) from e
