"""
InputPreparationService Protocol interface.

Defines the interface for preparing crew inputs from various sources
including files, direct values, and configuration-based resolution.
"""

from typing import Protocol, Dict, Any


class InputPreparationService(Protocol):
    """
    Interface for preparing crew inputs from various sources.
    
    This Protocol defines the interface for services that handle input
    preparation and resolution from different sources (files, direct values,
    configuration mappings). Implementations provide consistent input
    processing across different crew application types.
    """
    
    def prepare_inputs_for(self, crew_name: str, job_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare inputs for a crew from job configuration.
        
        This method resolves input values from various sources as defined
        in the job configuration, handling file loading, direct values,
        and other input resolution patterns.
        
        Args:
            crew_name: Name of the crew to prepare inputs for
            job_config: Job configuration containing input definitions
            
        Returns:
            Dictionary of resolved input parameters ready for crew execution
            
        Raises:
            InputPreparationException: If input preparation fails
            FileNotFoundError: If referenced input files don't exist
        """
        ...
    
    def prepare_multiple_inputs_for(self, crew_name: str, job_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare multiple inputs for a crew from job configuration.
        
        This method handles more complex input preparation scenarios where
        multiple input sources need to be resolved and combined into a
        single input dictionary for crew execution.
        
        Args:
            crew_name: Name of the crew to prepare inputs for
            job_config: Job configuration containing multiple input definitions
            
        Returns:
            Dictionary of resolved input parameters with multiple sources combined
            
        Raises:
            InputPreparationException: If input preparation fails
            FileNotFoundError: If referenced input files don't exist
        """
        ...