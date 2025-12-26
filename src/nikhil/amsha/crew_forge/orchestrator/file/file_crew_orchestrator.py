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
        mode: ExecutionMode = ExecutionMode.INTERACTIVE,
        max_retries: int = 0,
        output_validator: Optional[Union[callable, Any]] = None,
            output_json: Any = None
    ) -> Union[Any, ExecutionHandle]:
        """
        Execute a crew with the specified parameters, optionally retrying on validation failure.
        
        Uses the shared BaseCrewOrchestrator logic for consistent execution
        across all orchestrator implementations.
        
        Args:
            crew_name: Name of the crew to execute
            inputs: Dictionary of input parameters for the crew
            filename_suffix: Optional suffix for output filenames
            mode: Execution mode (INTERACTIVE or BACKGROUND)
            max_retries: Maximum number of retries if validation fails (default: 0)
            output_validator: Callable that takes a file path and returns bool (True=Success)
            output_json: Any
        Returns:
            For INTERACTIVE mode: The crew execution result
            For BACKGROUND mode: ExecutionHandle for monitoring
            
        Raises:
            CrewExecutionException: If crew execution fails
            CrewManagerException: If crew building fails
        """
        if mode == ExecutionMode.BACKGROUND and (max_retries > 0 or output_validator):
             # For now, we only support retries in INTERACTIVE mode because BACKGROUND 
             # requires more complex state management/callbacks.
             pass 

        attempt = 0
        success = False
        last_result = None
        
        # Determine effective loop count: 1 initial attempt + max_retries
        total_attempts = 1 + max_retries
        
        while attempt < total_attempts and not success:
            current_suffix = filename_suffix
            if attempt > 0:
                # Append retry count to suffix so output files dont overwrite effectively
                # or just for clarity. 
                base_suffix = filename_suffix or crew_name
                current_suffix = f"{base_suffix}_retry_{attempt}"
            
            # Execute via base class
            last_result = super().run_crew(crew_name, inputs, current_suffix, mode,output_json)
            
            # If no validator, success is automatic (unless exception raised, which super handles)
            if not output_validator:
                success = True
                continue

            # Perform Validation
            # Only strictly applicable in INTERACTIVE mode where we wait for result
            if mode == ExecutionMode.INTERACTIVE:
                last_file = self.get_last_output_file()
                if last_file:
                    print(f"[FileCrewOrchestrator] Validating output: {last_file}")
                    if output_validator(last_file):
                        print("[FileCrewOrchestrator] Validation PASSED.")
                        success = True
                    else:
                        print(f"[FileCrewOrchestrator] Validation FAILED (Attempt {attempt+1}/{total_attempts})")
                        attempt += 1
                else:
                    print(f"[FileCrewOrchestrator] No output file found to validate. (Attempt {attempt+1}/{total_attempts})")
                    attempt += 1
            else:
                 # Background mode validation logic would go here
                 success = True

        return last_result
    
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

    def get_last_execution_id(self) -> Optional[str]:
        """
        Get the execution ID of the last run.
        
        Returns:
            Execution ID string or None
        """
        return super().get_last_execution_id()



