"""
Unit tests for the CrewAI Flow pipeline orchestrator (proposal 03).
"""
import unittest

from amsha.crew_forge.orchestrator.flow.flow_crew_pipeline import (
    FlowCrewOrchestrator,
    PipelineState,
    _CrewPipelineFlow,
)
from amsha.execution_runtime.domain.execution_mode import ExecutionMode
from amsha.execution_runtime.service.runtime_engine import RuntimeEngine


class _RecordingOrchestrator:
    """Duck-typed BaseCrewOrchestrator that records crew runs without an LLM."""

    def __init__(self):
        self.calls = []
        self.runtime = RuntimeEngine()

    def run_crew(self, crew_name, inputs, filename_suffix=None, mode=ExecutionMode.INTERACTIVE):
        self.calls.append((crew_name, dict(inputs), filename_suffix, mode))
        return f"{crew_name}-done"


class TestFlowCrewOrchestrator(unittest.TestCase):
    def _build(self, pipeline, orchestrator=None):
        orchestrator = orchestrator or _RecordingOrchestrator()
        return FlowCrewOrchestrator(orchestrator, pipeline), orchestrator

    def test_runs_every_pipeline_crew_in_order(self):
        flow, orch = self._build(["crew_a", "crew_b"])
        out = flow.kickoff({"topic": "hi"})
        self.assertEqual([c[0] for c in orch.calls], ["crew_a", "crew_b"])
        self.assertEqual(out, {"crew_a": "crew_a-done", "crew_b": "crew_b-done"})

    def test_passes_same_inputs_to_every_crew(self):
        flow, orch = self._build(["a", "b"])
        flow.kickoff({"k": 1})
        for _name, inputs, _suffix, _mode in orch.calls:
            self.assertEqual(inputs, {"k": 1})

    def test_state_is_typed_pipeline_state(self):
        flow, _ = self._build(["a"])
        self.assertIsInstance(flow.flow, _CrewPipelineFlow)
        self.assertIsInstance(flow.flow.state, PipelineState)

    def test_get_last_output(self):
        flow, _ = self._build(["a", "b"])
        flow.kickoff({"k": 1})
        self.assertEqual(flow.get_last_output(), "b-done")
        self.assertEqual(flow.get_last_output("a"), "a-done")
        self.assertIsNone(flow.get_last_output("nope"))

    def test_empty_pipeline_raises(self):
        with self.assertRaises(ValueError):
            FlowCrewOrchestrator(_RecordingOrchestrator(), [])

    def test_background_mode_returns_execution_handle(self):
        flow, orch = self._build(["a", "b"])
        handle = flow.kickoff({"x": 1}, mode=ExecutionMode.BACKGROUND)
        self.assertEqual(handle.result(), {"a": "a-done", "b": "b-done"})
        self.assertEqual([c[0] for c in orch.calls], ["a", "b"])


if __name__ == "__main__":
    unittest.main()