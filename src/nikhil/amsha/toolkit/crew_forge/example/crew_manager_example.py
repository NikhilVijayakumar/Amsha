import yaml
from nikhil.amsha.toolkit.crew_forge.dependency.container import Container as CrewContainer


class AdCopyCrewManager:
    def __init__(self, llm, app_config_path: str):
        self.llm = llm
        self.crew_container = CrewContainer()
        self.crew_builder = None
        self.module_name = 'copy'
        self.output_dir_path = 'output/intermediate'

        self.load_config(app_config_path)
        self.setup()

    def load_config(self, path: str):
        with open(path, "r") as f:
            app_config = yaml.safe_load(f)
        self.crew_container.config.from_dict(app_config)

        # Extract values for convenience
        self.module_name = self.crew_container.config.module_name()
        self.output_dir_path = self.crew_container.config.output_dir_path()

    def setup(self):
        self.crew_container.wire(modules=[__name__])

        crew_runtime_data = {
            "llm": self.llm,
            "module_name":  self.module_name ,
            "output_dir_path": self.output_dir_path
        }
        crew_container = CrewContainer()
        self.crew_builder = crew_container.crew_builder_service(**crew_runtime_data)



    def create_ad_copy_crew(self):
        self.crew_builder.add_agent(agent_id="copywriter_agent")
        self.crew_builder.add_task(
            task_id="ad_copy_task",
            agent_id="copywriter_agent",
            output_filename="ad_copy_results"
        )
        return self.crew_builder.build()

    def shutdown(self):
        self.crew_container.unwire()
