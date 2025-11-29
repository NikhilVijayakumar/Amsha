# orchestrator.py (Refactored)
from typing import Dict, Any, Optional

from amsha.crew_forge.orchestrator.file.atomic_crew_file_manager import AtomicCrewFileManager
from amsha.crew_monitor.service.crew_performance_monitor import CrewPerformanceMonitor


class FileCrewOrchestrator:
    """
    Orchestrates the execution of a SINGLE atomic crew. It receives a pre-built
    manager and is completely decoupled from configuration files.
    """
    def __init__(self, manager: AtomicCrewFileManager):
        """Initializes the orchestrator with an injected manager."""
        print("--- [Orchestrator] Initializing pure runner ---")
        self.manager = manager
        self.last_monitor: Optional[CrewPerformanceMonitor] = None

    def run_crew(self, crew_name: str, inputs: Dict[str, Any],filename_suffix:Optional[str]=None):
        """
        Builds and runs the specified atomic crew using its manager.
        """
        print(f"\n[Orchestrator] Request received to run crew: '{crew_name}'")
        crew_to_run = self.manager.build_atomic_crew(crew_name,filename_suffix)

        print(f"[Orchestrator] Kicking off crew with inputs: {inputs}")
        
        # Initialize monitor with model name from manager
        self.last_monitor = CrewPerformanceMonitor(model_name=self.manager.model_name)
        self.last_monitor.start_monitoring()
        
        result = crew_to_run.kickoff(inputs=inputs)
        
        self.last_monitor.stop_monitoring()
        self.last_monitor.log_usage(result)
        print(self.last_monitor.get_summary())

        print(f"[Orchestrator] Crew '{crew_name}' finished.")
        return result


    def get_last_output_file(self)->Optional[str]:
        return self.manager.output_file

    def get_last_performance_stats(self) -> Optional[CrewPerformanceMonitor]:
        """Returns the performance monitor from the last run."""
        return self.last_monitor



