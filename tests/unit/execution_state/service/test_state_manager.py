import unittest
from unittest.mock import MagicMock
from amsha.execution_state.service.state_manager import StateManager, InMemoryStateRepository
from amsha.execution_state.domain.execution_state import ExecutionState
from amsha.execution_state.domain.enums import ExecutionStatus

class TestInMemoryStateRepository(unittest.TestCase):
    def setUp(self):
        self.repo = InMemoryStateRepository()
        
    def test_save_and_get(self):
        state = ExecutionState(inputs={"test": "data"})
        self.repo.save(state)
        
        retrieved = self.repo.get(state.execution_id)
        self.assertEqual(retrieved, state)
        self.assertEqual(retrieved.inputs, {"test": "data"})
        
    def test_get_non_existent(self):
        self.assertIsNone(self.repo.get("non-existent-id"))

class TestStateManager(unittest.TestCase):
    def setUp(self):
        self.repo = InMemoryStateRepository()
        self.manager = StateManager(repository=self.repo)
        
    def test_create_execution(self):
        inputs = {"key": "value"}
        state = self.manager.create_execution(inputs=inputs)
        
        self.assertIsInstance(state, ExecutionState)
        self.assertEqual(state.inputs, inputs)
        self.assertEqual(state.status, ExecutionStatus.PENDING)
        
        # Verify persistence
        retrieved = self.repo.get(state.execution_id)
        self.assertEqual(retrieved, state)
        
    def test_create_execution_no_inputs(self):
        state = self.manager.create_execution()
        self.assertEqual(state.inputs, {})
        
    def test_get_execution(self):
        state = self.manager.create_execution()
        retrieved = self.manager.get_execution(state.execution_id)
        self.assertEqual(retrieved, state)
        
    def test_get_execution_non_existent(self):
        self.assertIsNone(self.manager.get_execution("missing"))
        
    def test_update_status_success(self):
        state = self.manager.create_execution()
        metadata = {"step": "processing"}
        
        updated_state = self.manager.update_status(
            state.execution_id, 
            ExecutionStatus.RUNNING, 
            metadata=metadata
        )
        
        self.assertIsNotNone(updated_state)
        self.assertEqual(updated_state.status, ExecutionStatus.RUNNING)
        self.assertEqual(updated_state.metadata["step"], "processing")
        
        # Verify persistence
        retrieved = self.repo.get(state.execution_id)
        self.assertEqual(retrieved.status, ExecutionStatus.RUNNING)
        
    def test_update_status_non_existent(self):
        result = self.manager.update_status("missing", ExecutionStatus.RUNNING)
        self.assertIsNone(result)
        
    def test_mock_repository_interaction(self):
        mock_repo = MagicMock()
        manager = StateManager(repository=mock_repo)
        
        # Test create_execution
        manager.create_execution()
        self.assertTrue(mock_repo.save.called)
        
        # Test get_execution
        manager.get_execution("some-id")
        mock_repo.get.assert_called_with("some-id")
        
        # Test update_status
        mock_state = MagicMock()
        mock_repo.get.return_value = mock_state
        manager.update_status("some-id", ExecutionStatus.COMPLETED)
        mock_state.update_status.assert_called_with(ExecutionStatus.COMPLETED, None)
        self.assertTrue(mock_repo.save.called)

if __name__ == '__main__':
    unittest.main()
