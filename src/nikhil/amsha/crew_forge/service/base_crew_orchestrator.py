"""
Base orchestrator providing shared execution logic for all crew orchestrator implementations.
"""
from typing import Dict, Any, Optional, Union
from amsha.execution_runtime.service.runtime_engine import RuntimeEngine
from amsha.execution_runtime.domain.execution_mode import ExecutionMode
from amsha.execution_runtime.domain.execution_handle import ExecutionHandle
from amsha.execution_state.service.state_manager import StateManager
from amsha.execution_state.domain.enums import ExecutionStatus
from amsha.crew_monitor.service.crew_performance_monitor import CrewPerformanceMonitor
from amsha.crew_forge.protocols.crew_manager import CrewManager
from amsha.crew_forge.exceptions import (
    CrewExecutionException,
    CrewManagerException,
    ErrorContext,
    ErrorMessageBuilder,
    wrap_external_exception
)


class BaseCrewOrchestrator:
    """Shared orchestration logic for all crew orchestrator implementations."""
    
    def __init__(
        self, 
        manager: CrewManager, 
        runtime: Optional[RuntimeEngine] = None,
        state_manager: Optional[StateManager] = None
    ):
        """
        Initialize the base orchestrator with injected dependencies.
        
        Args:
            manager: CrewManager Protocol implementation for building crews
            runtime: Optional RuntimeEngine for execution management
            state_manager: Optional StateManager for execution state tracking
        """
        print("--- [BaseOrchestrator] Initializing shared orchestrator logic ---")
        self.manager = manager
        self.runtime = runtime or RuntimeEngine()
        self.state_manager = state_manager or StateManager()
        self.last_monitor: Optional[CrewPerformanceMonitor] = None
    
    def run_crew(
        self,
        crew_name: str,
        inputs: Dict[str, Any],
        filename_suffix: Optional[str] = None,
        mode: ExecutionMode = ExecutionMode.INTERACTIVE
    ) -> Union[Any, ExecutionHandle]:
        """
        Shared crew execution logic that works with any CrewManager implementation.
        
        Args:
            crew_name: Name of the crew to execute
            inputs: Input parameters for the crew
            filename_suffix: Optional suffix for output files
            mode: Execution mode (INTERACTIVE or BACKGROUND)
            
        Returns:
            Execution result (direct result for INTERACTIVE, ExecutionHandle for BACKGROUND)
            
        Raises:
            CrewManagerException: If crew building fails
            CrewExecutionException: If crew execution fails
        """
        print(f"\n[BaseOrchestrator] Request received to run crew: '{crew_name}'")
        
        context = ErrorContext("BaseCrewOrchestrator", "run_crew")
        context.add_context("crew_name", crew_name)
        context.add_context("mode", mode.value)
        
        # Create execution state
        state = self.state_manager.create_execution(inputs=inputs)
        print(f"[BaseOrchestrator] Created Execution State ID: {state.execution_id}")
        context.add_context("execution_id", state.execution_id)
        
        self.state_manager.update_status(
            state.execution_id, 
            ExecutionStatus.RUNNING, 
            metadata={"crew_name": crew_name, "mode": mode.value}
        )
        
        try:
            crew_to_run = self.manager.build_atomic_crew(crew_name, filename_suffix)
        except Exception as e:
            error_message = ErrorMessageBuilder.manager_error(
                "CrewManager", 
                "build_atomic_crew", 
                str(e)
            )
            
            self.state_manager.update_status(
                state.execution_id, 
                ExecutionStatus.FAILED, 
                metadata={"error": error_message}
            )
            
            # Wrap in appropriate exception type
            if isinstance(e, (CrewManagerException, CrewExecutionException)):
                raise
            else:
                raise wrap_external_exception(e, context, CrewManagerException)

        def _execute_kickoff():
            """Internal function to execute crew kickoff with monitoring."""
            print(f"[BaseOrchestrator] Kicking off crew with inputs: {inputs}")
            
            # Initialize monitor with model name from manager
            self.last_monitor = CrewPerformanceMonitor(model_name=self.manager.model_name)
            self.last_monitor.start_monitoring()
            
            try:
                result = crew_to_run.kickoff(inputs=inputs)
                
                self.last_monitor.stop_monitoring()
                self.last_monitor.log_usage(result)
                summary = self.last_monitor.get_summary()
                metrics = self.last_monitor.get_metrics()
                print(summary)
                print(f"[BaseOrchestrator] Crew '{crew_name}' finished.")
                
                # Update state on success
                self.state_manager.update_status(
                    state.execution_id, 
                    ExecutionStatus.COMPLETED, 
                    metadata={"metrics": metrics}
                )
                
                # Store result if serializable
                if isinstance(result, (str, dict, list, int, float, bool)):
                    current_state = self.state_manager.get_execution(state.execution_id)
                    if current_state:
                        current_state.set_output("result", result)
                        self.state_manager.repository.save(current_state)
                
                return result
            except Exception as e:
                error_message = ErrorMessageBuilder.execution_error(
                    crew_name, 
                    "crew_kickoff", 
                    str(e)
                )
                print(f"[BaseOrchestrator] Execution Failed: {error_message}")
                
                self.state_manager.update_status(
                    state.execution_id, 
                    ExecutionStatus.FAILED, 
                    metadata={"error": error_message}
                )
                
                # Wrap in execution exception
                if isinstance(e, CrewExecutionException):
                    raise
                else:
                    execution_context = ErrorContext("BaseCrewOrchestrator", "crew_kickoff")
                    execution_context.add_context("crew_name", crew_name)
                    execution_context.add_context("execution_id", state.execution_id)
                    raise wrap_external_exception(e, execution_context, CrewExecutionException)
        
        handle = self.runtime.submit(_execute_kickoff, mode=mode)
        
        # Attach execution_id to handle for correlation
        handle.execution_state_id = state.execution_id
        
        if mode == ExecutionMode.INTERACTIVE:
            return handle.result()
        return handle
    
    def get_last_output_file(self) -> Optional[str]:
        """Get the path to the last generated output file."""
        return self.manager.output_file
    
    def get_last_performance_stats(self) -> Optional[CrewPerformanceMonitor]:
        """Get performance statistics from the last execution."""
        return self.last_monitor