from typing import Optional, Dict, Any

from crewai.knowledge.source.text_file_knowledge_source import TextFileKnowledgeSource

from nikhil.amsha.toolkit.crew_forge.dependency.crew_forge_container import CrewForgeContainer
from nikhil.amsha.toolkit.crew_forge.domain.models.crew_config_data import CrewConfigResponse
from nikhil.amsha.utils.yaml_utils import YamlUtils


class AtomicCrewManager:
    """
    Acts as a factory to build specific, atomic crews based on a master blueprint
    and a job configuration file.
    """


    def __init__(self, llm, app_config_path: str, job_config: Dict[str, Any], model_name:str):
        print("[Manager] Initializing Factory...")
        self.llm = llm
        self.job_config = job_config
        self.crew_container = CrewForgeContainer()
        self.model_name = model_name

        # Load app config for DI
        app_config = YamlUtils.yaml_safe_load(app_config_path)
        self.app_config = app_config
        self.crew_container.config.from_dict(app_config)
        self.output_file:Optional[str] = None

        # Fetch the single master blueprint using top-level keys from job_config
        self.blueprint_service = self.crew_container.crew_blueprint_service()
        self.master_blueprint: Optional[CrewConfigResponse] = self.blueprint_service.get_config(
            name=self.job_config["crew_name"],
            usecase=self.job_config["usecase"]
        )

        if not self.master_blueprint:
            raise ValueError("Master blueprint specified in job_config not found in the database.")
        print("[Manager] Master blueprint loaded successfully.")

    def build_atomic_crew(self, crew_name: str,filename_suffix:Optional[str]=None):
        """Builds a single, atomic crew from a subset of the master blueprint."""
        print(f"[Manager] Building atomic crew: '{crew_name}'...")
        crew_def = self.job_config["crews"].get(crew_name)
        if not crew_def:
            raise ValueError(f"Definition for atomic crew '{crew_name}' not found in job_config.")

        # Set up a new, clean crew builder for this specific atomic crew
        crew_runtime_data = {
            "llm": self.llm,
            "module_name": self.job_config.get("module_name", ""),
            "output_dir_path": self.app_config.get("output_dir_path", f"output/{crew_name}")
        }
        crew_builder = self.crew_container.crew_builder_service(**crew_runtime_data)

        for step in crew_def['steps']:
            task_key = step['task_key']
            agent_key = step['agent_key']

            task_id = self.master_blueprint.tasks.get(task_key)
            if not task_id:
                raise ValueError(f"Task '{task_key}' not found in master blueprint.")

            agent_id = self.master_blueprint.agents.get(agent_key)
            if not agent_id:
                raise ValueError(f"Agent '{agent_id}' not found in master blueprint.")

            agent_knowledge_paths = set()
            for path in step.get('knowledge_sources', []):
                agent_knowledge_paths.add(path)
            if agent_knowledge_paths:
                agent_text_source = TextFileKnowledgeSource(
                    file_paths=list(agent_knowledge_paths)
                )
            else:
                agent_text_source = None
            crew_builder.add_agent(
                agent_id=agent_id,
                knowledge_sources=agent_text_source
            )
            if filename_suffix:
                crew_builder.add_task(
                    task_id=task_id,
                    agent=crew_builder.get_last_agent(),
                    output_filename=f"{self.model_name}_{task_key}_{filename_suffix}"
                )
            else:
                crew_builder.add_task(
                    task_id=task_id,
                    agent=crew_builder.get_last_agent(),
                    output_filename=f"{self.model_name}_{task_key}"
                )

        self.output_file = crew_builder.get_last_file()

        crew_knowledge_paths = set()

        # 2. Add crew-level knowledge sources
        for path in crew_def.get('knowledge_sources', []):
            crew_knowledge_paths.add(path)
        if crew_knowledge_paths:
            crew_text_source = TextFileKnowledgeSource(
                file_paths=list(crew_knowledge_paths)
            )
        else:
            crew_text_source = None

        print(f"[Manager] Finished building '{crew_name}'.")
        return crew_builder.build(knowledge_sources=crew_text_source)

    def build_json_crew(self,output_filename):
        json_validator = self.job_config.get("json_validator", {})
        task_key = json_validator['task_key']
        agent_key = json_validator['agent_key']
        blueprint = self.blueprint_service.get_config(
            name="Json Validator Crew",
            usecase="Json Validator"
        )
        task_id = blueprint.tasks.get(task_key)
        if not task_id:
            raise ValueError(f"Task '{task_key}' not found in master blueprint.")

        agent_id = blueprint.agents.get(agent_key)
        if not agent_id:
            raise ValueError(f"Agent '{agent_id}' not found in master blueprint.")

        crew_runtime_data = {
            "llm": self.llm,
            "module_name": "Json Validator Crew",
            "output_dir_path": output_filename
        }
        crew_builder = self.crew_container.crew_builder_service(**crew_runtime_data)

        crew_builder.add_agent(
            agent_id=agent_id
        )

        crew_builder.add_task(
            task_id=task_id,
            agent=crew_builder.get_last_agent(),
            output_filename=output_filename
        )
        return crew_builder.build()




