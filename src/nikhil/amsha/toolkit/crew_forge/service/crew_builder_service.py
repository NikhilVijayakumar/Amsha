# src/nikhil/amsha/toolkit/crew_forge/service/crew_builder_service.py
import os
import time
from typing import Optional

from crewai import Crew, Agent, Process, Task

from nikhil.amsha.toolkit.crew_forge.domain.models.crew_data import CrewData
from nikhil.amsha.toolkit.crew_forge.repo.interfaces.i_agent_repository import IAgentRepository
from nikhil.amsha.toolkit.crew_forge.repo.interfaces.i_task_repository import ITaskRepository


class CrewBuilderService:

    def __init__(self, data: CrewData, agent_repo: IAgentRepository, task_repo: ITaskRepository):
        self.llm = data.llm
        self.output_dir_path = data.output_dir_path
        self.module_name = data.module_name
        self.agent_repo: IAgentRepository = agent_repo
        self.task_repo: ITaskRepository = task_repo
        self._agents = []
        self._tasks = []
        self.output_files = []

        timestamp = time.strftime("%Y%m%d%H%M%S")
        self.output_dir = os.path.join(
            f"{self.output_dir_path}/output/{self.module_name}/output_{timestamp}/")
        self._create_output_dir()

    def _create_output_dir(self):
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def add_agent(self, agent_id: str,knowledge_sources=None, tools: list = None) -> 'CrewBuilderService':
        agent_details = self.agent_repo.get_agent_by_id(agent_id)
        if not agent_details:
            raise ValueError(f"Agent with ID '{agent_id}' not found.")

        agent = Agent(
            role=agent_details.role,
            goal=agent_details.goal,
            backstory=agent_details.backstory,
            llm=self.llm,
            tools=tools or []
        )
        if knowledge_sources:
            agent.knowledge_sources = knowledge_sources

        self._agents.append(agent)
        return self

    def add_task(self, task_id: str, agent: Agent, output_filename: str = None,validation:bool=False) -> 'CrewBuilderService':
        task_details = self.task_repo.get_task_by_id(task_id)
        if not task_details:
            raise ValueError(f"Task with ID '{task_id}' not found.")

        task = Task(
            name=task_details.name,
            description=task_details.description,
            expected_output=task_details.expected_output,
            agent=agent
        )
        if output_filename:
            if validation:
                output_file = output_filename
            else:
                output_file = os.path.join(self.output_dir, f"{output_filename}.json")
            self.output_files.append(output_file)
            task.output_file = output_file

        self._tasks.append(task)
        return self

    def build(self, process: Process = Process.sequential,knowledge_sources=None) -> Crew:
        if not self._agents or not self._tasks:
            raise ValueError("A crew must have at least one agent and one task.")

        crew= Crew(
            agents=self._agents,
            tasks=self._tasks,
            process=process,
            verbose=True
        )
        if knowledge_sources:
            crew.knowledge_sources = knowledge_sources
        return crew

    def get_last_agent(self) -> Optional[Agent]:
        """
        Returns the most recently added agent, or None if no agents have been added. 🧑‍✈️
        """
        return self._agents[-1] if self._agents else None

    def get_last_file(self) -> Optional[str]:
        """
        Returns the most recently added output files, or None if no output files have been added. 🧑‍✈
        """
        return self.output_files[-1] if self.output_files else None
