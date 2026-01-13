
from typing import Dict, Any, Optional

from amsha.crew_forge.orchestrator.file.amsha_crew_file_application import AmshaCrewFileApplication
from amsha.llm_factory.domain.model.llm_type import LLMType
from model.science_knowledge_base import ScienceKnowledgeBase


class GenerateScientificKnowledgeApplication(AmshaCrewFileApplication):

    def __init__(self, config_paths: Dict[str, str],llm_type:LLMType, inputs=None, llm_config_override: Optional[Dict] = None):

        super().__init__(config_paths, llm_type, inputs, llm_config_override)


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
                pipeline_input["scientific_concept"] = next_input["scientific_concept"]
                print(f"{class_name} - pipeline_input:{pipeline_input}")
                result =self.execute_crew_with_retry( crew_name=crew_name,inputs=pipeline_input,
                                                      output_json = ScienceKnowledgeBase,
                                                      output_folder= next_input["podcast_name"])

                results_for_list.append(result)
            pipeline_results[crew_name] = results_for_list
        return pipeline_results


if __name__ == "__main__":
    # Configuration is now neatly defined in one place.
    configs = {
        "llm": "example/crew_forge/config/llm_config.yaml",
        "app": "example/crew_forge/config/app_config.yaml",
        "job": "example/crew_forge/config/scientific_kb_config.yaml"
    }
    inputs_list = [
        {
            "scientific_concept": {
                "key_name": "topic",
                "source": "direct",
                "value": "Quantum Entanglement"
            }
        },
        {
            "podcast_name": {
                "key_name": "title",
                "source": "direct",
                "value": "The Science Minute"
            }
        }
    ]
    llm_config_override = {
        "model_config": {
            "base_url": "http://localhost:1234/v1",
            "model": "lm_studio/gemma-3-12b-it",
            "api_key": "lm_studio"
        },
        "llm_parameters": {
            "temperature": 0.8,
            "top_p": 0.9,
            "max_completion_tokens": 8192
        }
    }
    # The main script is now incredibly simple and clean.
    app = GenerateScientificKnowledgeApplication(config_paths=configs, llm_type=LLMType.CREATIVE, inputs=inputs_list, llm_config_override=llm_config_override)
    app.run()


