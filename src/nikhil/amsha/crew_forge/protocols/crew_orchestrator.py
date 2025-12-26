"""
CrewOrchestrator Protocol interface.

Defines the interface for crew execution orchestration that handles
the coordination of crew building and execution with runtime management.
"""

from typing import Protocol, Dict, Any, Optional, Union
from amsha.execution_runtime.domain.execution_handle import ExecutionHandle
from amsha.execution_runtime.domain.execution_mode import ExecutionMode
from amsha.crew_monitor.service.crew_performance_monitor import CrewPerformanceMonitor


class CrewOrchestrator(Protocol):
    """
    Interface for crew execution orchestration.
    
    This Protocol defines the interface for orchestrating crew execution,
    including building crews, managing execution state, and monitoring
    performance. Implementations handle the coordination between crew
    managers, runtime engines, and state management.
    """
    
    def run_crew(
        self,
        crew_name: str,
        inputs: Dict[str, Any],
        filename_suffix: Optional[str] = None,
        mode: ExecutionMode = ExecutionMode.INTERACTIVE,
            output_json: Any = None
    ) -> Union[Any, ExecutionHandle]:
        """
        Execute a crew with the specified parameters.
        
        This method coordinates the complete crew execution lifecycle,
        including building the crew, managing execution state, and
        monitoring performance.
        
        Args:
            crew_name: Name of the crew to execute
            inputs: Dictionary of input parameters for the crew
            filename_suffix: Optional suffix for output filenames
            mode: Execution mode (INTERACTIVE or BACKGROUND)
             output_json: Any
        Returns:
            For INTERACTIVE mode: The crew execution result
            For BACKGROUND mode: ExecutionHandle for monitoring
            
        Raises:
            CrewExecutionException: If crew execution fails
            CrewManagerException: If crew building fails
        """
        ...
    
    def get_last_output_file(self) -> Optional[str]:
        """
        Get the last output file path.
        
        Returns:
            Path to the last generated output file, or None if no file exists
        """
        ...
    
    def get_last_performance_stats(self) -> Optional[CrewPerformanceMonitor]:
        """
        Get performance statistics from the last execution.
        
        Returns:
            CrewPerformanceMonitor instance with metrics from the last run,
            or None if no execution has occurred
        """
        ...