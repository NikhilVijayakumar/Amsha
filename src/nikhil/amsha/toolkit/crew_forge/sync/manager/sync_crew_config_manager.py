import json
import os
from typing import List, Dict, Any
from nikhil.amsha.toolkit.crew_forge.dependency.crew_forge_container import CrewForgeContainer
from nikhil.amsha.toolkit.crew_forge.domain.models.crew_config_data import CrewConfigResponse
from nikhil.amsha.utils.yaml_utils import YamlUtils


class SyncCrewConfigManager:

    def __init__(self,app_config_path: str, job_config_path: str):
        print("[SyncCrewConfig] Initializing...")


        # Load the YAML configuration file
        job_config = YamlUtils.yaml_safe_load(job_config_path)

        self.job_config = job_config

        # Get the output filepath from the loaded config and store it
        self.output_filepath = self.job_config.get("output_filepath")

        if not self.output_filepath:
            raise ValueError(
                "[SyncCrewConfig] Error: 'output_filepath' key not found in the job configuration file."
            )
        app_config = YamlUtils.yaml_safe_load(app_config_path)
        self.app_config = app_config


        self.crew_container = CrewForgeContainer()
        self.crew_container.config.from_dict(app_config)
        self.blueprint_service = self.crew_container.crew_blueprint_service()
        self.master_blueprint: List[CrewConfigResponse] = self.blueprint_service.get_all_config()
        print(f"[SyncCrewConfig] Found {len(self.master_blueprint)} crew configurations to process.")

    def _process_blueprint(self, crew_config: CrewConfigResponse) -> Dict[str, Any]:
        return {
            "name": crew_config.name,
            "usecase": crew_config.usecase,
            "agents": list(crew_config.agents.keys()),
            "tasks": list(crew_config.tasks.keys()),
        }

    def sync(self):
        if not self.master_blueprint:
            print("[SyncCrewConfig] No crew configurations found. Nothing to sync.")
            return

        print("[SyncCrewConfig] Processing all crew blueprints...")
        processed_configs = [self._process_blueprint(config) for config in self.master_blueprint]

        try:
            output_dir = os.path.dirname(self.output_filepath)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)

            print(f"[SyncCrewConfig] Saving processed configurations to '{self.output_filepath}'...")
            with open(self.output_filepath, 'w') as json_file:
                json.dump(processed_configs, json_file, indent=4)
            print(f"[SyncCrewConfig] ✅ Successfully saved configurations to '{self.output_filepath}'.")
        except IOError as e:
            print(f"[SyncCrewConfig] ❌ Error: Failed to write to file '{self.output_filepath}'. Reason: {e}")