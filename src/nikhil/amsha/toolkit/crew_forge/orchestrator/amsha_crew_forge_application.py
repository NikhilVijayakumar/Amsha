import json
from pathlib import Path
from typing import Dict, Any

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
        llm = self._initialize_llm()
        manager = AtomicCrewManager(
            llm=llm,
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
            return llm_builder.build_creative().llm
        return llm_builder.build_evaluation().llm

    def _prepare_inputs_for(self, crew_name: str) -> dict:
        """Prepares inputs for a specific crew defined in the job config."""
        crew_def = self.job_config["crews"][crew_name]
        input_def = crew_def.get("input", {})

        if input_def.get("source") == "file":
            file_path = Path(input_def["path"])
            # This logic can be expanded to handle text, json, etc.
            with open(file_path, 'r') as f:
                return json.load(f)
        elif input_def.get("source") == "direct":
            return input_def.get("value", {})

        return {}



