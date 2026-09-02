import unittest

from crewai.events.event_bus import crewai_event_bus
from crewai.events.types.crew_events import (
    CrewKickoffCompletedEvent,
    CrewKickoffFailedEvent,
    CrewKickoffStartedEvent,
)
from crewai.events.types.flow_events import (
    FlowFailedEvent,
    FlowFinishedEvent,
    FlowStartedEvent,
    MethodExecutionFailedEvent,
    MethodExecutionFinishedEvent,
    MethodExecutionStartedEvent,
)
from crewai.events.types.llm_events import LLMCallCompletedEvent, LLMCallStartedEvent, LLMCallType
from crewai.events.types.task_events import TaskCompletedEvent, TaskStartedEvent
from crewai.events.types.tool_usage_events import (
    ToolUsageErrorEvent,
    ToolUsageFinishedEvent,
    ToolUsageStartedEvent,
)
from crewai.tasks.task_output import TaskOutput

from amsha.crew_monitor.service.amsha_event_listener import (
    AmshaEventListener,
    _extract_usage,
)


def _emit(source, event):
    """Emit an event and block until all sync handlers have run."""
    future = crewai_event_bus.emit(source, event)
    if future is not None:
        future.result(timeout=5)


class TestAmshaEventListener(unittest.TestCase):
    """Register a fresh listener inside a scoped_handlers() context so the
    module-level singleton on the global bus is left untouched."""

    def setUp(self):
        import amsha.crew_monitor  # noqa: F401  # ensures the singleton exists

    def _listener(self):
        self._scope = crewai_event_bus.scoped_handlers()
        self._scope.__enter__()
        self.addCleanup(self._scope.__exit__, None, None, None)
        return AmshaEventListener()

    def test_crew_completed_logs_tokens_and_duration(self):
        with self.assertLogs("Amsha.crew_monitor.events", level="INFO") as cm:
            listener = self._listener()
            _emit(None, CrewKickoffStartedEvent(crew_name="alpha", inputs={}))
            _emit(None, CrewKickoffCompletedEvent(crew_name="alpha", output="done", total_tokens=42))
        record = cm.records[-1]
        self.assertEqual(record.getMessage(), "Crew kickoff completed")
        self.assertEqual(record.crew_name, "alpha")
        self.assertEqual(record.total_tokens, 42)
        self.assertIsNotNone(record.duration_seconds)

    def test_crew_failed_logs_error(self):
        with self.assertLogs("Amsha.crew_monitor.events", level="ERROR") as cm:
            self._listener()
            _emit(None, CrewKickoffFailedEvent(crew_name="alpha", error="boom"))
        self.assertEqual(cm.records[-1].getMessage(), "Crew kickoff failed")
        self.assertEqual(cm.records[-1].error, "boom")

    def test_task_completed_logs_task_timing(self):
        with self.assertLogs("Amsha.crew_monitor.events", level="INFO") as cm:
            self._listener()
            _emit(None, TaskStartedEvent(task_name="research", context=None))
            _emit(None, TaskCompletedEvent(
                output=TaskOutput(raw="ok", description="d", agent="a"), task_name="research"))
        record = cm.records[-1]
        self.assertEqual(record.getMessage(), "Task completed")
        self.assertEqual(record.task_name, "research")
        self.assertIsNotNone(record.duration_seconds)

    def test_llm_completed_logs_per_call_usage(self):
        with self.assertLogs("Amsha.crew_monitor.events", level="INFO") as cm:
            self._listener()
            _emit(None, LLMCallStartedEvent(call_id="c1", model="local-model"))
            _emit(None, LLMCallCompletedEvent(
                call_id="c1", model="local-model", response="hi",
                call_type=LLMCallType.LLM_CALL,
                usage={"prompt_tokens": 5, "completion_tokens": 3},
            ))
        record = cm.records[-1]
        self.assertEqual(record.getMessage(), "LLM call completed")
        self.assertEqual(record.model, "local-model")
        self.assertEqual(record.prompt_tokens, 5)
        self.assertEqual(record.completion_tokens, 3)
        self.assertIsNotNone(record.duration_seconds)

    def test_tool_finished_logs_tool_name(self):
        import datetime
        now = datetime.datetime.now(datetime.timezone.utc)
        with self.assertLogs("Amsha.crew_monitor.events", level="INFO") as cm:
            self._listener()
            _emit(None, ToolUsageStartedEvent(tool_name="search", tool_args={}))
            _emit(None, ToolUsageFinishedEvent(
                tool_name="search", tool_args={},
                started_at=now, finished_at=now, output="ok",
            ))
        record = cm.records[-1]
        self.assertEqual(record.getMessage(), "Tool usage finished")
        self.assertEqual(record.tool_name, "search")
        self.assertIsNotNone(record.duration_seconds)

    def test_tool_error_logs_error(self):
        with self.assertLogs("Amsha.crew_monitor.events", level="ERROR") as cm:
            self._listener()
            _emit(None, ToolUsageErrorEvent(tool_name="search", tool_args={}, error="bad"))
        self.assertEqual(cm.records[-1].getMessage(), "Tool usage error")
        self.assertEqual(cm.records[-1].tool_name, "search")

    def test_flow_lifecycle_logs_names(self):
        with self.assertLogs("Amsha.crew_monitor.events", level="INFO") as cm:
            self._listener()
            _emit(None, FlowStartedEvent(flow_name="pipeline"))
            _emit(None, FlowFinishedEvent(flow_name="pipeline", result="ok", state={}))
            _emit(None, MethodExecutionStartedEvent(flow_name="pipeline", method_name="run_a", params={}, state={}))
            _emit(None, MethodExecutionFinishedEvent(flow_name="pipeline", method_name="run_a", result="r", state={}))
        self.assertEqual(cm.records[-1].getMessage(), "Flow method finished")
        self.assertEqual(cm.records[-1].flow_name, "pipeline")
        self.assertEqual(cm.records[-1].method_name, "run_a")
        self.assertIsNotNone(cm.records[-1].duration_seconds)

    def test_method_failed_logs_error(self):
        with self.assertLogs("Amsha.crew_monitor.events", level="ERROR") as cm:
            self._listener()
            _emit(None, MethodExecutionFailedEvent(
                flow_name="pipeline", method_name="run_a", error=Exception("nope")))
        self.assertEqual(cm.records[-1].getMessage(), "Flow method failed")
        self.assertEqual(cm.records[-1].error, "nope")

    def test_flow_failed_logs_error(self):
        with self.assertLogs("Amsha.crew_monitor.events", level="ERROR") as cm:
            self._listener()
            _emit(None, FlowFailedEvent(flow_name="pipeline", error=Exception("bad flow")))
        self.assertEqual(cm.records[-1].getMessage(), "Flow failed")
        self.assertIn("bad flow", cm.records[-1].error)

    def test_handlers_do_not_leak(self):
        scope = crewai_event_bus.scoped_handlers()
        scope.__enter__()
        listener = AmshaEventListener()
        scope.__exit__(None, None, None)

        # The bus must be exactly back to its pre-scope state: the module-level
        # singleton's handler is present, the temporary listener's is not.
        from amsha.crew_monitor import _event_listener

        handlers = crewai_event_bus._sync_handlers.get(TaskStartedEvent, frozenset())
        self.assertIn(_event_listener._record_start, handlers)
        self.assertNotIn(listener._record_start, handlers)

    def test_extract_usage_normalizes_provider_keys(self):
        self.assertEqual(
            _extract_usage({"input_tokens": 7, "output_tokens": 4}),
            {"prompt_tokens": 7, "completion_tokens": 4, "total_tokens": None},
        )
        self.assertEqual(_extract_usage(None), {})
        self.assertEqual(_extract_usage({}), {})


if __name__ == '__main__':
    unittest.main()