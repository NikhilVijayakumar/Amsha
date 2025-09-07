import json
from pathlib import Path
from typing import Dict, Any, Optional

from nikhil.amsha.toolkit.crew_forge.Utils.json_cleaner_utils import JsonCleanerUtils
from nikhil.amsha.toolkit.crew_forge.orchestrator.atomic_crew_manager import AtomicCrewManager
from nikhil.amsha.toolkit.crew_forge.orchestrator.crew_orchestrator import CrewOrchestrator
from nikhil.amsha.toolkit.llm_factory.dependency.llm_container import LLMContainer
from nikhil.amsha.toolkit.llm_factory.domain.llm_type import LLMType
from nikhil.amsha.utils.yaml_utils import YamlUtils


class AmshaCrewForgeApplication:
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
        manager = AtomicCrewManager(
            llm=llm,
            model_name = self.model_name,
            app_config_path=config_paths["app"],
            job_config=self.job_config
        )
        self.orchestrator = CrewOrchestrator(manager)


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
        # raw_content = current_file.read_text(encoding='utf-8')
        # for attempt in range(max_llm_retries + 1):
        #     print(f"--- Cleaning Attempt {attempt + 1}/{max_llm_retries + 1} for {output_filename} ---")
        #     try:
        #         # 1. Always try the fast, local cleaner first.
        #         print(f"raw_content:{raw_content}")
        #         if cleaner.process_content(raw_content):
        #             print(f"✅ JSON validated successfully. Clean file at: {cleaner.output_file_path}")
        #             return True
        #
        #         # 2. If it fails, check if we have any LLM retries left.
        #         if attempt >= max_llm_retries:
        #             print(f"❌ Max retries reached. Could not fix the file.")
        #             break  # Exit the loop after the last failed attempt
        #
        #         # 3. If retries are available, use the LLM to try and fix the file.
        #         print(
        #             f"⚠️ Initial cleaning failed. Attempting to fix with LLM (Attempt {attempt + 1}/{max_llm_retries})...")
        #         json_input = {"raw_llm_output": raw_content}
        #
        #         # The LLM crew overwrites the existing file with its fix
        #         raw_content = self.orchestrator.json_crew(
        #             inputs=json_input,
        #             output_filename=output_filename
        #         )
        #         print(f"🤖 LLM fix applied. Re-validating in the next loop...\n{raw_content}")
        #
        #     except Exception as e:
        #         print(f"❌ An error occurred during the LLM fix: {e}")
                # If the LLM crew itself fails, we should stop.


        return False



