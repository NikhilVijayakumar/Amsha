import json
from pathlib import Path
from typing import Dict, Any, Optional

from nikhil.amsha.crew_forge.orchestrator.file.atomic_crew_file_manager import AtomicCrewFileManager
from nikhil.amsha.crew_forge.orchestrator.file.file_crew_orchestrator import FileCrewOrchestrator
from nikhil.amsha.toolkit.llm_factory.dependency.llm_container import LLMContainer
from nikhil.amsha.toolkit.llm_factory.domain.llm_type import LLMType
from nikhil.amsha.output_process.optimization.json_cleaner_utils import JsonCleanerUtils
from nikhil.amsha.utils.yaml_utils import YamlUtils


class AmshaCrewFileApplication:
    """
    A reusable base class that handles all the boilerplate setup for running a crew.

    """

    def __init__(self, config_paths: Dict[str, str],llm_type:LLMType):
        """
        Initializes the application with necessary configuration paths.

        Args:
            config_paths: A dictionary containing paths to config files.
        """
        self.llm_type = llm_type
        self.config_paths = config_paths
        self.job_config = YamlUtils.yaml_safe_load(config_paths["job"])
        self.model_name:Optional[str] = None
        llm = self._initialize_llm()
        manager = AtomicCrewFileManager(
            llm=llm,
            model_name = self.model_name,
            app_config_path=config_paths["app"],
            job_config=self.job_config
        )
        self.orchestrator = FileCrewOrchestrator(manager)


    def _initialize_llm(self) -> Any:
        """Sets up the DI container for the LLM and builds the instance."""
        print("⚙️  Setting up LLM...")
        llm_container = LLMContainer()
        llm_container.config.llm.yaml_path.from_value(
            str(Path(self.config_paths["llm"]))
        )
        llm_builder = llm_container.llm_builder()
        if self.llm_type == LLMType.CREATIVE:
            build_llm = llm_builder.build_creative()
        else:
            build_llm = llm_builder.build_evaluation()
        self.model_name = build_llm.model_name
        return build_llm.llm


    def _prepare_multiple_inputs_for(self, crew_name: str) -> dict:
        """
        Prepares the inputs dictionary for a specific crew by resolving values
        from a list of sources in the job config.
        """
        crew_def = self.job_config["crews"][crew_name]
        # Expect a list of inputs, defaulting to an empty list
        inputs_def = crew_def.get("input", [])
        final_inputs = {}

        print(f"📦 [App] Preparing inputs for '{crew_name}'...")

        # Loop through each input definition in the list
        for input_item in inputs_def:
            key_name = input_item["key_name"]  # The key for the final dictionary

            # Case 1: The value is from a file source
            if input_item.get("source") == "file":
                file_path = Path(input_item["path"])
                file_format = input_item.get("format", "text")
                print(f"  -> Loading '{key_name}' from file: {file_path}")

                if file_format == "json":
                    with open(file_path, 'r', encoding='utf-8') as f:
                        # Correctly assign the loaded data to its key
                        final_inputs[key_name] = json.load(f)
                else:  # Plain text
                    with open(file_path, 'r', encoding='utf-8') as f:
                        # Correctly assign the loaded data to its key
                        final_inputs[key_name] = f.read()

            # Case 2: The value is provided directly in the config
            elif input_item.get("source") == "direct":
                print(f"  -> Loading '{key_name}' directly from config.")
                final_inputs[key_name] = input_item["value"]

        print(f"  -> Final prepared inputs: {list(final_inputs.keys())}")
        return final_inputs


    def _prepare_inputs_for(self, crew_name: str) -> dict:
        """
        Prepares the inputs dictionary for a specific crew by resolving values
        from the job config.
        """
        crew_def = self.job_config["crews"][crew_name]
        inputs_def = crew_def.get("input", {})  # Get the inputs dictionary
        final_inputs = {}

        print(f"📦 [App] Preparing inputs for '{crew_name}'...")

        # Loop through each placeholder and its defined value
        for placeholder, value_def in inputs_def.items():

            # Case 1: The value is a dictionary defining a file source
            if isinstance(value_def, dict) and value_def.get("source") == "file":
                file_path = Path(value_def["path"])
                file_format = value_def.get("format", "text")
                print(f"  -> Loading '{placeholder}' from file: {file_path}")

                if file_format == "json":
                    with open(file_path, 'r', encoding='utf-8') as f:
                        final_inputs = json.load(f)
                else:  # Plain text
                    with open(file_path, 'r', encoding='utf-8') as f:
                        final_inputs = f.read()

            # Case 2: The value is provided directly (e.g., a string)
            else:
                print(f"  -> Loading '{placeholder}' directly from config.")
                final_inputs = value_def


        return final_inputs



    def clean_json(self, output_filename: str, max_llm_retries: int = 2) -> bool:
        """
        Cleans and validates a JSON file, using an LLM for fixes with a retry limit.

        Args:
            output_filename: The path to the JSON file to be cleaned.
            max_llm_retries: The maximum number of times to call the LLM to fix the file.

        Returns:
            The true or false.
        """
        print(f"AmshaCrewForgeApplication:{output_filename}")
        current_file = Path(output_filename)
        cleaner = JsonCleanerUtils(output_filename)
        if cleaner.process_file():
            print(f"✅ JSON validated successfully. Clean file at: {cleaner.output_file_path}")
            return True
        return False



