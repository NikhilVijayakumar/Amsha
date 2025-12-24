"""
Unit tests for BaseCrewOrchestrator class.
"""
import unittest
from unittest.mock import MagicMock, patch, Mock
from amsha.crew_forge.service.base_crew_orchestrator import BaseCrewOrchestrator
from amsha.execution_runtime.domain.execution_mode import ExecutionMode
from amsha.execution_runtime.domain.execution_handle import ExecutionHandle
from amsha.execution_state.domain.enums import ExecutionStatus
from amsha.crew_forge.exceptions import CrewManagerException, CrewExecutionException


class TestBaseCrewOrchestrator(unittest.TestCase):
    """Test cases for BaseCrewOrchestrator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_manager = MagicMock()
        self.mock_manager.model_name = "test-model"
        self.mock_runtime = MagicMock()
        self.mock_state_manager = MagicMock()
        
        self.orchestrator = BaseCrewOrchestrator(
            manager=self.mock_manager,
            runtime=self.mock_runtime,
            state_manager=self.mock_state_manager
        )
        
    def test_initialization(self):
        """Test proper initialization of BaseCrewOrchestrator."""
        self.assertEqual(self.orchestrator.manager, self.mock_manager)
        self.assertEqual(self.orchestrator.runtime, self.mock_runtime)
        self.assertEqual(self.orchestrator.state_manager, self.mock_state_manager)

    @patch('amsha.crew_forge.service.base_crew_orchestrator.CrewPerformanceMonitor')
    def test_run_crew_interactive_success(self, mock_monitor_class):
        """Test successful interactive crew execution."""
        # Setup mocks
        crew_name = "test_crew"
        inputs = {"topic": "AI"}
        
        mock_state = MagicMock()
        mock_state.execution_id = "exec-123"
        self.mock_state_manager.create_execution.return_value = mock_state
        
        mock_crew = MagicMock()
        mock_crew.kickoff.return_value = "Success result"
        self.mock_manager.build_atomic_crew.return_value = mock_crew
        
        mock_handle = MagicMock(spec=ExecutionHandle)
        mock_handle.result.return_value = "Success result"
        self.mock_runtime.submit.side_effect = lambda func, mode: mock_handle
        
        # Call the orchestrator
        result = self.orchestrator.run_crew(crew_name, inputs, mode=ExecutionMode.INTERACTIVE)
        
        # Verify
        self.assertEqual(result, "Success result")
        self.mock_state_manager.create_execution.assert_called_once_with(inputs=inputs)
        self.mock_manager.build_atomic_crew.assert_called_once_with(crew_name, None)
        self.mock_runtime.submit.assert_called_once()
        
        # Verify internal execution function logic
        exec_func = self.mock_runtime.submit.call_args[0][0]
        exec_result = exec_func()
        
        self.assertEqual(exec_result, "Success result")
        mock_crew.kickoff.assert_called_once_with(inputs=inputs)
        self.mock_state_manager.update_status.assert_any_call(
            "exec-123", 
            ExecutionStatus.COMPLETED, 
            metadata=unittest.mock.ANY
        )

    def test_run_crew_background_success(self):
        """Test successful background crew execution."""
        # Setup mocks
        crew_name = "test_crew"
        inputs = {"topic": "AI"}
        
        mock_state = MagicMock()
        mock_state.execution_id = "exec-123"
        self.mock_state_manager.create_execution.return_value = mock_state
        
        mock_handle = MagicMock(spec=ExecutionHandle)
        self.mock_runtime.submit.return_value = mock_handle
        
        # Call the orchestrator
        result = self.orchestrator.run_crew(crew_name, inputs, mode=ExecutionMode.BACKGROUND)
        
        # Verify
        self.assertEqual(result, mock_handle)
        self.assertEqual(mock_handle.execution_state_id, "exec-123")
        self.mock_runtime.submit.assert_called_once()

    def test_run_crew_build_failure(self):
        """Test error handling when crew building fails."""
        # Setup mocks
        crew_name = "test_crew"
        inputs = {"topic": "AI"}
        
        mock_state = MagicMock()
        mock_state.execution_id = "exec-123"
        self.mock_state_manager.create_execution.return_value = mock_state
        
        self.mock_manager.build_atomic_crew.side_effect = Exception("Build failed")
        
        # Call and verify
        with self.assertRaises(CrewManagerException):
            self.orchestrator.run_crew(crew_name, inputs)
            
        self.mock_state_manager.update_status.assert_any_call(
            "exec-123", 
            ExecutionStatus.FAILED, 
            metadata=unittest.mock.ANY
        )

    @patch('amsha.crew_forge.service.base_crew_orchestrator.CrewPerformanceMonitor')
    def test_run_crew_kickoff_failure(self, mock_monitor_class):
        """Test error handling when crew kickoff fails."""
        # Setup mocks
        crew_name = "test_crew"
        inputs = {"topic": "AI"}
        
        mock_state = MagicMock()
        mock_state.execution_id = "exec-123"
        self.mock_state_manager.create_execution.return_value = mock_state
        
        mock_crew = MagicMock()
        mock_crew.kickoff.side_effect = Exception("Kickoff failed")
        self.mock_manager.build_atomic_crew.return_value = mock_crew
        
        # Mock runtime to execute immediately and raise
        mock_handle = MagicMock(spec=ExecutionHandle)
        mock_handle.result.side_effect = lambda: exec_func()
        self.mock_runtime.submit.side_effect = lambda func, mode: mock_handle
        
        # We need to capture the exec_func from the submit call
        exec_func = None
        def mock_submit(func, mode):
            nonlocal exec_func
            exec_func = func
            return mock_handle
        self.mock_runtime.submit.side_effect = mock_submit
        
        # Call the orchestrator - should raise exception in INTERACTIVE mode
        with self.assertRaises(CrewExecutionException):
            self.orchestrator.run_crew(crew_name, inputs, mode=ExecutionMode.INTERACTIVE)
            
        self.mock_state_manager.update_status.assert_any_call(
            "exec-123", 
            ExecutionStatus.FAILED, 
            metadata=unittest.mock.ANY
        )

    def test_getters(self):
        """Test getter methods."""
        self.mock_manager.output_file = "output.json"
        self.orchestrator.last_execution_id = "exec-123"
        
        self.assertEqual(self.orchestrator.get_last_output_file(), "output.json")
        self.assertEqual(self.orchestrator.get_last_execution_id(), "exec-123")
        self.assertIsNone(self.orchestrator.get_last_performance_stats())

if __name__ == '__main__':
    unittest.main()
