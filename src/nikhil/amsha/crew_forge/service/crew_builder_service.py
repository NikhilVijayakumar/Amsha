# src/nikhil/amsha/toolkit/crew_forge/service/crew_builder_service.py
import os
import time
import typing
from typing import Optional
from amsha.common.logger import get_logger

from crewai import Crew, Agent, Process, Task

from amsha.crew_forge.domain.models.agent_data import AgentRequest
from amsha.crew_forge.domain.models.crew_data import CrewData
from amsha.crew_forge.domain.models.task_data import TaskRequest


class CrewBuilderService:

    def __init__(self, data: CrewData):
        self.logger = get_logger("crew_forge.builder")
        self.llm = data.llm
        self.module_name = data.module_name
        if data.output_dir_path:
            timestamp = time.strftime("%Y%m%d%H%M%S")
            self.output_dir_path = data.output_dir_path
            self.output_dir = os.path.join(
                f"{self.output_dir_path}/output/{self.module_name}/output_{timestamp}/")
            self._create_output_dir()
        self._agents = []
        self._tasks = []
        self.output_files = []




    def _create_output_dir(self):
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def add_agent(self, agent_details: AgentRequest,knowledge_sources=None, tools: list = None) -> 'CrewBuilderService':

        if not agent_details:
            self._agents.append(agent_details)

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

    def add_task(self, task_details: TaskRequest, agent: Agent, output_filename: str = None,
                 validation:bool=False, output_json: typing.Any = None) -> 'CrewBuilderService':
        self.logger.debug("Building crew task", extra={
            "output_filename": output_filename
        })

        if not task_details:
            raise ValueError(f"Task with name '{task_details.name}' not found.")

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

        if output_json:
            task.output_json = output_json


        self._tasks.append(task)
        return self

    def build(self, process: Process = Process.sequential,knowledge_sources=None) -> Crew:
        if not self._agents or not self._tasks:
            raise ValueError("A crew must have at least one agent and one task.")

        # CrewAI 1.8.0: stream=True causes immediate return with streaming output object
        # Remove it to allow normal execution
        crew= Crew(
            agents=self._agents,
            tasks=self._tasks,
            process=process,
            verbose=True,
            stream=True
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
