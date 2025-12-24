"""
Unit tests for crew_forge.seeding module.
"""
import unittest
from unittest.mock import MagicMock, patch, mock_open
import os
from amsha.crew_forge.seeding.database_seeder import DatabaseSeeder
from amsha.crew_forge.seeding.parser.crew_parser import CrewParser
from amsha.crew_forge.domain.models.agent_data import AgentRequest, AgentResponse
from amsha.crew_forge.domain.models.task_data import TaskRequest, TaskResponse
from amsha.crew_forge.domain.models.crew_config_data import CrewConfigRequest, CrewConfigResponse
from amsha.crew_forge.repo.interfaces.i_agent_repository import IAgentRepository
from amsha.crew_forge.repo.interfaces.i_task_repository import ITaskRepository
from amsha.crew_forge.repo.interfaces.i_crew_config_repository import ICrewConfigRepository


class TestCrewParser(unittest.TestCase):
    """Test cases for CrewParser."""

    def setUp(self):
        self.parser = CrewParser()

    def test_clean_multiline_string(self):
        """Test cleaning of multiline strings."""
        text = "  Line 1\n\tLine 2   \n  Line 3  "
        cleaned = self.parser.clean_multiline_string(text)
        self.assertEqual(cleaned, "Line 1 Line 2 Line 3")

    @patch('amsha.utils.yaml_utils.YamlUtils.yaml_safe_load')
    def test_parse_agent(self, mock_load):
        """Test parsing agent YAML."""
        mock_load.return_value = {
            'agent': {
                'role': 'Role',
                'goal': 'Goal\nwith newline',
                'backstory': 'Backstory\twith tab'
            }
        }
        res = self.parser.parse_agent("agent.yaml")
        self.assertEqual(res.role, "Role")
        self.assertEqual(res.goal, "Goal with newline")
        self.assertEqual(res.backstory, "Backstory with tab")

    @patch('amsha.utils.yaml_utils.YamlUtils.yaml_safe_load')
    def test_parse_task(self, mock_load):
        """Test parsing task YAML."""
        mock_load.return_value = {
            'task': {
                'name': 'Name',
                'description': 'Desc\nwith newline',
                'expected_output': 'Output\twith tab'
            }
        }
        res = self.parser.parse_task("task.yaml")
        self.assertEqual(res.name, "Name")
        self.assertEqual(res.description, "Desc with newline")
        self.assertEqual(res.expected_output, "Output with tab")


class TestDatabaseSeeder(unittest.TestCase):
    """Test cases for DatabaseSeeder."""

    def setUp(self):
        self.mock_agent_repo = MagicMock(spec=IAgentRepository)
        self.mock_task_repo = MagicMock(spec=ITaskRepository)
        self.mock_crew_repo = MagicMock(spec=ICrewConfigRepository)
        self.seeder = DatabaseSeeder(self.mock_agent_repo, self.mock_task_repo, self.mock_crew_repo)

    @patch('os.path.isdir')
    @patch('logging.error')
    def test_synchronize_invalid_path(self, mock_log_error, mock_isdir):
        """Test synchronize with invalid path."""
        mock_isdir.return_value = False
        self.seeder.synchronize("/invalid")
        mock_log_error.assert_called()

    @patch('os.walk')
    @patch('amsha.crew_forge.seeding.parser.crew_parser.CrewParser.parse_agent')
    @patch('amsha.crew_forge.seeding.parser.crew_parser.CrewParser.parse_task')
    def test_collect_configs_from_path(self, mock_parse_task, mock_parse_agent, mock_walk):
        """Test collecting configs from path."""
        mock_walk.return_value = [
            ('/root', ['usecase1'], []),
            ('/root/usecase1', ['agents', 'tasks'], []),
            ('/root/usecase1/agents', [], ['agent1.yaml']),
            ('/root/usecase1/tasks', [], ['task1.yaml']),
        ]
        mock_parse_agent.return_value = AgentRequest(role="R", goal="G", backstory="B")
        mock_parse_task.return_value = TaskRequest(name="T", description="D", expected_output="O")

        res = self.seeder._collect_configs_from_path("/root")
        self.assertIn("usecase1", res)
        self.assertEqual(len(res["usecase1"]["agents"]), 1)
        self.assertEqual(len(res["usecase1"]["tasks"]), 1)
        self.assertEqual(res["usecase1"]["agents"][0]["key"], "agent1")

    def test_synchronize_agents(self):
        """Test synchronizing agents."""
        agent_req = AgentRequest(role="R", goal="G", backstory="B", usecase="U")
        agent_configs = [{"key": "agent1", "data": agent_req}]
        
        # Case 1: New agent
        self.mock_agent_repo.find_by_role_and_usecase.return_value = None
        self.mock_agent_repo.create_agent.return_value = AgentResponse(_id="123", role="R", goal="G", backstory="B")
        
        id_map = self.seeder._synchronize_agents("U", agent_configs)
        self.assertEqual(id_map["agent1"], "123")
        self.mock_agent_repo.create_agent.assert_called()

        # Case 2: Existing agent, updated
        existing_agent = AgentResponse(_id="123", role="R", goal="Old G", backstory="B")
        self.mock_agent_repo.find_by_role_and_usecase.return_value = existing_agent
        
        id_map = self.seeder._synchronize_agents("U", agent_configs)
        self.assertEqual(id_map["agent1"], "123")
        self.mock_agent_repo.update_agent.assert_called()

        # Case 3: Existing agent, unchanged
        existing_agent.goal = "G"
        id_map = self.seeder._synchronize_agents("U", agent_configs)
        self.assertEqual(id_map["agent1"], "123")

        # Case 4: Exception
        self.mock_agent_repo.find_by_role_and_usecase.side_effect = Exception("Error")
        with patch('logging.error') as mock_log:
            id_map = self.seeder._synchronize_agents("U", agent_configs)
            mock_log.assert_called()
        self.mock_agent_repo.find_by_role_and_usecase.side_effect = None

    def test_synchronize_tasks(self):
        """Test synchronizing tasks."""
        task_req = TaskRequest(name="T", description="D", expected_output="O", usecase="U")
        task_configs = [{"key": "task1", "data": task_req}]
        
        # Case 1: New task
        self.mock_task_repo.find_by_name_and_usecase.return_value = None
        self.mock_task_repo.create_task.return_value = TaskResponse(_id="456", name="T", description="D", expected_output="O")
        
        id_map = self.seeder._synchronize_tasks("U", task_configs)
        self.assertEqual(id_map["task1"], "456")
        self.mock_task_repo.create_task.assert_called()

        # Case 2: Existing task, updated
        existing_task = TaskResponse(_id="456", name="T", description="Old D", expected_output="O")
        self.mock_task_repo.find_by_name_and_usecase.return_value = existing_task
        
        id_map = self.seeder._synchronize_tasks("U", task_configs)
        self.assertEqual(id_map["task1"], "456")
        self.mock_task_repo.update_task.assert_called()

        # Case 3: Existing task, unchanged
        existing_task.description = "D"
        id_map = self.seeder._synchronize_tasks("U", task_configs)
        self.assertEqual(id_map["task1"], "456")

        # Case 4: Exception
        self.mock_task_repo.find_by_name_and_usecase.side_effect = Exception("Error")
        with patch('logging.error') as mock_log:
            id_map = self.seeder._synchronize_tasks("U", task_configs)
            mock_log.assert_called()
        self.mock_task_repo.find_by_name_and_usecase.side_effect = None

    def test_synchronize_crew(self):
        """Test synchronizing crew."""
        agent_id_map = {"a1": "id1"}
        task_id_map = {"t1": "id2"}
        
        # Case 1: New crew
        self.mock_crew_repo.get_crew_by_name_and_usecase.return_value = None
        self.seeder._synchronize_crew("usecase_1", agent_id_map, task_id_map)
        self.mock_crew_repo.create_crew_config.assert_called()

        # Case 2: Existing crew, updated
        existing_crew = CrewConfigResponse(_id="789", name="Usecase 1 Crew", agents={}, tasks={})
        self.mock_crew_repo.get_crew_by_name_and_usecase.return_value = existing_crew
        self.seeder._synchronize_crew("usecase_1", agent_id_map, task_id_map)
        self.mock_crew_repo.update_crew_config.assert_called()

        # Case 3: Existing crew, unchanged
        existing_crew.agents = agent_id_map
        existing_crew.tasks = task_id_map
        self.seeder._synchronize_crew("usecase_1", agent_id_map, task_id_map)

        # Case 4: Exception
        self.mock_crew_repo.get_crew_by_name_and_usecase.side_effect = Exception("Error")
        with patch('logging.error') as mock_log:
            self.seeder._synchronize_crew("usecase_1", agent_id_map, task_id_map)
            mock_log.assert_called()
        self.mock_crew_repo.get_crew_by_name_and_usecase.side_effect = None

    def test_process_usecases(self):
        """Test processing usecases."""
        usecase_map = {
            "u1": {
                "agents": [{"key": "a1", "data": AgentRequest(role="R", goal="G", backstory="B")}],
                "tasks": [{"key": "t1", "data": TaskRequest(name="T", description="D", expected_output="O")}]
            }
        }
        with patch.object(self.seeder, '_synchronize_agents') as mock_sync_agents, \
             patch.object(self.seeder, '_synchronize_tasks') as mock_sync_tasks, \
             patch.object(self.seeder, '_synchronize_crew') as mock_sync_crew:
            
            mock_sync_agents.return_value = {"a1": "id1"}
            mock_sync_tasks.return_value = {"t1": "id2"}
            
            self.seeder._process_usecases(usecase_map)
            mock_sync_agents.assert_called()
            mock_sync_tasks.assert_called()
            mock_sync_crew.assert_called_with("u1", {"a1": "id1"}, {"t1": "id2"})

    @patch('os.path.isdir')
    @patch('amsha.crew_forge.seeding.database_seeder.DatabaseSeeder._collect_configs_from_path')
    @patch('amsha.crew_forge.seeding.database_seeder.DatabaseSeeder._process_usecases')
    def test_synchronize_full_flow(self, mock_process, mock_collect, mock_isdir):
        """Test full synchronize flow."""
        mock_isdir.return_value = True
        mock_collect.return_value = {"u1": {"agents": [], "tasks": []}}
        
        self.seeder.synchronize("/root")
        mock_process.assert_called_with(mock_collect.return_value)
        
        # Empty map
        mock_collect.return_value = {}
        with patch('logging.warning') as mock_warn:
            self.seeder.synchronize("/root")
            mock_warn.assert_called_with("No use cases found to process.")


if __name__ == '__main__':
    unittest.main()
