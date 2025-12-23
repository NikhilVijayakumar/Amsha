"""
CrewManager Protocol interface.

Defines the interface for crew building and configuration management.
This Protocol enables different crew manager implementations to be used
interchangeably through structural typing.
"""

from typing import Protocol, Optional, runtime_checkable
from crewai import Crew


@runtime_checkable
class CrewManager(Protocol):
    """
    Interface for crew building and configuration.
    
    This Protocol defines the interface for components responsible for
    building and configuring CrewAI crews from various sources (files,
    databases, etc.). Implementations handle the details of loading
    configurations and assembling crews.
    """
    
    def build_atomic_crew(
        self, 
        crew_name: str, 
        filename_suffix: Optional[str] = None
    ) -> Crew:
        """
        Build a configured crew ready for execution.
        
        This method creates a complete CrewAI Crew instance from the
        specified configuration, including all agents, tasks, and
        knowledge sources.
        
        Args:
            crew_name: Name of the crew configuration to build
            filename_suffix: Optional suffix for output filenames
            
        Returns:
            Configured CrewAI Crew instance ready for execution
            
        Raises:
            CrewManagerException: If crew building fails
            CrewConfigurationException: If crew configuration is invalid
        """
        ...
    
    @property
    def model_name(self) -> str:
        """
        Get the model name used by this manager.
        
        Returns:
            String identifier of the LLM model being used
        """
        ...
    
    @property
    def output_file(self) -> Optional[str]:
        """
        Get the current output file path.
        
        Returns:
            Path to the current output file, or None if no file is set
        """
        ...