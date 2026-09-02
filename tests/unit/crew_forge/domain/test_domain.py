"""
Unit tests for crew_forge.domain enums and models.
"""
import unittest
from unittest.mock import MagicMock
from amsha.crew_forge.domain.models.agent_data import AgentRequest
from amsha.crew_forge.domain.models.task_data import TaskRequest
from amsha.crew_forge.domain.models.crew_data import CrewData
from crewai import LLM


class TestDomain(unittest.TestCase):
    """Test cases for domain enums and models."""

    def test_agent_models(self):
        """Test AgentRequest model."""
        req = AgentRequest(role="Role", goal="Goal", backstory="Backstory")
        self.assertEqual(req.role, "Role")
        self.assertEqual(req.goal, "Goal")
        self.assertEqual(req.backstory, "Backstory")
        self.assertIsNone(req.usecase)

    def test_task_models(self):
        """Test TaskRequest model."""
        req = TaskRequest(name="Task", description="Desc", expected_output="Output")
        self.assertEqual(req.name, "Task")
        self.assertEqual(req.description, "Desc")
        self.assertEqual(req.expected_output, "Output")

    def test_crew_data_model(self):
        """Test CrewData model."""
        mock_llm = MagicMock(spec=LLM)
        data = CrewData(llm=mock_llm, module_name="Module", output_dir_path="/path")
        self.assertEqual(data.llm, mock_llm)
        self.assertEqual(data.module_name, "Module")
        self.assertEqual(data.output_dir_path, "/path")


if __name__ == '__main__':
    unittest.main()
