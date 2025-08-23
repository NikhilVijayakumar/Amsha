# orchestrator.py (Refactored)
import json
from pathlib import Path

from crewai import LLM

from nikhil.amsha.toolkit.crew_forge.dependency.crew_forge_container import CrewForgeContainer
from nikhil.amsha.toolkit.crew_forge.orchestrator.atomic_crew_manager import AtomicCrewManager
from nikhil.amsha.toolkit.llm_factory.dependency.llm_container import LLMContainer
# Assuming the refactored manager is in a file named manager.py


from nikhil.amsha.utils.yaml_utils import YamlUtils


class PipelineOrchestrator:
    """
    Orchestrates a pipeline of atomic crews defined in a job configuration file.
    """

    def __init__(self, llm: LLM, app_config_path: str, job_config_path: str):
        print("--- [Orchestrator] Initializing Pipeline Runner ---")

        self.job_config = YamlUtils.yaml_safe_load(job_config_path)
        self.llm = llm
        # 1. Initialize LLM

        print(f"[Orchestrator] LLM ready: {self.llm.model}")

        # 2. Initialize Manager Factory
        self.manager = AtomicCrewManager(
            llm=self.llm,
            app_config_path=app_config_path,
            job_config=self.job_config
        )

        # 3. Pre-build all atomic crews defined in the config
        self.atomic_crews = {}
        for crew_name in self.job_config.get("crews", {}).keys():
            self.atomic_crews[crew_name] = self.manager.build_atomic_crew(crew_name)
        print("[Orchestrator] All atomic crews have been built.")

    def run_pipeline(self):
        """Executes the pipeline defined in the job config."""
        pipeline_steps = self.job_config.get("pipeline", [])
        if not pipeline_steps:
            print("[Orchestrator] No pipeline found to run.")
            return

        print("--- [Orchestrator] Starting Pipeline Execution ---")
        pipeline_results = {}

        for crew_name in pipeline_steps:
            crew_def = self.job_config["crews"][crew_name]
            crew_to_run = self.atomic_crews[crew_name]

            # Resolve inputs for the current step
            inputs = {}
            input_def = crew_def.get("input", {})
            source = input_def.get("source")

            if source == "file":
                file_path = Path(input_def["path"])
                print(f"[Pipeline] Loading input for '{crew_name}' from file: {file_path}")
                # Assuming JSON file for this example
                with open(file_path, 'r') as f:
                    inputs = json.load(f)

            elif source == "previous_step":
                previous_crew_name = input_def["crew"]
                if previous_crew_name not in pipeline_results:
                    raise ValueError(
                        f"Input for '{crew_name}' depends on '{previous_crew_name}', which has not been run or produced no results.")
                print(f"[Pipeline] Loading input for '{crew_name}' from previous step: '{previous_crew_name}'")
                inputs = pipeline_results[previous_crew_name]

            # Execute the crew
            print(f"\n[Pipeline] === Running Step: {crew_name} ===")
            result = crew_to_run.kickoff(inputs=inputs)
            pipeline_results[crew_name] = result
            print(f"[Pipeline] === Finished Step: {crew_name} ===\nResult: {result}")

        print("--- [Orchestrator] Pipeline Execution Finished ---")
        return pipeline_results


