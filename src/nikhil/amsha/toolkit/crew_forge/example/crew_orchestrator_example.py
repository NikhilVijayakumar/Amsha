from pathlib import Path
from nikhil.amsha.toolkit.crew_forge.example.crew_manager_example import AdCopyCrewManager
from nikhil.amsha.toolkit.llm_factory.dependency.container import Container as LLMContainer


class AdCopyOrchestrator:
    def __init__(self, llm_config_path: str, crew_config_path: str):
        self.llm_config_path = llm_config_path
        self.crew_config_path = crew_config_path
        self.llm = None
        self.manager = None

        self.initialize_llm()
        self.initialize_manager()

    def initialize_llm(self):
        llm_container = LLMContainer()
        llm_container.config.llm.yaml_path.from_value(str(Path(self.llm_config_path)))
        llm_builder = llm_container.llm_builder()
        actual_llm_data = llm_builder.build_creative()
        self.llm = actual_llm_data.llm

    def initialize_manager(self):
        self.manager = AdCopyCrewManager(
            llm=self.llm,
            app_config_path=self.crew_config_path
        )

    def orchestrate(self):
        try:
            ad_crew = self.manager.create_ad_copy_crew()
            print("\n[Main] Running Crew...")
            result = ad_crew.kickoff()
            print("\n[Main] Crew Finished. Result:")
            print(result)
        finally:
            self.manager.shutdown()


if __name__ == "__main__":
    orchestrator = AdCopyOrchestrator(
        llm_config_path="config/llm_config.yaml",
        crew_config_path="config/app_config.yaml"
    )
    orchestrator.orchestrate()
