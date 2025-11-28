from typing import Dict, Any

from nikhil.amsha.crew_forge.orchestrator.db.amsha_crew_db_application import AmshaCrewDBApplication
from nikhil.amsha.output_process.optimization.json_cleaner_utils import JsonCleanerUtils

from nikhil.amsha.toolkit.llm_factory.domain.llm_type import LLMType


class CopyApplication(AmshaCrewDBApplication):
    """
    Encapsulates the entire process of setting up and running a crew pipeline.
    """
    def __init__(self, config_paths: Dict[str, str],llm_type:LLMType):
        """
        Initializes the application with necessary configuration paths.
        """
        super().__init__(config_paths, llm_type)

    def run(self) -> Any:
        """
        Reads the 'pipeline' from the job_config and executes each crew in sequence.
        """

        print("🚀 [CopyApplication] Starting configured pipeline workflow...")

        pipeline_steps = self.job_config.get("pipeline", [])
        if not pipeline_steps:
            print("⚠️ No pipeline defined in job_config.yaml. Nothing to run.")
            return

        pipeline_results = {}
        # The input for the next step, starting as an empty dictionary.
        next_input = {}

        for crew_name in pipeline_steps:
            # For the very first step, prepare its initial inputs from the config.
            if not pipeline_results:  # This identifies the first run
                next_input = self._prepare_inputs_for(crew_name)

            # Run the crew with the current inputs
            result = self.orchestrator.run_crew(
                crew_name=crew_name,
                inputs=next_input
            )
            output_file = self.orchestrator.get_last_output_file()
            if output_file:
                cleaner = JsonCleanerUtils(output_file)
                cleaner.process_file()
            # Store the result and set it as the input for the next loop iteration
            pipeline_results[crew_name] = result
            next_input = result

        print("\n--- ✅ Final Pipeline Results ---")
        print(pipeline_results)
        return pipeline_results


if __name__ == "__main__":
    # Configuration is now neatly defined in one place.
    configs = {
        "llm": "config/llm_config.yaml",
        "app": "config/app_config.yaml",
        "job": "config/job_config.yaml"
    }

    # The main script is now incredibly simple and clean.
    app = CopyApplication(config_paths=configs,llm_type=LLMType.CREATIVE)
    app.run()