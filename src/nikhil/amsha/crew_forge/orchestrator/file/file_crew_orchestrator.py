# orchestrator.py (Refactored)
from typing import Dict, Any, Optional

from nikhil.amsha.crew_forge.orchestrator.file.atomic_crew_file_manager import AtomicCrewFileManager


class FileCrewOrchestrator:
    """
    Orchestrates the execution of a SINGLE atomic crew. It receives a pre-built
    manager and is completely decoupled from configuration files.
    """
    def __init__(self, manager: AtomicCrewFileManager):
        """Initializes the orchestrator with an injected manager."""
        print("--- [Orchestrator] Initializing pure runner ---")
        self.manager = manager

    def run_crew(self, crew_name: str, inputs: Dict[str, Any],filename_suffix:Optional[str]=None):
        """
        Builds and runs the specified atomic crew using its manager.
        """
        print(f"\n[Orchestrator] Request received to run crew: '{crew_name}'")
        crew_to_run = self.manager.build_atomic_crew(crew_name,filename_suffix)

        print(f"[Orchestrator] Kicking off crew with inputs: {inputs}")
        result = crew_to_run.kickoff(inputs=inputs)

        print(f"[Orchestrator] Crew '{crew_name}' finished.")
        return result


    def get_last_output_file(self)->Optional[str]:
        return self.manager.output_file



