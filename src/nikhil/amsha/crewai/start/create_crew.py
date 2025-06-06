import json
import os
import time

from crewai import Crew, Agent, Process, Task

from nikhil.amsha.crewai.model.crew_data import CrewData


class CreateCrew:

    def __init__(self,data:CrewData):
        self.llm = data.llm
        self.agent_repo = data.agent_repo
        self.task_repo = data.task_repo
        self.agents = []
        self.tasks = []
        self.output_dir_path = data.output_dir_path
        self.module_name = data.module_name
        self.timestamp = time.strftime("%Y%m%d%H%M%S")
        self.output_dir = os.path.join(
            f"{self.output_dir_path}/output/intermediate/{self.module_name}/output_{self.timestamp}/")
        self.create_output_dir()

    def create_output_dir(self):
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def get_output_dir(self):
        return self.output_dir

    def crew_with_knowledge(self, process=Process.sequential, knowledge_sources=None):
        crew = Crew(agents=self.agents,
                    tasks=self.tasks,
                    process=process,
                    verbose=True)
        if knowledge_sources:
            crew.knowledge_sources = knowledge_sources
        return crew

    def get_agent(self, agent_id: str):
        """Retrieves an agent by its ID."""
        return self.agent_repo.get_agent_by_id(agent_id)

    def get_task(self, task_id: str):
        """Retrieves a task by its ID."""
        return self.task_repo.get_task_by_id(task_id)



    def create_agent(self, agent_id: str, knowledge_sources=None,tools=None):
        """Retrieves an agent by its ID."""
        agent_details = self.get_agent(agent_id)
        agent = Agent(
            role=agent_details.role,
            goal=agent_details.goal,
            backstory=agent_details.backstory,
            llm=self.llm)
        if knowledge_sources:
            agent.knowledge_sources = knowledge_sources
        if tools:
            agent.tools=tools
        self.agents.append(agent)
        return agent

    def create_task(self, task_id: str, agent: Agent,save=True,filename=None):
        """Retrieves an agent by its ID."""
        task_details = self.get_task(task_id)
        task = Task(
            name=task_details.name,
            description=task_details.description,
            expected_output=task_details.expected_output,
            agent=agent
        )
        if save:
            if filename is None:
                filename = task_details.name
            task.output_file=f"{self.get_output_dir()}{filename}.json"
        self.tasks.append(task)

    @staticmethod
    def load_json(file_name):
        with open(file_name, 'r', encoding='utf8') as file:
            return json.load(file)