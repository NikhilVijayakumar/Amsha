"""
Unit tests for atomic builder services.
"""
import unittest
from unittest.mock import MagicMock, patch
from crewai import Agent, Process
from amsha.crew_forge.service.atomic_db_builder import AtomicDbBuilderService
from amsha.crew_forge.service.atomic_yaml_builder import AtomicYamlBuilderService
from amsha.crew_forge.domain.models.crew_data import CrewData
from amsha.crew_forge.domain.models.agent_data import AgentResponse
from amsha.crew_forge.domain.models.task_data import TaskResponse
from amsha.crew_forge.repo.interfaces.i_agent_repository import IAgentRepository
from amsha.crew_forge.repo.interfaces.i_task_repository import ITaskRepository
from amsha.crew_forge.seeding.parser.crew_parser import CrewParser


class TestAtomicDbBuilderService(unittest.TestCase):
    """Test cases for AtomicDbBuilderService."""

    def setUp(self):
        self.mock_data = MagicMock(spec=CrewData)
        self.mock_data.llm = MagicMock()
        self.mock_data.module_name = "test_module"
        self.mock_data.output_dir_path = "/tmp"
        self.mock_agent_repo = MagicMock(spec=IAgentRepository)
        self.mock_task_repo = MagicMock(spec=ITaskRepository)
        with patch('amsha.crew_forge.service.crew_builder_service.CrewBuilderService') as mock_builder_class:
            self.service = AtomicDbBuilderService(self.mock_data, self.mock_agent_repo, self.mock_task_repo)
            self.service.builder = mock_builder_class.return_value

    def test_add_agent(self):
        """Test adding agent by ID."""
        # Success
        self.mock_agent_repo.get_agent_by_id.return_value = AgentResponse(_id="1", role="R", goal="G", backstory="B")
        self.service.add_agent("1")
        self.service.builder.add_agent.assert_called()

        # Failure
        self.mock_agent_repo.get_agent_by_id.return_value = None
        with self.assertRaises(ValueError):
            self.service.add_agent("invalid")

    def test_add_task(self):
        """Test adding task by ID."""
        mock_agent = MagicMock(spec=Agent)
        # Success
        self.mock_task_repo.get_task_by_id.return_value = TaskResponse(_id="1", name="T", description="D", expected_output="O")
        self.service.add_task("1", mock_agent)
        self.service.builder.add_task.assert_called()

        # Failure
        self.mock_task_repo.get_task_by_id.return_value = None
        with self.assertRaises(ValueError):
            self.service.add_task("invalid", mock_agent)

    def test_build(self):
        """Test build method."""
        self.service.build(Process.sequential)
        self.service.builder.build.assert_called_with(Process.sequential, None)

    def test_get_last_agent_file(self):
        """Test retrieval of last agent and file."""
        self.service.get_last_agent()
        self.service.builder.get_last_agent.assert_called()
        self.service.get_last_file()
        self.service.builder.get_last_file.assert_called()


class TestAtomicYamlBuilderService(unittest.TestCase):
    """Test cases for AtomicYamlBuilderService."""

    def setUp(self):
        self.mock_data = MagicMock(spec=CrewData)
        self.mock_data.llm = MagicMock()
        self.mock_data.module_name = "test_module"
        self.mock_data.output_dir_path = "/tmp"
        self.mock_parser = MagicMock(spec=CrewParser)
        with patch('amsha.crew_forge.service.crew_builder_service.CrewBuilderService') as mock_builder_class:
            self.service = AtomicYamlBuilderService(self.mock_data, self.mock_parser, "agent.yaml", "task.yaml")
            self.service.builder = mock_builder_class.return_value

    def test_add_agent(self):
        """Test adding agent from YAML."""
        # Success
        self.mock_parser.parse_agent.return_value = MagicMock()
        self.service.add_agent()
        self.service.builder.add_agent.assert_called()

        # Failure
        self.mock_parser.parse_agent.return_value = None
        with self.assertRaises(ValueError):
            self.service.add_agent()

    def test_add_task(self):
        """Test adding task from YAML."""
        mock_agent = MagicMock(spec=Agent)
        # Success
        self.mock_parser.parse_task.return_value = MagicMock()
        self.service.add_task(mock_agent)
        self.service.builder.add_task.assert_called()

        # Failure
        self.mock_parser.parse_task.return_value = None
        with self.assertRaises(ValueError):
            self.service.add_task(mock_agent)

    def test_build(self):
        """Test build method."""
        self.service.build()
        self.service.builder.build.assert_called()

    def test_get_last_agent_file(self):
        """Test retrieval of last agent and file."""
        self.service.get_last_agent()
        self.service.builder.get_last_agent.assert_called()
        self.service.get_last_file()
        self.service.builder.get_last_file.assert_called()


if __name__ == '__main__':
    unittest.main()
