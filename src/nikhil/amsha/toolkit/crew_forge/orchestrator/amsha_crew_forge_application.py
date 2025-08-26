import json
from pathlib import Path
from typing import Dict, Any, Optional

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
                        final_inputs[placeholder] = json.load(f)
                else:  # Plain text
                    with open(file_path, 'r', encoding='utf-8') as f:
                        final_inputs[placeholder] = f.read()

            # Case 2: The value is provided directly (e.g., a string)
            else:
                print(f"  -> Loading '{placeholder}' directly from config.")
                final_inputs[placeholder] = value_def

        print(f"  -> Final prepared inputs: {list(final_inputs.keys())}")
        return final_inputs



