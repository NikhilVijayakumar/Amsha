from typing import Dict, Any

from nikhil.vak.domain.llm_factory.domain.llm_type import LLMType

from nikhil.amsha.crew_forge.orchestrator.file.amsha_crew_file_application import AmshaCrewFileApplication


class DesignerCrewApplication(AmshaCrewFileApplication):

    def __init__(self, config_paths: Dict[str, str],llm_type:LLMType):

        super().__init__(config_paths, llm_type)


    def run(self) -> Any:
        class_name = self.__class__.__name__
        print(f"{class_name} - Starting configured pipeline workflow...")
        pipeline_steps = self.job_config.get("pipeline", [])
        if not pipeline_steps:
            print("No pipeline defined in job_config.yaml. Nothing to run.")
            return

        pipeline_results = {}
        results_for_list = []
        pipeline_input = {}
        for crew_name in pipeline_steps:
            if not pipeline_results:
                next_input = self._prepare_multiple_inputs_for(crew_name)
                pipeline_input["novel_blueprint"] = next_input
                print(f"{class_name} - pipeline_input:{pipeline_input}")
                result = self.orchestrator.run_crew(
                    crew_name=crew_name,
                    inputs=pipeline_input
                )
                output_file = self.orchestrator.get_last_output_file()
                if output_file:
                    print(f"{class_name}:{output_file}")
                    self.clean_json(output_file)


                results_for_list.append(result)
            pipeline_results[crew_name] = results_for_list
        return pipeline_results


if __name__ == "__main__":
    # Configuration is now neatly defined in one place.
    configs = {
        "llm": Settings.LLM_CONFIG,
        "app": Settings.APP_CONFIG,
        "job": "config/job_config.yaml"
    }

    # The main script is now incredibly simple and clean.
    app = DesignerCrewApplication(config_paths=configs,llm_type=LLMType.CREATIVE)
    app.run()