import yaml

from typing import Optional

from nikhil.amsha.toolkit.crew_forge.dependency.container import Container as CrewContainer
from nikhil.amsha.toolkit.crew_forge.domain.models.crew_config_data import CrewConfigResponse
from nikhil.amsha.utils.yaml_utils import YamlUtils


class AdCopyCrewManager:
    """
    Manages the creation and configuration of the Ad Copy Crew.

    This class is responsible for loading crew blueprints, adding agents and tasks,
    and building the final crew object.
    """

    def __init__(self, llm, app_config_path: str, module_name: str, output_dir_path: str):
        """
        Initializes the AdCopyCrewManager.

        Args:
            llm: The language model instance to be used by the crew.
            app_config_path: Path to the application's configuration file for blueprints.
            module_name: The name of the module for the crew builder.
            output_dir_path: The path for the crew's output files.
        """
        print("[Manager] Initializing...")
        self.llm = llm
        self.module_name = module_name
        self.output_dir_path = output_dir_path
        self.crew_container = CrewContainer()
        self.crew_builder = None

        # Load configuration and setup the crew builder
        self._load_app_config(app_config_path)
        self._setup_crew_builder()
        print("[Manager] Initialized successfully.")

    def _load_app_config(self, path: str):
        """Loads the main application configuration for accessing blueprints."""
        print(f"[Manager] Loading application config from: {path}")
        app_config = YamlUtils.yaml_safe_load(path)

        self.crew_container.config.from_dict(app_config)
        print("[Manager] Application config loaded.")

    def _setup_crew_builder(self):
        """Initializes the CrewBuilderService with runtime data."""
        print("[Manager] Setting up Crew Builder...")

        crew_runtime_data = {
            "llm": self.llm,
            "module_name": self.module_name,
            "output_dir_path": self.output_dir_path
        }

        # We get the builder service from the container
        self.crew_builder = self.crew_container.crew_builder_service(**crew_runtime_data)
        print(f"[Manager] Crew Builder is ready. Output will be saved to '{self.output_dir_path}'")

    def create_ad_copy_crew(self, crew_name: str, usecase: str):
        """
        Creates and configures the ad copy crew.

        Args:
            crew_name: The name of the crew blueprint to use.
            usecase: The usecase of the crew blueprint.

        Returns:
            The fully configured crew object, ready to be kicked off.
        """
        print(f"[Manager] Creating crew '{crew_name}' for usecase '{usecase}'.")
        blueprint_service = self.crew_container.crew_blueprint_service()
        config_data: Optional[CrewConfigResponse] = blueprint_service.get_config(name=crew_name, usecase=usecase)

        if not config_data:
            raise ValueError(f"Crew configuration blueprint not found for name='{crew_name}' and usecase='{usecase}'")

        print(f"[Manager] Blueprint for crew '{config_data.name}' loaded successfully.")

        agent_id = config_data.agents.get("copywriter_agent")
        task_id = config_data.tasks.get("ad_copy_task")

        if not agent_id or not task_id:
            raise ValueError("Blueprint is missing 'copywriter_agent' or 'ad_copy_task'.")

        self.crew_builder.add_agent(agent_id=agent_id)
        agent_object = self.crew_builder.get_last_agent()
        self.crew_builder.add_task(
            task_id=task_id,
            agent=agent_object,
            output_filename="ad_copy_results"
        )

        print("[Manager] Agent and Task added to the crew.")
        ad_crew = self.crew_builder.build()
        print("[Manager] Crew built successfully.")
        return ad_crew

    def shutdown(self):
        """Unwires the dependency injection container."""
        print("[Manager] Shutting down...")
        self.crew_container.unwire()
        print("[Manager] Shutdown complete.")