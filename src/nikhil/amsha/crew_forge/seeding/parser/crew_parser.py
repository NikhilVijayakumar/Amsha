import re

from amsha.crew_forge.domain.models.agent_data import AgentRequest
from amsha.crew_forge.domain.models.task_data import TaskRequest
from amsha.utils.yaml_utils import YamlUtils


class CrewParser:

    @staticmethod
    def clean_multiline_string(text: str) -> str:
        cleaned = re.sub(r'[\n\t]+', ' ', text)
        cleaned = re.sub(r'\s{2,}', ' ', cleaned)
        return cleaned.strip()

    def parse_agent(self, agent_yaml_file: str) -> AgentRequest:
        config = YamlUtils.yaml_safe_load(agent_yaml_file)
        data = config['agent']
        kwargs = {
            'role': data['role'],
            'goal': self.clean_multiline_string(data['goal']),
            'backstory': self.clean_multiline_string(data['backstory']),
        }
        kwargs.update(self._pass_through_fields(data, AgentRequest, {'role', 'goal', 'backstory'}))
        return AgentRequest(**kwargs)

    def parse_task(self, task_yaml_file: str) -> TaskRequest:
        config = YamlUtils.yaml_safe_load(task_yaml_file)
        data = config['task']
        kwargs = {
            'name': data['name'],
            'description': self.clean_multiline_string(data['description']),
            'expected_output': self.clean_multiline_string(data['expected_output']),
        }
        kwargs.update(self._pass_through_fields(data, TaskRequest, {'name', 'description', 'expected_output'}))
        return TaskRequest(**kwargs)

    @staticmethod
    def _pass_through_fields(data: dict, model, handled: set) -> dict:
        """Copy any YAML keys that match declared optional model fields, preserving truthy values."""
        extras = {}
        for field in model.model_fields:
            if field in handled or field not in data:
                continue
            value = data[field]
            if value is not None:
                extras[field] = value
        return extras
