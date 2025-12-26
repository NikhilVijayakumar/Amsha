# src/nikhil/amsha/toolkit/crew_forge/service/atomic_yaml_builder.py
from typing import Optional, Any

from crewai import Crew, Agent, Process

from amsha.crew_forge.domain.models.crew_data import CrewData
from amsha.crew_forge.seeding.parser.crew_parser import CrewParser
from amsha.crew_forge.service.crew_builder_service import CrewBuilderService


class AtomicYamlBuilderService:

    def __init__(self,data: CrewData,parser:CrewParser,agent_yaml_file:str,task_yaml_file:str):
        self.parser:CrewParser = parser
        self.agent_yaml_file:str =agent_yaml_file
        self.task_yaml_file:str = task_yaml_file
        self.builder:CrewBuilderService = CrewBuilderService(data)

    def add_agent(self,knowledge_sources=None, tools: list = None):
        agent_details = self.parser.parse_agent(self.agent_yaml_file)
        if not agent_details:
            raise ValueError(f"Agent file: '{self.agent_yaml_file}' not found.")
        self.builder.add_agent(agent_details, knowledge_sources, tools)

    def add_task(self, agent: Agent, output_filename: str = None,
                 validation:bool=False,output_json: Any = None):
        task_details = self.parser.parse_task(self.task_yaml_file)
        if not task_details:
            raise ValueError(f"Task file: '{self.task_yaml_file}' not found.")
        self.builder.add_task(task_details, agent, output_filename, validation,output_json)

    def build(self, process: Process = Process.sequential, knowledge_sources=None) -> Crew:
        return self.builder.build(process, knowledge_sources)

    def get_last_agent(self) -> Optional[Agent]:
        return self.builder.get_last_agent()

    def get_last_file(self) -> Optional[str]:
        return self.builder.get_last_file()
