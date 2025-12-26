"""
Unit tests for crew_forge.repo mongo-based repositories.
"""
import unittest
from unittest.mock import MagicMock, patch
from bson import ObjectId
from pymongo.errors import DuplicateKeyError

from amsha.crew_forge.domain.models.repo_data import RepoData
from amsha.crew_forge.domain.models.agent_data import AgentRequest, AgentResponse
from amsha.crew_forge.domain.models.task_data import TaskRequest, TaskResponse
from amsha.crew_forge.domain.models.crew_config_data import CrewConfigRequest, CrewConfigResponse
from amsha.crew_forge.repo.adapters.mongo.mongo_repository import MongoRepository
from amsha.crew_forge.repo.adapters.mongo.agent_repo import AgentRepository
from amsha.crew_forge.repo.adapters.mongo.task_repo import TaskRepository
from amsha.crew_forge.repo.adapters.mongo.crew_config_repo import CrewConfigRepository


VALID_ID = "507f1f77bcf86cd799439011"

class TestMongoRepositories(unittest.TestCase):
    """Test cases for mongo-based repositories."""

    def setUp(self):
        self.repo_data = RepoData(mongo_uri="mongodb://localhost:27017", db_name="test_db", collection_name="test_coll")
        
        # Patch MongoClient to avoid actual connections
        self.patcher = patch('pymongo.MongoClient')
        self.mock_client_class = self.patcher.start()
        self.mock_client = self.mock_client_class.return_value
        self.mock_db = MagicMock()
        self.mock_coll = MagicMock()
        
        self.mock_client.__getitem__.return_value = self.mock_db
        self.mock_db.__getitem__.return_value = self.mock_coll

    def tearDown(self):
        self.patcher.stop()

    def test_mongo_repository_base(self):
        """Test base MongoRepository methods."""
        repo = MongoRepository(self.repo_data)
        
        # find_one
        repo.find_one({"key": "val"})
        self.mock_coll.find_one.assert_called_with({"key": "val"})
        
        # find_many
        self.mock_coll.find.return_value = [{"a": 1}]
        res = repo.find_many({"key": "val"})
        self.assertEqual(res, [{"a": 1}])
        self.mock_coll.find.assert_called_with({"key": "val"})
        
        # insert_one
        repo.insert_one({"a": 1})
        self.mock_coll.insert_one.assert_called_with({"a": 1})
        
        # insert_many
        repo.insert_many([{"a": 1}])
        self.mock_coll.insert_many.assert_called_with([{"a": 1}])
        
        # update_one
        repo.update_one({"q": 1}, {"d": 2})
        self.mock_coll.update_one.assert_called_with({"q": 1}, {"$set": {"d": 2}})
        
        # delete_one
        repo.delete_one({"q": 1})
        self.mock_coll.delete_one.assert_called_with({"q": 1})
        
        # create_unique_compound_index
        repo.create_unique_compound_index(["a", "b"])
        self.mock_coll.create_index.assert_called()
        
        # Error case for index
        with patch('builtins.print') as mock_print:
            self.mock_coll.create_index.side_effect = Exception("Index Error")
            repo.create_unique_compound_index(["a"])
            mock_print.assert_any_call("Error creating unique compound index on ['a']: Index Error")
            
        # Empty keys for index
        with self.assertRaises(ValueError):
            repo.create_unique_compound_index([])

    def test_agent_repository(self):
        """Test AgentRepository methods."""
        repo = AgentRepository(self.repo_data)
        
        # create_agent
        req = AgentRequest(role="R", goal="G", backstory="B", usecase="U")
        mock_result = MagicMock()
        mock_result.inserted_id = ObjectId(VALID_ID)
        self.mock_coll.insert_one.return_value = mock_result
        self.mock_coll.find_one.return_value = {"_id": mock_result.inserted_id, "role": "R", "goal": "G", "backstory": "B", "usecase": "U"}
        
        res = repo.create_agent(req)
        self.assertEqual(res.role, "R")
        
        # DuplicateKeyError
        self.mock_coll.insert_one.side_effect = DuplicateKeyError("Duplicate")
        with self.assertRaises(ValueError) as cm:
            repo.create_agent(req)
        self.assertIn("already exists", str(cm.exception))
        self.mock_coll.insert_one.side_effect = None

        # get_agent_by_id
        res = repo.get_agent_by_id(VALID_ID)
        self.assertEqual(res.id, VALID_ID)
        
        # get_agent_by_id - None
        self.mock_coll.find_one.return_value = None
        res = repo.get_agent_by_id(VALID_ID)
        self.assertIsNone(res)
        self.mock_coll.find_one.return_value = {"_id": mock_result.inserted_id, "role": "R", "goal": "G", "backstory": "B", "usecase": "U"}
        
        # Invalid ID
        with self.assertRaises(ValueError):
            repo.get_agent_by_id("invalid")

        # find_by_role_and_usecase
        res = repo.find_by_role_and_usecase("R", "U")
        self.assertEqual(res.role, "R")
        
        # find_by_role_and_usecase - None
        self.mock_coll.find_one.return_value = None
        res = repo.find_by_role_and_usecase("R", "U")
        self.assertIsNone(res)
        self.mock_coll.find_one.return_value = {"_id": mock_result.inserted_id, "role": "R", "goal": "G", "backstory": "B", "usecase": "U"}

        # update_agent
        mock_update_res = MagicMock()
        mock_update_res.modified_count = 1
        self.mock_coll.update_one.return_value = mock_update_res
        res = repo.update_agent(VALID_ID, req)
        self.assertIsNotNone(res)
        
        # update_agent - invalid ID
        with self.assertRaises(ValueError):
            repo.update_agent("invalid", req)

        # delete_agent
        repo.delete_agent(VALID_ID)
        self.mock_coll.delete_one.assert_called()
        
        # delete_agent - invalid ID
        with self.assertRaises(ValueError):
            repo.delete_agent("invalid")

        # get_agents_by_usecase
        self.mock_coll.find.return_value = [{"_id": ObjectId(VALID_ID), "role": "R", "goal": "G", "backstory": "B", "usecase": "U"}]
        res = repo.get_agents_by_usecase("U")
        self.assertEqual(len(res), 1)

    def test_task_repository(self):
        """Test TaskRepository methods."""
        repo = TaskRepository(self.repo_data)
        
        # create_task
        req = TaskRequest(name="T", description="D", expected_output="O", usecase="U")
        mock_result = MagicMock()
        mock_result.inserted_id = ObjectId(VALID_ID)
        self.mock_coll.insert_one.return_value = mock_result
        self.mock_coll.find_one.return_value = {"_id": mock_result.inserted_id, "name": "T", "description": "D", "expected_output": "O", "usecase": "U"}
        
        res = repo.create_task(req)
        self.assertEqual(res.name, "T")

        # DuplicateKeyError
        self.mock_coll.insert_one.side_effect = DuplicateKeyError("Duplicate")
        with self.assertRaises(ValueError):
            repo.create_task(req)
        self.mock_coll.insert_one.side_effect = None

        # get_task_by_id
        res = repo.get_task_by_id(VALID_ID)
        self.assertEqual(res.id, VALID_ID)
        
        # get_task_by_id - None
        self.mock_coll.find_one.return_value = None
        res = repo.get_task_by_id(VALID_ID)
        self.assertIsNone(res)
        self.mock_coll.find_one.return_value = {"_id": mock_result.inserted_id, "name": "T", "description": "D", "expected_output": "O", "usecase": "U"}

        # find_by_name_and_usecase
        res = repo.find_by_name_and_usecase("T", "U")
        self.assertEqual(res.name, "T")
        
        # find_by_name_and_usecase - None
        self.mock_coll.find_one.return_value = None
        res = repo.find_by_name_and_usecase("T", "U")
        self.assertIsNone(res)
        self.mock_coll.find_one.return_value = {"_id": mock_result.inserted_id, "name": "T", "description": "D", "expected_output": "O", "usecase": "U"}

        # update_task
        mock_update_res = MagicMock()
        mock_update_res.modified_count = 1
        self.mock_coll.update_one.return_value = mock_update_res
        res = repo.update_task(VALID_ID, req)
        self.assertIsNotNone(res)
        
        # update_task - invalid ID
        with self.assertRaises(ValueError):
            repo.update_task("invalid", req)

        # delete_task
        repo.delete_task(VALID_ID)
        self.mock_coll.delete_one.assert_called()
        
        # delete_task - invalid ID
        with self.assertRaises(ValueError):
            repo.delete_task("invalid")

        # get_tasks_by_usecase
        self.mock_coll.find.return_value = [{"_id": ObjectId(VALID_ID), "name": "T", "description": "D", "expected_output": "O", "usecase": "U"}]
        res = repo.get_tasks_by_usecase("U")
        self.assertEqual(len(res), 1)

    def test_crew_config_repository(self):
        """Test CrewConfigRepository methods."""
        repo = CrewConfigRepository(self.repo_data)
        
        # create_crew_config
        req = CrewConfigRequest(name="C", agents={}, tasks={}, usecase="U")
        mock_result = MagicMock()
        mock_result.inserted_id = ObjectId(VALID_ID)
        self.mock_coll.insert_one.return_value = mock_result
        self.mock_coll.find_one.return_value = {"_id": mock_result.inserted_id, "name": "C", "agents": {}, "tasks": {}, "usecase": "U"}
        
        res = repo.create_crew_config(req)
        self.assertEqual(res.name, "C")
        
        # create_crew_config - None result
        self.mock_coll.insert_one.return_value = None
        res = repo.create_crew_config(req)
        self.assertIsNone(res)
        self.mock_coll.insert_one.return_value = mock_result

        # DuplicateKeyError
        self.mock_coll.insert_one.side_effect = DuplicateKeyError("Duplicate")
        with self.assertRaises(ValueError):
            repo.create_crew_config(req)
        self.mock_coll.insert_one.side_effect = None

        # get_crew_config_by_id
        res = repo.get_crew_config_by_id(VALID_ID)
        self.assertEqual(res.id, VALID_ID)
        
        # get_crew_config_by_id - None
        self.mock_coll.find_one.return_value = None
        res = repo.get_crew_config_by_id(VALID_ID)
        self.assertIsNone(res)
        self.mock_coll.find_one.return_value = {"_id": mock_result.inserted_id, "name": "C", "agents": {}, "tasks": {}, "usecase": "U"}
        
        # Invalid ID
        with self.assertRaises(ValueError):
            repo.get_crew_config_by_id("invalid")

        # update_crew_config
        mock_update_res = MagicMock()
        mock_update_res.modified_count = 1
        self.mock_coll.update_one.return_value = mock_update_res
        res = repo.update_crew_config(VALID_ID, req)
        self.assertIsNotNone(res)
        
        # update_crew_config - No modified count
        mock_update_res.modified_count = 0
        res = repo.update_crew_config(VALID_ID, req)
        self.assertIsNone(res)
        mock_update_res.modified_count = 1
        
        # update_crew_config - invalid ID
        with self.assertRaises(ValueError):
            repo.update_crew_config("invalid", req)

        # delete_crew_config
        repo.delete_crew_config(VALID_ID)
        self.mock_coll.delete_one.assert_called()
        
        # delete_crew_config - invalid ID
        with self.assertRaises(ValueError):
            repo.delete_crew_config("invalid")

        # get_crew_configs_by_usecase
        self.mock_coll.find.return_value = [{"_id": ObjectId(VALID_ID), "name": "C", "agents": {}, "tasks": {}, "usecase": "U"}]
        res = repo.get_crew_configs_by_usecase("U")
        self.assertEqual(len(res), 1)

        # get_crew_by_name_and_usecase
        res = repo.get_crew_by_name_and_usecase("C", "U")
        self.assertEqual(res.name, "C")
        
        # get_crew_by_name_and_usecase - None
        self.mock_coll.find_one.return_value = None
        res = repo.get_crew_by_name_and_usecase("C", "U")
        self.assertIsNone(res)
        self.mock_coll.find_one.return_value = {"_id": mock_result.inserted_id, "name": "C", "agents": {}, "tasks": {}, "usecase": "U"}

        # get_all_crew_configs
        self.mock_coll.find.return_value = [{"_id": ObjectId(VALID_ID), "name": "C", "agents": {}, "tasks": {}, "usecase": "U"}]
        res = repo.get_all_crew_configs()
        self.assertEqual(len(res), 1)


if __name__ == '__main__':
    unittest.main()
