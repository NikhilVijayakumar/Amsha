from pathlib import Path
from typing import Dict, Any

from nikhil.amsha.toolkit.crew_forge.orchestrator.pipeline_orchestrator import PipelineOrchestrator
from nikhil.amsha.toolkit.llm_factory.dependency.llm_container import LLMContainer

class PipelineApplication:
    """
    Encapsulates the entire process of setting up and running a crew pipeline.
    """
    def __init__(self, config_paths: Dict[str, str]):
        """
        Initializes the application with necessary configuration paths.

        Args:
            config_paths: A dictionary containing paths to config files.
        """
        self.config_paths = config_paths
        self.llm = self._initialize_llm()
        self.orchestrator = self._initialize_orchestrator()

    def _initialize_llm(self) -> Any:
        """Sets up the DI container for the LLM and builds the instance."""
        print("⚙️  Setting up LLM...")
        llm_container = LLMContainer()
        llm_container.config.llm.yaml_path.from_value(
            str(Path(self.config_paths["llm"]))
        )
        llm_builder = llm_container.llm_builder()
        return llm_builder.build_creative().llm

    def _initialize_orchestrator(self) -> PipelineOrchestrator:
        """Creates and configures the main pipeline orchestrator."""
        print("⚙️  Setting up Orchestrator...")
        return PipelineOrchestrator(
            llm=self.llm,
            app_config_path=self.config_paths["app"],
            job_config_path=self.config_paths["job"]
        )

    def run(self) -> Any:
        """
        Executes the main pipeline and returns the final results.
        """
        print("🚀 Starting pipeline execution...")
        final_results = self.orchestrator.run_pipeline()
        print("\n--- Final Pipeline Results ---")
        print(final_results)
        return final_results


if __name__ == "__main__":
    # Configuration is now neatly defined in one place.
    configs = {
        "llm": "config/llm_config.yaml",
        "app": "config/app_config.yaml",
        "job": "config/job_config.yaml"
    }

    # The main script is now incredibly simple and clean.
    app = PipelineApplication(config_paths=configs)
    app.run()