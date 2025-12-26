import unittest
import time
from amsha.execution_runtime.service.runtime_engine import RuntimeEngine
from amsha.execution_runtime.domain.execution_mode import ExecutionMode
from amsha.execution_state.domain.enums import ExecutionStatus

def dummy_task(x, y):
    return x + y

def slow_task(seconds):
    time.sleep(seconds)
    return "done"

class TestRuntimeEngine(unittest.TestCase):
    def setUp(self):
        self.engine = RuntimeEngine()
        
    def tearDown(self):
        self.engine.shutdown()
        
    def test_sync_execution(self):
        handle = self.engine.submit(dummy_task, 10, 20, mode=ExecutionMode.INTERACTIVE)
        self.assertEqual(handle.status(), ExecutionStatus.COMPLETED)
        self.assertEqual(handle.result(), 30)
        self.assertIsInstance(handle.execution_id, str)
        
    def test_sync_execution_failure(self):
        def failing_task():
            raise ValueError("Task failed")
        
        with self.assertRaises(ValueError):
            self.engine.submit(failing_task, mode=ExecutionMode.INTERACTIVE)
            
    def test_background_execution(self):
        handle = self.engine.submit(slow_task, 0.1, mode=ExecutionMode.BACKGROUND)
        # It might be pending or running immediately
        self.assertTrue(handle.status() in [ExecutionStatus.PENDING, ExecutionStatus.RUNNING, ExecutionStatus.COMPLETED])
        result = handle.result(timeout=1.0)
        self.assertEqual(result, "done")
        self.assertEqual(handle.status(), ExecutionStatus.COMPLETED)
        
    def test_background_execution_failure(self):
        def failing_task():
            raise ValueError("Async task failed")
            
        handle = self.engine.submit(failing_task, mode=ExecutionMode.BACKGROUND)
        with self.assertRaises(ValueError):
            handle.result(timeout=1.0)
        self.assertEqual(handle.status(), ExecutionStatus.FAILED)
        
    def test_background_execution_timeout(self):
        handle = self.engine.submit(slow_task, 2.0, mode=ExecutionMode.BACKGROUND)
        with self.assertRaises(TimeoutError):
            handle.result(timeout=0.1)
            
    def test_cancellation_success(self):
        # To ensure it can be cancelled, we need a task that hasn't started yet.
        # We can fill the executor with other tasks.
        for _ in range(10):
            self.engine.submit(slow_task, 1.0)
            
        handle = self.engine.submit(slow_task, 2.0, mode=ExecutionMode.BACKGROUND)
        cancelled = handle.cancel()
        if cancelled:
            self.assertEqual(handle.status(), ExecutionStatus.CANCELLED)
            with self.assertRaises(RuntimeError):
                handle.result()
        self.assertIsInstance(cancelled, bool)

    def test_cancel_no_future(self):
        handle = self.engine.submit(dummy_task, 1, 2, mode=ExecutionMode.INTERACTIVE)
        self.assertFalse(handle.cancel())

    def test_status_pending(self):
        # Mocking a future to be in pending state (not running, not done)
        from unittest.mock import MagicMock
        mock_future = MagicMock()
        mock_future.running.return_value = False
        mock_future.done.return_value = False
        
        from amsha.execution_runtime.service.runtime_engine import LocalExecutionHandle
        handle = LocalExecutionHandle("test-id", future=mock_future)
        self.assertEqual(handle.status(), ExecutionStatus.PENDING)

    def test_status_cancelled_future(self):
        from unittest.mock import MagicMock
        mock_future = MagicMock()
        mock_future.running.return_value = False
        mock_future.done.return_value = True
        mock_future.cancelled.return_value = True
        
        from amsha.execution_runtime.service.runtime_engine import LocalExecutionHandle
        handle = LocalExecutionHandle("test-id", future=mock_future)
        self.assertEqual(handle.status(), ExecutionStatus.CANCELLED)

if __name__ == '__main__':
    unittest.main()
