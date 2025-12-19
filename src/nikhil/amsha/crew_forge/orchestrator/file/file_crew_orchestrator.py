# orchestrator.py (Refactored)
from typing import Dict, Any, Optional, Union

from amsha.crew_forge.orchestrator.file.atomic_crew_file_manager import AtomicCrewFileManager
from amsha.crew_monitor.service.crew_performance_monitor import CrewPerformanceMonitor
from amsha.execution_runtime.service.runtime_engine import RuntimeEngine
from amsha.execution_runtime.domain.execution_mode import ExecutionMode
from amsha.execution_runtime.domain.execution_handle import ExecutionHandle
from amsha.execution_state.service.state_manager import StateManager
from amsha.execution_state.domain.enums import ExecutionStatus


class FileCrewOrchestrator:
    """
    Orchestrates the execution of a SINGLE atomic crew. It receives a pre-built
    manager and is completely decoupled from configuration files.
    """
    def __init__(self, manager: AtomicCrewFileManager, runtime: Optional[RuntimeEngine] = None, state_manager: Optional[StateManager] = None):
        """Initializes the orchestrator with an injected manager, runtime, and state manager."""
        print("--- [Orchestrator] Initializing pure runner ---")
        self.manager = manager
        self.last_monitor: Optional[CrewPerformanceMonitor] = None
        self.runtime = runtime or RuntimeEngine()
        self.state_manager = state_manager or StateManager()

    def run_crew(self, crew_name: str, inputs: Dict[str, Any], filename_suffix:Optional[str]=None, mode: ExecutionMode = ExecutionMode.INTERACTIVE) -> Union[Any, ExecutionHandle]:
        """
        Builds and runs the specified atomic crew using its manager.
        Supports both valid Interactive and Background execution modes.
        """
        print(f"\n[Orchestrator] Request received to run crew: '{crew_name}'")
        
        # 1. Create Execution State
        state = self.state_manager.create_execution(inputs=inputs)
        print(f"[Orchestrator] Created Execution State ID: {state.execution_id}")
        self.state_manager.update_status(state.execution_id, ExecutionStatus.RUNNING, metadata={"crew_name": crew_name, "mode": mode.value})
        
        try:
            crew_to_run = self.manager.build_atomic_crew(crew_name,filename_suffix)
        except Exception as e:
            self.state_manager.update_status(state.execution_id, ExecutionStatus.FAILED, metadata={"error": str(e)})
            raise e

        def _execute_kickoff():
            print(f"[Orchestrator] Kicking off crew with inputs: {inputs}")
            
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
                print(f"[Orchestrator] Crew '{crew_name}' finished.")
                
                # Update State on Success
                self.state_manager.update_status(state.execution_id, ExecutionStatus.COMPLETED, metadata={"metrics": metrics})
                
                if isinstance(result, (str, dict, list, int, float, bool)):
                     current_state = self.state_manager.get_execution(state.execution_id)
                     if current_state:
                         current_state.set_output("result", result)
                         self.state_manager.repository.save(current_state)
                
                return result
            except Exception as e:
                print(f"[Orchestrator] Execution Failed: {e}")
                self.state_manager.update_status(state.execution_id, ExecutionStatus.FAILED, metadata={"error": str(e)})
                raise e

        handle = self.runtime.submit(_execute_kickoff, mode=mode)
        
        # Attach execution_id to handle if possible (monkey patch for now just for correlation)
        handle.execution_state_id = state.execution_id
        
        if mode == ExecutionMode.INTERACTIVE:
            return handle.result()
        return handle


    def get_last_output_file(self)->Optional[str]:
        return self.manager.output_file

    def get_last_performance_stats(self) -> Optional[CrewPerformanceMonitor]:
        """Returns the performance monitor from the last run."""
        return self.last_monitor



