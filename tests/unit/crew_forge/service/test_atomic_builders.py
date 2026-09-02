"""
Unit tests for atomic builder services.
"""
import unittest
from unittest.mock import MagicMock, patch
from crewai import Agent
from amsha.crew_forge.service.atomic_yaml_builder import AtomicYamlBuilderService
from amsha.crew_forge.domain.models.crew_data import CrewData
from amsha.crew_forge.seeding.parser.crew_parser import CrewParser


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
