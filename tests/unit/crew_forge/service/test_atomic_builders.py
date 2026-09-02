"""
Unit tests for atomic builder services.
"""
import unittest
import tempfile
from pathlib import Path
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
        self.mock_data.memory = False
        self.mock_data.checkpoint = None
        self.mock_data.tracing = None
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


class TestAtomicYamlBuilderServiceSkills(unittest.TestCase):
    """Test skill-name resolution in AtomicYamlBuilderService."""

    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self.root = Path(self._tmpdir.name)
        self.skills_root = self.root / "skills"
        (self.skills_root / "domain-skills").mkdir(parents=True)
        self.mock_data = MagicMock(spec=CrewData)
        self.mock_data.llm = MagicMock()
        self.mock_data.module_name = "test_module"
        self.mock_data.output_dir_path = "/tmp"
        self.mock_data.memory = False
        self.mock_data.checkpoint = None
        self.mock_data.tracing = None
        self.mock_parser = MagicMock(spec=CrewParser)

    def tearDown(self):
        self._tmpdir.cleanup()

    def _service(self, skills_root):
        with patch('amsha.crew_forge.service.crew_builder_service.CrewBuilderService') as mock_builder_class:
            service = AtomicYamlBuilderService(
                self.mock_data, self.mock_parser, "agent.yaml", "task.yaml",
                skills_root=str(skills_root),
            )
            service.builder = mock_builder_class.return_value
            return service, mock_builder_class.return_value

    def test_resolves_skill_name_to_search_path(self):
        mock_details = MagicMock()
        mock_details.skills = ["domain-skills"]
        self.mock_parser.parse_agent.return_value = mock_details
        service, builder = self._service(self.skills_root)
        service.add_agent()
        self.assertEqual(
            mock_details.skills,
            [str(self.skills_root / "domain-skills")],
        )
        builder.add_agent.assert_called_once()

    def test_keeps_existing_path_skill_unchanged(self):
        existing = self.root / "custom-skills"
        existing.mkdir()
        mock_details = MagicMock()
        mock_details.skills = [str(existing)]
        self.mock_parser.parse_agent.return_value = mock_details
        service, _ = self._service(self.skills_root)
        service.add_agent()
        self.assertEqual(mock_details.skills, [str(existing)])

    def test_unknown_skill_name_raises(self):
        mock_details = MagicMock()
        mock_details.skills = ["missing-skill"]
        self.mock_parser.parse_agent.return_value = mock_details
        service, _ = self._service(self.skills_root)
        with self.assertRaises(ValueError):
            service.add_agent()

    def test_skills_untouched_without_skills_root(self):
        mock_details = MagicMock()
        mock_details.skills = ["domain-skills"]
        self.mock_parser.parse_agent.return_value = mock_details
        with patch('amsha.crew_forge.service.crew_builder_service.CrewBuilderService') as mock_builder_class:
            service = AtomicYamlBuilderService(self.mock_data, self.mock_parser, "agent.yaml", "task.yaml")
            service.builder = mock_builder_class.return_value
        service.add_agent()
        self.assertEqual(mock_details.skills, ["domain-skills"])


if __name__ == '__main__':
    unittest.main()
