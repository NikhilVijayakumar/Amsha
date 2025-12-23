"""
File-based implementation of CrewApplication Protocol.

This module provides a Protocol-compliant application class for file-based
crew execution that uses shared services and utilities for common functionality.
"""
from typing import Dict, Any, Optional, Union
from pathlib import Path

from amsha.crew_forge.protocols.crew_application import CrewApplication
from amsha.crew_forge.orchestrator.file.atomic_crew_file_manager import AtomicCrewFileManager
from amsha.crew_forge.orchestrator.file.file_crew_orchestrator import FileCrewOrchestrator
from amsha.crew_forge.service.shared_input_preparation_service import SharedInputPreparationService
from amsha.crew_forge.service.shared_llm_initialization_service import SharedLLMInitializationService
from amsha.crew_forge.service.shared_json_file_service import SharedJSONFileService
from amsha.execution_runtime.domain.execution_handle import ExecutionHandle
from amsha.execution_runtime.domain.execution_mode import ExecutionMode
from amsha.execution_runtime.service.runtime_engine import RuntimeEngine
from amsha.execution_state.service.state_manager import StateManager
from amsha.llm_factory.domain.model.llm_type import LLMType
from amsha.utils.yaml_utils import YamlUtils
from amsha.crew_forge.exceptions import (
    CrewConfigurationException,
    ErrorContext,
    ErrorMessageBuilder,
    wrap_external_exception
)


class FileCrewApplication(CrewApplication):
    """
    File-based implementation of CrewApplication Protocol.
    
    This class provides a complete crew application implementation that uses
    file-based configuration and shared services for common functionality.
    It maintains backward compatibility with existing initialization patterns
    while conforming to the CrewApplication Protocol interface.
    """
    
    def __init__(
        self, 
        config_paths: Dict[str, str], 
        llm_type: LLMType,
        runtime: Optional[RuntimeEngine] = None,
        state_manager: Optional[StateManager] = None
    ):
        """
        Initialize the file-based crew application.
        
        Args:
            config_paths: Dictionary containing paths to configuration files
                         Expected keys: "job", "app", "llm"
            llm_type: Type of LLM to initialize (CREATIVE or EVALUATION)
            
        Raises:
            CrewConfigurationException: If configuration loading or LLM initialization fails
        """
        print("🚀 [FileCrewApp] Initializing file-based crew application...")
        
        context = ErrorContext("FileCrewApplication", "__init__")
        context.add_context("llm_type", llm_type.value)
        context.add_context("config_paths", str(config_paths))
        
        try:
            self.llm_type = llm_type
            self.config_paths = config_paths
            
            # Validate required configuration paths
            required_keys = ["job", "app", "llm"]
            missing_keys = [key for key in required_keys if key not in config_paths]
            if missing_keys:
                raise CrewConfigurationException(
                    message=ErrorMessageBuilder.configuration_error(
                        "FileCrewApplication",
                        f"missing required configuration paths: {missing_keys}"
                    ),
                    config_details=f"Required keys: {required_keys}, provided: {list(config_paths.keys())}"
                )
            
            # Load job configuration
            self.job_config = YamlUtils.yaml_safe_load(config_paths["job"])
            
            # Initialize LLM using shared service
            llm, model_name = SharedLLMInitializationService.initialize_llm(
                config_paths["llm"], 
                llm_type
            )
            
            # Create manager using the initialized LLM
            manager = AtomicCrewFileManager(
                llm=llm,
                model_name=model_name,
                app_config_path=config_paths["app"],
                job_config=self.job_config
            )
            
            # Create orchestrator with the manager and injected dependencies
            self.orchestrator = FileCrewOrchestrator(
                manager=manager,
                runtime=runtime,
                state_manager=state_manager
            )
            
            # Initialize shared services
            self._input_service = SharedInputPreparationService()
            self._json_service = SharedJSONFileService()
            
            print("✅ [FileCrewApp] File-based crew application initialized successfully")
            
        except (CrewConfigurationException,):
            # Re-raise crew_forge exceptions as-is
            raise
        except Exception as e:
            # Wrap any other unexpected exceptions
            raise wrap_external_exception(e, context, CrewConfigurationException)
    
    def run_crew(
        self, 
        crew_name: str, 
        inputs: Dict[str, Any], 
        mode: ExecutionMode = ExecutionMode.INTERACTIVE
    ) -> Union[Any, ExecutionHandle]:
        """
        Execute a crew with given inputs.
        
        Args:
            crew_name: Name of the crew to execute
            inputs: Dictionary of input parameters for the crew
            mode: Execution mode (INTERACTIVE or BACKGROUND)
            
        Returns:
            For INTERACTIVE mode: The crew execution result
            For BACKGROUND mode: ExecutionHandle for monitoring
            
        Raises:
            CrewConfigurationException: If crew configuration is invalid
            CrewExecutionException: If crew execution fails
        """
        print(f"🎯 [FileCrewApp] Running crew '{crew_name}' in {mode.value} mode...")
        return self.orchestrator.run_crew(crew_name, inputs, mode=mode)
    
    def prepare_inputs_for(self, crew_name: str) -> Dict[str, Any]:
        """
        Prepare inputs for a specific crew from configuration.
        
        This method resolves input values from various sources (files, direct values)
        as defined in the crew configuration, returning a dictionary ready for
        crew execution.
        
        Args:
            crew_name: Name of the crew to prepare inputs for
            
        Returns:
            Dictionary of resolved input parameters
            
        Raises:
            InputPreparationException: If input preparation fails
            CrewConfigurationException: If crew configuration is invalid
        """
        print(f"📦 [FileCrewApp] Preparing inputs for crew '{crew_name}'...")
        
        # Try multiple inputs format first, fall back to single input format
        try:
            return self._input_service.prepare_multiple_inputs_for(crew_name, self.job_config)
        except (CrewConfigurationException, KeyError):
            # Fall back to single input format for backward compatibility
            return self._input_service.prepare_inputs_for(crew_name, self.job_config)
    
    def clean_json(self, output_filename: str, max_retries: int = 2) -> bool:
        """
        Clean and validate JSON output files.
        
        This method processes JSON output files to ensure they are valid
        and properly formatted, using LLM-based correction if needed.
        
        Args:
            output_filename: Path to the JSON file to clean
            max_retries: Maximum number of LLM correction attempts
            
        Returns:
            True if cleaning was successful, False otherwise
            
        Raises:
            FileNotFoundError: If the output file doesn't exist
        """
        print(f"🧹 [FileCrewApp] Cleaning JSON file: {output_filename}")
        return self._json_service.clean_json(output_filename, max_retries)
    
    def get_last_output_file(self) -> Optional[str]:
        """
        Get the path to the last generated output file.
        
        Returns:
            Path to the last output file, or None if no file was generated
        """
        return self.orchestrator.get_last_output_file()
    
    # Backward compatibility methods
    def _prepare_inputs_for(self, crew_name: str) -> Dict[str, Any]:
        """
        Backward compatibility method for single input format.
        
        This method is kept for compatibility with existing client code
        that may call this private method directly.
        """
        return self._input_service.prepare_inputs_for(crew_name, self.job_config)
    
    def _prepare_multiple_inputs_for(self, crew_name: str) -> Dict[str, Any]:
        """
        Backward compatibility method for multiple inputs format.
        
        This method is kept for compatibility with existing client code
        that may call this private method directly.
        """
        return self._input_service.prepare_multiple_inputs_for(crew_name, self.job_config)
    
    @staticmethod
    def clean_json_metrics(output_filename: str) -> tuple[bool, Optional[str]]:
        """
        Backward compatibility method for cleaning JSON with metrics.
        
        This static method is kept for compatibility with existing client code.
        
        Args:
            output_filename: Path to the JSON file to clean
            
        Returns:
            Tuple of (success_flag, cleaned_file_path)
        """
        service = SharedJSONFileService()
        success = service.clean_json(output_filename)
        if success:
            # Return the cleaned file path (typically same as input for in-place cleaning)
            return True, output_filename
        return False, None