import unittest
from datetime import datetime
from amsha.execution_state.domain.enums import ExecutionStatus
from amsha.execution_state.domain.execution_state import ExecutionState

class TestExecutionState(unittest.TestCase):
    
    def test_initialization(self):
        state = ExecutionState(
            inputs={},
            outputs={},
            metadata={},
            history=[]
        )
        self.assertIsNotNone(state.execution_id)
        self.assertEqual(state.status, ExecutionStatus.PENDING)
        self.assertIsInstance(state.created_at, datetime)
        self.assertEqual(state.inputs, {})
        self.assertEqual(state.outputs, {})
        self.assertEqual(state.history, [])

    def test_status_update(self):
        state = ExecutionState(
            inputs={},
            outputs={},
            metadata={},
            history=[]
        )
        state.update_status(ExecutionStatus.RUNNING, metadata={"reason": "started"})
        
        self.assertEqual(state.status, ExecutionStatus.RUNNING)
        self.assertEqual(len(state.history), 1)
        self.assertEqual(state.history[0].status, ExecutionStatus.RUNNING)
        self.assertEqual(state.history[0].metadata["reason"], "started")
        
    def test_output_update(self):
        state = ExecutionState(
            inputs={},
            outputs={},
            metadata={},
            history=[]
        )
        state.set_output("result", 42)
        self.assertEqual(state.outputs["result"], 42)
        
    def test_metadata_update(self):
        state = ExecutionState(
            inputs={},
            outputs={},
            metadata={},
            history=[]
        )
        state.add_metadata("env", "prod")
        self.assertEqual(state.metadata["env"], "prod")

if __name__ == '__main__':
    unittest.main()
