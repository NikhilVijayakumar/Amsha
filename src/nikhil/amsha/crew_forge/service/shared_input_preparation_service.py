"""
Shared input preparation logic for all application implementations.
"""
import json
from pathlib import Path
from typing import Dict, Any
from amsha.crew_forge.exceptions import (
    InputPreparationException,
    CrewConfigurationException,
    ErrorContext,
    ErrorMessageBuilder,
    wrap_external_exception
)


class SharedInputPreparationService:
    """Shared input preparation logic for all application implementations."""
    
    @staticmethod
    def prepare_inputs_for(crew_name: str, job_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare inputs for a crew from job configuration using single input format.
        
        Args:
            crew_name: Name of the crew to prepare inputs for
            job_config: Job configuration dictionary containing crew definitions
            
        Returns:
            Dictionary of prepared inputs for the crew
            
        Raises:
            CrewConfigurationException: If crew definition is not found
            InputPreparationException: If input preparation fails
        """
        context = ErrorContext("SharedInputPreparationService", "prepare_inputs_for")
        context.add_context("crew_name", crew_name)
        
        try:
            crew_def = job_config["crews"].get(crew_name)
            if not crew_def:
                raise CrewConfigurationException(
                    message=ErrorMessageBuilder.configuration_error(
                        crew_name, 
                        "crew definition not found in job configuration"
                    ),
                    crew_name=crew_name,
                    config_details="crew not found in 'crews' section"
                )
                
            inputs_def = crew_def.get("input", {})
            final_inputs = {}
            
            print(f"📦 [SharedInputPrep] Preparing inputs for '{crew_name}'...")
            
            # Loop through each placeholder and its defined value
            for placeholder, value_def in inputs_def.items():
                context.add_context("placeholder", placeholder)
                
                # Case 1: The value is a dictionary defining a file source
                if isinstance(value_def, dict) and value_def.get("source") == "file":
                    file_path = Path(value_def["path"])
                    file_format = value_def.get("format", "text")
                    context.add_context("file_path", str(file_path))
                    context.add_context("file_format", file_format)
                    
                    print(f"  -> Loading '{placeholder}' from file: {file_path}")
                    
                    try:
                        if not file_path.exists():
                            raise FileNotFoundError(f"Input file not found: {file_path}")
                        
                        if file_format == "json":
                            with open(file_path, 'r', encoding='utf-8') as f:
                                final_inputs = json.load(f)
                        else:  # Plain text
                            with open(file_path, 'r', encoding='utf-8') as f:
                                final_inputs = f.read()
                                
                    except (FileNotFoundError, json.JSONDecodeError, IOError) as e:
                        raise wrap_external_exception(
                            e, 
                            context, 
                            InputPreparationException
                        )
                
                # Case 2: The value is provided directly (e.g., a string)
                else:
                    print(f"  -> Loading '{placeholder}' directly from config.")
                    final_inputs = value_def
            
            print(f"  -> Final prepared inputs: {list(final_inputs.keys()) if isinstance(final_inputs, dict) else 'single value'}")
            return final_inputs
            
        except (CrewConfigurationException, InputPreparationException):
            # Re-raise crew_forge exceptions as-is
            raise
        except Exception as e:
            # Wrap any other unexpected exceptions
            raise wrap_external_exception(e, context, InputPreparationException)
    
    @staticmethod
    def prepare_multiple_inputs_for(crew_name: str, job_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare multiple inputs for a crew from job configuration using list input format.
        
        Args:
            crew_name: Name of the crew to prepare inputs for
            job_config: Job configuration dictionary containing crew definitions
            
        Returns:
            Dictionary of prepared inputs for the crew
            
        Raises:
            CrewConfigurationException: If crew definition is not found or invalid
            InputPreparationException: If input preparation fails
        """
        context = ErrorContext("SharedInputPreparationService", "prepare_multiple_inputs_for")
        context.add_context("crew_name", crew_name)
        
        try:
            crew_def = job_config["crews"].get(crew_name)
            if not crew_def:
                raise CrewConfigurationException(
                    message=ErrorMessageBuilder.configuration_error(
                        crew_name, 
                        "crew definition not found in job configuration"
                    ),
                    crew_name=crew_name,
                    config_details="crew not found in 'crews' section"
                )
                
            # Expect a list of inputs, defaulting to an empty list
            inputs_def = crew_def.get("input", [])
            final_inputs = {}
            
            print(f"📦 [SharedInputPrep] Preparing multiple inputs for '{crew_name}'...")
            
            # Loop through each input definition in the list
            for input_item in inputs_def:
                if not isinstance(input_item, dict) or "key_name" not in input_item:
                    raise CrewConfigurationException(
                        message=ErrorMessageBuilder.configuration_error(
                            crew_name,
                            "invalid input definition: missing 'key_name'"
                        ),
                        crew_name=crew_name,
                        config_details=f"input item must be dict with 'key_name': {input_item}"
                    )
                    
                key_name = input_item["key_name"]  # The key for the final dictionary
                context.add_context("key_name", key_name)
                
                # Case 1: The value is from a file source
                if input_item.get("source") == "file":
                    file_path = Path(input_item["path"])
                    file_format = input_item.get("format", "text")
                    context.add_context("file_path", str(file_path))
                    context.add_context("file_format", file_format)
                    
                    print(f"  -> Loading '{key_name}' from file: {file_path}")
                    
                    try:
                        if not file_path.exists():
                            raise FileNotFoundError(f"Input file not found: {file_path}")
                        
                        if file_format == "json":
                            with open(file_path, 'r', encoding='utf-8') as f:
                                final_inputs[key_name] = json.load(f)
                        else:  # Plain text
                            with open(file_path, 'r', encoding='utf-8') as f:
                                final_inputs[key_name] = f.read()
                                
                    except (FileNotFoundError, json.JSONDecodeError, IOError) as e:
                        raise wrap_external_exception(
                            e, 
                            context, 
                            InputPreparationException
                        )
                
                # Case 2: The value is provided directly in the config
                elif input_item.get("source") == "direct":
                    print(f"  -> Loading '{key_name}' directly from config.")
                    final_inputs[key_name] = input_item["value"]
                
                else:
                    raise CrewConfigurationException(
                        message=ErrorMessageBuilder.configuration_error(
                            crew_name,
                            f"invalid input source for '{key_name}': must be 'file' or 'direct'"
                        ),
                        crew_name=crew_name,
                        config_details=f"source must be 'file' or 'direct', got: {input_item.get('source')}"
                    )
            
            print(f"  -> Final prepared inputs: {list(final_inputs.keys())}")
            return final_inputs
            
        except (CrewConfigurationException, InputPreparationException):
            # Re-raise crew_forge exceptions as-is
            raise
        except Exception as e:
            # Wrap any other unexpected exceptions
            raise wrap_external_exception(e, context, InputPreparationException)