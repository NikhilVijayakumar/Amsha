import yaml
import re

from nikhil.amsha.crewai.model import AgentRequest
from nikhil.amsha.crewai.model import TaskRequest


class YamlUtils:

    def __init__(self):
        self.task = None
        self.agent = None
        self.llm_config = None

    @staticmethod
    def clean_multiline_string(text: str) -> str:
        cleaned = re.sub(r'[\n\t]+', ' ', text)
        cleaned = re.sub(r'\s{2,}', ' ', cleaned)
        return cleaned.strip()

    @staticmethod
    def yaml_safe_load(config_file_path:str):
        with open(config_file_path, "r") as file:
            return yaml.safe_load(file)

    def parse_agent(self, agent_yaml_file: str):
        config = YamlUtils.yaml_safe_load(agent_yaml_file)
        self.agent = AgentRequest(
            role=config['agent']['role'],
            goal=self.clean_multiline_string(config['agent']['goal']),
            backstory=self.clean_multiline_string(config['agent']['backstory']),
        )
        return self.agent

    def parse_task(self, task_yaml_file: str):
        config = YamlUtils.yaml_safe_load(task_yaml_file)
        self.task = TaskRequest(
            name=config['task']['name'],
            description=self.clean_multiline_string(config['task']['description']),
            expected_output=self.clean_multiline_string(config['task']['expected_output'])
        )
        return self.task

    def load_llm_config(self, llm_yaml_path: str):
        self.llm_config = YamlUtils.yaml_safe_load(llm_yaml_path)
        return self.llm_config

    def get_llm_settings(self, use_case: str, model_key: str = None):
        if self.llm_config is None:
            raise ValueError("LLM config not loaded. Call load_llm_config first.")

        use_case_config = self.llm_config['llm'].get(use_case)
        if not use_case_config:
            raise ValueError(f"Use case '{use_case}' not found in YAML config.")

        model_key = model_key or use_case_config['default']
        model_config = use_case_config['models'].get(model_key)
        if not model_config:
            raise ValueError(f"Model '{model_key}' not found under '{use_case}' use case.")

        params = self.llm_config['llm_parameters'].get(use_case, {})
        return model_config, params