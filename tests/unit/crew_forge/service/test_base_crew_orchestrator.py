"""
Unit tests for BaseCrewOrchestrator class.
"""
import unittest
from unittest.mock import MagicMock, patch, Mock
from amsha.crew_forge.service.base_crew_orchestrator import BaseCrewOrchestrator
from amsha.execution_runtime.domain.execution_mode import ExecutionMode
from amsha.execution_runtime.domain.execution_handle import ExecutionHandle
from amsha.execution_state.domain.enums import ExecutionStatus
from amsha.execution_state.service.state_manager import StateManager, InMemoryStateRepository
from amsha.crew_forge.exceptions import CrewManagerException, CrewExecutionException
from crewai import CheckpointConfig


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

    @patch('amsha.crew_forge.service.base_crew_orchestrator.CrewPerformanceMonitor')
    def test_run_crew_records_checkpoint_ref(self, mock_monitor_class):
        """A crew with checkpointing enabled has its location recorded on the execution state."""
        crew_name = "test_crew"
        inputs = {"topic": "AI"}

        mock_state = MagicMock()
        mock_state.execution_id = "exec-123"
        self.mock_state_manager.create_execution.return_value = mock_state

        mock_crew = MagicMock()
        mock_crew.kickoff.return_value = "Success result"
        mock_crew.checkpoint = CheckpointConfig(location="./execution/checkpoints")
        self.mock_manager.build_atomic_crew.return_value = mock_crew

        mock_handle = MagicMock(spec=ExecutionHandle)
        mock_handle.result.return_value = "Success result"
        self.mock_runtime.submit.side_effect = lambda func, mode: mock_handle

        self.orchestrator.run_crew(crew_name, inputs, mode=ExecutionMode.INTERACTIVE)

        exec_func = self.mock_runtime.submit.call_args[0][0]
        exec_func()
        self.mock_state_manager.attach_checkpoint.assert_called_once_with(
            "exec-123", "./execution/checkpoints"
        )

    @patch('amsha.crew_forge.service.base_crew_orchestrator.CrewPerformanceMonitor')
    def test_run_crew_skips_attach_when_no_checkpoint(self, mock_monitor_class):
        """A crew without checkpointing does not call attach_checkpoint."""
        crew_name = "test_crew"
        inputs = {"topic": "AI"}

        mock_state = MagicMock()
        mock_state.execution_id = "exec-123"
        self.mock_state_manager.create_execution.return_value = mock_state

        mock_crew = MagicMock()
        mock_crew.kickoff.return_value = "Success result"
        mock_crew.checkpoint = None
        self.mock_manager.build_atomic_crew.return_value = mock_crew

        mock_handle = MagicMock(spec=ExecutionHandle)
        mock_handle.result.return_value = "Success result"
        self.mock_runtime.submit.side_effect = lambda func, mode: mock_handle

        self.orchestrator.run_crew(crew_name, inputs, mode=ExecutionMode.INTERACTIVE)
        exec_func = self.mock_runtime.submit.call_args[0][0]
        exec_func()

        self.mock_state_manager.attach_checkpoint.assert_not_called()

    @patch('amsha.crew_forge.service.base_crew_orchestrator.CrewPerformanceMonitor')
    def test_resume_crew_forwards_restore(self, mock_monitor_class):
        """resume_crew looks up the stored checkpoint ref and passes it to run_crew."""
        state_manager = StateManager(repository=InMemoryStateRepository())
        state = state_manager.create_execution(inputs={"topic": "AI"})
        state_manager.attach_checkpoint(state.execution_id, "./execution/checkpoints")

        orch = BaseCrewOrchestrator(
            manager=self.mock_manager,
            runtime=self.mock_runtime,
            state_manager=state_manager,
        )
        with patch.object(orch, "run_crew", return_value="resumed") as mocked_run:
            result = orch.resume_crew("test_crew", {"topic": "AI"}, state.execution_id, restore_from="1712345678_abc12345")

        self.assertEqual(result, "resumed")
        ckpt = mocked_run.call_args.kwargs["from_checkpoint"]
        self.assertIsInstance(ckpt, CheckpointConfig)
        self.assertEqual(ckpt.location, "./execution/checkpoints")
        self.assertEqual(ckpt.restore_from, "1712345678_abc12345")

    def test_resume_crew_without_checkpoint_raises(self):
        """resume_crew on an execution with no recorded checkpoint raises CrewExecutionException."""
        state_manager = StateManager(repository=InMemoryStateRepository())
        state = state_manager.create_execution(inputs={})

        orch = BaseCrewOrchestrator(
            manager=self.mock_manager,
            runtime=self.mock_runtime,
            state_manager=state_manager,
        )
        with self.assertRaises(CrewExecutionException):
            orch.resume_crew("test_crew", {}, state.execution_id, restore_from="id")

    def test_resume_crew_unknown_execution_raises(self):
        """resume_crew on an unknown execution raises CrewExecutionException."""
        orch = BaseCrewOrchestrator(
            manager=self.mock_manager,
            runtime=self.mock_runtime,
            state_manager=StateManager(repository=InMemoryStateRepository()),
        )
        with self.assertRaises(CrewExecutionException):
            orch.resume_crew("test_crew", {}, "missing-exec", restore_from="id")

if __name__ == '__main__':
    unittest.main()
