"""
CrewApplication Protocol interface.

Defines the high-level interface for crew application management that clients
depend on. This Protocol enables structural typing and duck typing for
different application implementations (File-based, DB-based, etc.).
"""

from typing import Protocol, Dict, Any, Optional, Union, runtime_checkable
from amsha.execution_runtime.domain.execution_handle import ExecutionHandle
from amsha.execution_runtime.domain.execution_mode import ExecutionMode


@runtime_checkable
class CrewApplication(Protocol):
    """
    High-level interface for crew application management.
    
    This Protocol defines the client-facing interface for crew applications,
    enabling different backend implementations (file-based, database-based)
    to be used interchangeably through structural typing.
    
    All implementations must provide these methods with compatible signatures
    and behavior to ensure Protocol compliance.
    """
    
    def run_crew(
        self, 
        crew_name: str, 
        inputs: Dict[str, Any], 
        mode: ExecutionMode = ExecutionMode.INTERACTIVE,
            output_json: Any = None
    ) -> Union[Any, ExecutionHandle]:
        """
        Execute a crew with given inputs.
        
        Args:
            crew_name: Name of the crew to execute
            inputs: Dictionary of input parameters for the crew
            mode: Execution mode (INTERACTIVE or BACKGROUND)
            output_json: Any
        Returns:
            For INTERACTIVE mode: The crew execution result
            For BACKGROUND mode: ExecutionHandle for monitoring
            
        Raises:
            CrewConfigurationException: If crew configuration is invalid
            CrewExecutionException: If crew execution fails
        """
        ...
    
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
        ...
    
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
        ...
    
    def get_last_output_file(self) -> Optional[str]:
        """
        Get the path to the last generated output file.
        
        Returns:
            Path to the last output file, or None if no file was generated
        """
        ...