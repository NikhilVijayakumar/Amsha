import yaml


import re

from src.bavans.amsha.model.agent_data import AgentRequest
from src.bavans.amsha.model.task_data import TaskRequest


class YamlUtils:

    def __init__(self):
        self.task = None
        self.agent = None

    @staticmethod
    def clean_multiline_string(text: str) -> str:
        # Replace newlines and tabs with a space, collapse multiple spaces
        cleaned = re.sub(r'[\n\t]+', ' ', text)
        cleaned = re.sub(r'\s{2,}', ' ', cleaned)
        return cleaned.strip()

    def parse_agent(self,agent_yaml_file: str):
        with open(agent_yaml_file, 'r') as file:
            config = yaml.safe_load(file)

        self.agent = AgentRequest(
            role=config['agent']['role'],
            goal=YamlUtils.clean_multiline_string(config['agent']['goal']),
            backstory=YamlUtils.clean_multiline_string(config['agent']['backstory']),
        )

        return self.agent

    def parse_task(self,task_yaml_file: str):
        with open(task_yaml_file, 'r') as file:
            config = yaml.safe_load(file)

        self.task = TaskRequest(
            name=config['task']['name'],
            description=YamlUtils.clean_multiline_string(config['task']['description']),
            expected_output=YamlUtils.clean_multiline_string(config['task']['expected_output'])
        )
        return self.task

