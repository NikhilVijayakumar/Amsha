# orchestrator.py (Refactored)
from typing import Dict, Any

from nikhil.amsha.toolkit.crew_forge.orchestrator.atomic_crew_manager import AtomicCrewManager


class CrewOrchestrator:
    """
    Orchestrates the execution of a SINGLE atomic crew. It receives a pre-built
    manager and is completely decoupled from configuration files.
    """
    def __init__(self, manager: AtomicCrewManager):
        """Initializes the orchestrator with an injected manager."""
        print("--- [Orchestrator] Initializing pure runner ---")
        self.manager = manager

    def run_crew(self, crew_name: str, inputs: Dict[str, Any]):
        """
        Builds and runs the specified atomic crew using its manager.
        """
        print(f"\n[Orchestrator] Request received to run crew: '{crew_name}'")
        crew_to_run = self.manager.build_atomic_crew(crew_name)

        print(f"[Orchestrator] Kicking off crew with inputs: {inputs}")
        result = crew_to_run.kickoff(inputs=inputs)

        print(f"[Orchestrator] Crew '{crew_name}' finished.")
        return result

    def get_last_output_file(self):
        return self.manager.output_file



