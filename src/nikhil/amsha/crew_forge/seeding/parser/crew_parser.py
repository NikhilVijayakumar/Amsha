import re

from nikhil.amsha.crew_forge.domain.models.agent_data import AgentRequest
from nikhil.amsha.crew_forge.domain.models.task_data import TaskRequest
from nikhil.vak.utils.yaml_utils import YamlUtils


class CrewParser:

    @staticmethod
    def clean_multiline_string(text: str) -> str:
        cleaned = re.sub(r'[\n\t]+', ' ', text)
        cleaned = re.sub(r'\s{2,}', ' ', cleaned)
        return cleaned.strip()

    def parse_agent(self, agent_yaml_file: str) -> AgentRequest:
        config = YamlUtils().yaml_safe_load(agent_yaml_file)
        return AgentRequest(
            role=config['agent']['role'],
            goal=self.clean_multiline_string(config['agent']['goal']),
            backstory=self.clean_multiline_string(config['agent']['backstory']),
        )

    def parse_task(self, task_yaml_file: str) -> TaskRequest:
        config = YamlUtils.yaml_safe_load(task_yaml_file)
        return TaskRequest(
            name=config['task']['name'],
            description=self.clean_multiline_string(config['task']['description']),
            expected_output=self.clean_multiline_string(config['task']['expected_output'])
        )
