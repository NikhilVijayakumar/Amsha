from pathlib import Path
from typing import Dict, Any

from nikhil.amsha.toolkit.crew_forge.example.crew_manager_example import AdCopyCrewManager
from nikhil.amsha.toolkit.llm_factory.dependency.container import Container as LLMContainer
from nikhil.amsha.utils.yaml_utils import YamlUtils


class AdCopyOrchestrator:
    """
    Orchestrates the entire process of setting up the LLM, managing the crew,
    and running the ad copy generation task based on a job config file.
    """

    def __init__(self, llm_config_path: str, app_config_path: str, job_config_path: str):
        """
        Initializes the AdCopyOrchestrator.

        Args:
            llm_config_path: Path to the LLM configuration file.
            app_config_path: Path to the main application configuration file.
            job_config_path: Path to the job-specific configuration file.
        """
        print("--- [Orchestrator] Starting Full Process ---")
        self.app_config_path = app_config_path

        self.llm_container = LLMContainer()
        self.llm = None
        self.manager = None

        # Job-specific attributes
        self.job_params: Dict[str, Any] = {}

        # Initialize dependencies
        self._load_job_config(job_config_path)
        self._initialize_llm(llm_config_path)
        self._initialize_manager()

    def _load_job_config(self, path: str):
        """Loads the job-specific configuration."""
        print(f"[Orchestrator] Loading job config from: {path}")
        self.job_params =  YamlUtils.yaml_safe_load(path)


        required_keys = ["crew_name", "usecase", "module_name", "output_dir_path"]
        if not all(key in self.job_params for key in required_keys):
            raise ValueError(f"job_config.yaml must contain {required_keys}.")
        print("[Orchestrator] Job config loaded.")

    def _initialize_llm(self, path: str):
        """Initializes the language model from its configuration."""
        print("[Orchestrator] Initializing LLM...")
        self.llm_container.config.llm.yaml_path.from_value(str(Path(path)))
        llm_builder = self.llm_container.llm_builder()

        print("[Orchestrator] Building the 'creative' LLM...")
        actual_llm_data = llm_builder.build_creative()
        self.llm = actual_llm_data.llm
        print(f"[Orchestrator] LLM ready: {self.llm.model}")

    def _initialize_manager(self):
        """Initializes the AdCopyCrewManager."""
        if not self.llm:
            raise RuntimeError("LLM must be initialized before the manager.")
        print("[Orchestrator] Initializing Crew Manager...")

        # Using .get() as requested. This is safer and better practice.
        self.manager = AdCopyCrewManager(
            llm=self.llm,
            app_config_path=self.app_config_path,
            module_name=self.job_params.get("module_name"),
            output_dir_path=self.job_params.get("output_dir_path")
        )
        print("[Orchestrator] Crew Manager is ready.")

    def orchestrate(self):
        """
        Runs the full orchestration logic: create crew, run task, and print results.
        """
        if not self.manager:
            raise RuntimeError("Manager is not initialized.")

        try:
            crew_name = self.job_params.get("crew_name")
            usecase = self.job_params.get("usecase")
            inputs = self.job_params.get("inputs", {})  # Provide a default empty dict

            # Create the crew using parameters from the job config file
            ad_crew = self.manager.create_ad_copy_crew(crew_name, usecase)

            print(f"\n[Orchestrator] Kicking off the crew with inputs: {inputs}")
            # Pass the inputs from the job config to the kickoff method
            result = ad_crew.kickoff(inputs=inputs)

            print("\n--- [Orchestrator] Crew Finished ---")
            print("Result:", result)

        except Exception as e:
            print(f"\n[Orchestrator] An error occurred during orchestration: {e}")
        finally:
            # Ensure resources are cleaned up
            if self.manager:
                self.manager.shutdown()
            self.llm_container.unwire()
            print("--- [Orchestrator] Full Process Finished ---")


if __name__ == "__main__":
    # Define configuration file paths
    llm_config = "config/llm_config.yaml"
    app_config = "config/app_config.yaml"
    job_config = "config/job_config.yaml"

    # Create and run the orchestrator
    orchestrator = AdCopyOrchestrator(
        llm_config_path=llm_config,
        app_config_path=app_config,
        job_config_path=job_config
    )
    orchestrator.orchestrate()