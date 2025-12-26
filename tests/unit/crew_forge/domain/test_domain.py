"""
Unit tests for crew_forge.domain enums and models.
"""
import unittest
from unittest.mock import MagicMock
from amsha.crew_forge.domain.enum.repo_backend import RepoBackend
from amsha.crew_forge.domain.models.agent_data import AgentRequest, AgentResponse
from amsha.crew_forge.domain.models.task_data import TaskRequest, TaskResponse
from amsha.crew_forge.domain.models.crew_config_data import CrewConfigRequest, CrewConfigResponse
from amsha.crew_forge.domain.models.crew_data import CrewData
from amsha.crew_forge.domain.models.repo_data import RepoData
from amsha.crew_forge.domain.models.sync_config import SyncConfigData
from amsha.crew_forge.repo.interfaces.i_agent_repository import IAgentRepository
from amsha.crew_forge.repo.interfaces.i_task_repository import ITaskRepository
from amsha.crew_forge.repo.interfaces.i_crew_config_repository import ICrewConfigRepository
from crewai import LLM


class TestDomain(unittest.TestCase):
    """Test cases for domain enums and models."""

    def test_repo_backend_enum(self):
        """Test RepoBackend enum members and values."""
        self.assertEqual(RepoBackend.MONGO, "mongo")
        self.assertEqual(RepoBackend.IN_MEMORY, "in_memory")
        self.assertEqual(RepoBackend.COSMOS, "cosmos")
        self.assertEqual(len(RepoBackend), 3)

    def test_agent_models(self):
        """Test AgentRequest and AgentResponse models."""
        # AgentRequest
        req = AgentRequest(role="Role", goal="Goal", backstory="Backstory")
        self.assertEqual(req.role, "Role")
        self.assertEqual(req.goal, "Goal")
        self.assertEqual(req.backstory, "Backstory")
        self.assertIsNone(req.usecase)

        # AgentResponse
        res = AgentResponse(_id="123", role="Role", goal="Goal", backstory="Backstory")
        self.assertEqual(res.id, "123")
        self.assertEqual(res.role, "Role")
        
        # Test with alias
        res_alias = AgentResponse(id="456", role="Role", goal="Goal", backstory="Backstory")
        # Pydantic v2 handles id/alias differently depending on config, 
        # but here it's defined as id: Optional[str] = Field(None, alias="_id")
        # So it expects _id in input if not using populate_by_name
        res_dict = AgentResponse.model_validate({"_id": "789", "role": "R", "goal": "G", "backstory": "B"})
        self.assertEqual(res_dict.id, "789")

    def test_task_models(self):
        """Test TaskRequest and TaskResponse models."""
        # TaskRequest
        req = TaskRequest(name="Task", description="Desc", expected_output="Output")
        self.assertEqual(req.name, "Task")
        self.assertEqual(req.description, "Desc")
        self.assertEqual(req.expected_output, "Output")

        # TaskResponse
        res = TaskResponse(_id="123", name="Task", description="Desc", expected_output="Output")
        self.assertEqual(res.id, "123")

    def test_crew_config_models(self):
        """Test CrewConfigRequest and CrewConfigResponse models."""
        agents = {"agent1": "id1"}
        tasks = {"task1": "id1"}
        
        # CrewConfigRequest
        req = CrewConfigRequest(name="Crew", agents=agents, tasks=tasks)
        self.assertEqual(req.name, "Crew")
        self.assertEqual(req.agents, agents)
        self.assertEqual(req.tasks, tasks)

        # CrewConfigResponse
        res = CrewConfigResponse(_id="123", name="Crew", agents=agents, tasks=tasks)
        self.assertEqual(res.id, "123")

    def test_crew_data_model(self):
        """Test CrewData model."""
        mock_llm = MagicMock(spec=LLM)
        data = CrewData(llm=mock_llm, module_name="Module", output_dir_path="/path")
        self.assertEqual(data.llm, mock_llm)
        self.assertEqual(data.module_name, "Module")
        self.assertEqual(data.output_dir_path, "/path")

    def test_repo_data_model(self):
        """Test RepoData model."""
        data = RepoData(mongo_uri="uri", db_name="db", collection_name="coll")
        self.assertEqual(data.mongo_uri, "uri")
        self.assertEqual(data.db_name, "db")
        self.assertEqual(data.collection_name, "coll")

    def test_sync_config_data_model(self):
        """Test SyncConfigData model."""
        mock_agent_repo = MagicMock(spec=IAgentRepository)
        mock_task_repo = MagicMock(spec=ITaskRepository)
        mock_crew_repo = MagicMock(spec=ICrewConfigRepository)
        
        data = SyncConfigData(
            agent_repo=mock_agent_repo,
            task_repo=mock_task_repo,
            crew_repo=mock_crew_repo,
            domain_root_path="/root"
        )
        self.assertEqual(data.agent_repo, mock_agent_repo)
        self.assertEqual(data.task_repo, mock_task_repo)
        self.assertEqual(data.crew_repo, mock_crew_repo)
        self.assertEqual(data.domain_root_path, "/root")


if __name__ == '__main__':
    unittest.main()
