"""
File-based crew orchestrator implementation using BaseCrewOrchestrator.

This module provides a Protocol-compliant orchestrator for file-based
crew execution that leverages shared orchestration logic.
"""
from typing import Dict, Any, Optional, Union

from amsha.crew_forge.service.base_crew_orchestrator import BaseCrewOrchestrator
from amsha.crew_forge.protocols.crew_manager import CrewManager
from amsha.crew_monitor.service.crew_performance_monitor import CrewPerformanceMonitor
from amsha.execution_runtime.service.runtime_engine import RuntimeEngine
from amsha.execution_runtime.domain.execution_mode import ExecutionMode
from amsha.execution_runtime.domain.execution_handle import ExecutionHandle
from amsha.execution_state.service.state_manager import StateManager


class FileCrewOrchestrator(BaseCrewOrchestrator):
    """
    File-based crew orchestrator implementation.
    
    This class implements the CrewOrchestrator Protocol using the shared
    BaseCrewOrchestrator logic. It provides file-based crew execution
    with consistent execution state management and performance monitoring.
    """
    
    def __init__(
        self, 
        manager: CrewManager, 
        runtime: Optional[RuntimeEngine] = None,
        state_manager: Optional[StateManager] = None
    ):
        """
        Initialize the file-based orchestrator.
        
        Args:
            manager: CrewManager Protocol implementation for building crews
            runtime: Optional RuntimeEngine for execution management
            state_manager: Optional StateManager for execution state tracking
        """
        super().__init__(manager, runtime, state_manager)
    
    def run_crew(
        self,
        crew_name: str,
        inputs: Dict[str, Any],
        filename_suffix: Optional[str] = None,
        mode: ExecutionMode = ExecutionMode.INTERACTIVE
    ) -> Union[Any, ExecutionHandle]:
        """
        Execute a crew with the specified parameters.
        
        Uses the shared BaseCrewOrchestrator logic for consistent execution
        across all orchestrator implementations.
        
        Args:
            crew_name: Name of the crew to execute
            inputs: Dictionary of input parameters for the crew
            filename_suffix: Optional suffix for output filenames
            mode: Execution mode (INTERACTIVE or BACKGROUND)
            
        Returns:
            For INTERACTIVE mode: The crew execution result
            For BACKGROUND mode: ExecutionHandle for monitoring
            
        Raises:
            CrewExecutionException: If crew execution fails
            CrewManagerException: If crew building fails
        """
        return super().run_crew(crew_name, inputs, filename_suffix, mode)
    
    def get_last_output_file(self) -> Optional[str]:
        """
        Get the last output file path.
        
        Returns:
            Path to the last generated output file, or None if no file exists
        """
        return super().get_last_output_file()
    
    def get_last_performance_stats(self) -> Optional[CrewPerformanceMonitor]:
        """
        Get performance statistics from the last execution.
        
        Returns:
            CrewPerformanceMonitor instance with metrics from the last run,
            or None if no execution has occurred
        """
        return super().get_last_performance_stats()



