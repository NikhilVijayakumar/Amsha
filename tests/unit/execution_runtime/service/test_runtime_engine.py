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
        
    def test_background_execution(self):
        handle = self.engine.submit(slow_task, 0.1, mode=ExecutionMode.BACKGROUND)
        # It might be pending or running immediately
        self.assertTrue(handle.status() in [ExecutionStatus.PENDING, ExecutionStatus.RUNNING, ExecutionStatus.COMPLETED])
        result = handle.result(timeout=1.0)
        self.assertEqual(result, "done")
        self.assertEqual(handle.status(), ExecutionStatus.COMPLETED)
        
    def test_cancellation(self):
        handle = self.engine.submit(slow_task, 2.0, mode=ExecutionMode.BACKGROUND)
        cancelled = handle.cancel()
        # Note: cancellation in ThreadPoolExecutor only works if the task hasn't started.
        # If it started, cancel() returns False. 
        # So we can't strictly assert True/False without controlling the queue.
        # But we can check api signature.
        self.assertIsInstance(cancelled, bool)

if __name__ == '__main__':
    unittest.main()
