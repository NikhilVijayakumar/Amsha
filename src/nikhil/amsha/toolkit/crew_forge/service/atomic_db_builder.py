# src/nikhil/amsha/toolkit/crew_forge/service/atomic_db_builder.py
from typing import Optional

from crewai import Crew, Agent, Process

from nikhil.amsha.toolkit.crew_forge.domain.models.agent_data import AgentRequest
from nikhil.amsha.toolkit.crew_forge.domain.models.crew_data import CrewData
from nikhil.amsha.toolkit.crew_forge.domain.models.task_data import TaskRequest
from nikhil.amsha.toolkit.crew_forge.repo.interfaces.i_agent_repository import IAgentRepository
from nikhil.amsha.toolkit.crew_forge.repo.interfaces.i_task_repository import ITaskRepository
from nikhil.amsha.toolkit.crew_forge.service.crew_builder_service import CrewBuilderService


class AtomicDbBuilderService:

    def __init__(self,data: CrewData, agent_repo: IAgentRepository,task_repo: ITaskRepository):
        self.builder = None
        self.agent_repo: IAgentRepository = agent_repo
        self.task_repo: ITaskRepository = task_repo
        self.builder: CrewBuilderService = CrewBuilderService(data)


    def add_agent(self, agent_id: str,knowledge_sources=None, tools: list = None) :
        agent_details = self.agent_repo.get_agent_by_id(agent_id)
        if not agent_details:
            raise ValueError(f"Agent with ID '{agent_id}' not found.")

        details:AgentRequest = AgentRequest(role=agent_details.role,goal=agent_details.goal,backstory=agent_details.backstory)
        self.builder.add_agent(details,knowledge_sources,tools)

    def add_task(self, task_id: str, agent: Agent, output_filename: str = None,validation:bool=False) :
        task_details = self.task_repo.get_task_by_id(task_id)
        if not task_details:
            raise ValueError(f"Task with ID '{task_id}' not found.")
        details:TaskRequest = TaskRequest(name=task_details.name,description=task_details.description,expected_output=task_details.expected_output)
        self.builder.add_task(details, agent, output_filename,validation)

    def build(self, process: Process = Process.sequential,knowledge_sources=None) -> Crew:
        return self.builder.build(process,knowledge_sources)

    def get_last_agent(self) -> Optional[Agent]:
        return self.builder.get_last_agent()

    def get_last_file(self) -> Optional[str]:
        return self.builder.get_last_file()
