"""
AmshaEventListener — logs CrewAI's event-bus events into Amsha's logger pipeline.

Complementary to ``CrewPerformanceMonitor``: that class samples OS-level
resources (CPU/RAM/GPU) around a run, this listener reports what actually
*happened* during it — crew/task/flow lifecycle, per-task timing, per-LLM-call
token usage, and tool calls.

CrewAI footgun: a ``BaseEventListener`` subclass is only alive while referenced,
and the module imports it at import time (crew_monitor/__init__.py) so consumers
never need to remember to keep it alive.
"""

from __future__ import annotations

import threading
import time
from typing import Any

from crewai.events.base_event_listener import BaseEventListener
from crewai.events.event_bus import CrewAIEventsBus, is_replaying
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
from crewai.events.types.llm_events import (
    LLMCallCompletedEvent,
    LLMCallFailedEvent,
    LLMCallStartedEvent,
)
from crewai.events.types.task_events import (
    TaskCompletedEvent,
    TaskFailedEvent,
    TaskStartedEvent,
)
from crewai.events.types.tool_usage_events import (
    ToolUsageErrorEvent,
    ToolUsageFinishedEvent,
    ToolUsageStartedEvent,
)

from amsha.common.logger import MetricsLogger, get_logger


def _extract_usage(usage: dict[str, Any] | None) -> dict[str, Any]:
    """Normalize provider-specific token keys to prompt/completion/total."""
    if not usage:
        return {}
    return {
        "prompt_tokens": usage.get("prompt_tokens") or usage.get("input_tokens"),
        "completion_tokens": usage.get("completion_tokens") or usage.get("output_tokens"),
        "total_tokens": usage.get("total_tokens"),
    }


class AmshaEventListener(BaseEventListener):
    """Subscribes to CrewAI's event bus and logs key lifecycle events via MetricsLogger.

    Paired start/end events (crew kickoff, task, LLM call, tool usage, flow,
    flow method) are correlated through CrewAI's ``started_event_id`` scope
    mechanism to produce per-entity durations — the detail the coarse
    whole-crew ``CrewPerformanceMonitor`` cannot provide.
    """

    def __init__(self) -> None:
        self.logger = get_logger("crew_monitor.events")
        self.metrics = MetricsLogger(self.logger)
        # event_id of a *_started event -> wall-clock time it began
        self._starts: dict[str, float] = {}
        self._lock = threading.Lock()
        super().__init__()

    def setup_listeners(self, crewai_event_bus: CrewAIEventsBus) -> None:
        """Register handlers for the events Amsha's metrics care about."""
        on = crewai_event_bus.on
        for event_type in (
            CrewKickoffStartedEvent,
            TaskStartedEvent,
            LLMCallStartedEvent,
            ToolUsageStartedEvent,
            FlowStartedEvent,
            MethodExecutionStartedEvent,
        ):
            on(event_type)(self._record_start)
        on(CrewKickoffCompletedEvent)(self._on_crew_completed)
        on(CrewKickoffFailedEvent)(self._on_crew_failed)
        on(TaskCompletedEvent)(self._on_task_completed)
        on(TaskFailedEvent)(self._on_task_failed)
        on(LLMCallCompletedEvent)(self._on_llm_completed)
        on(LLMCallFailedEvent)(self._on_llm_failed)
        on(ToolUsageFinishedEvent)(self._on_tool_finished)
        on(ToolUsageErrorEvent)(self._on_tool_error)
        on(FlowFinishedEvent)(self._on_flow_finished)
        on(FlowFailedEvent)(self._on_flow_failed)
        on(MethodExecutionFinishedEvent)(self._on_method_finished)
        on(MethodExecutionFailedEvent)(self._on_method_failed)

    def _record_start(self, source: Any, event: Any) -> None:
        """Remember the wall-clock start of a scoped event, keyed by its event_id."""
        if is_replaying():
            return
        with self._lock:
            self._starts[event.event_id] = time.time()

    def _duration(self, event: Any) -> float | None:
        """Seconds elapsed since the paired *_started event, if it was seen."""
        if is_replaying():
            return None
        started_event_id = event.started_event_id
        if not started_event_id:
            return None
        with self._lock:
            started_at = self._starts.pop(started_event_id, None)
        return round(time.time() - started_at, 4) if started_at else None

    # --------------------------------------------------------------- handlers
    def _on_crew_completed(self, source: Any, event: CrewKickoffCompletedEvent) -> None:
        """Log a completed crew run with its duration and total tokens."""
        self.metrics.logger.info("Crew kickoff completed", extra={
            "event_type": event.type,
            "crew_name": event.crew_name,
            "duration_seconds": self._duration(event),
            "total_tokens": event.total_tokens,
        })

    def _on_crew_failed(self, source: Any, event: CrewKickoffFailedEvent) -> None:
        self.logger.error("Crew kickoff failed", extra={
            "event_type": event.type,
            "crew_name": event.crew_name,
            "duration_seconds": self._duration(event),
            "error": str(event.error),
        })

    def _on_task_completed(self, source: Any, event: TaskCompletedEvent) -> None:
        self.logger.info("Task completed", extra={
            "event_type": event.type,
            "task_name": event.task_name,
            "task_id": event.task_id,
            "agent_role": event.agent_role,
            "duration_seconds": self._duration(event),
        })

    def _on_task_failed(self, source: Any, event: TaskFailedEvent) -> None:
        self.logger.error("Task failed", extra={
            "event_type": event.type,
            "task_name": event.task_name,
            "task_id": event.task_id,
            "agent_role": event.agent_role,
            "duration_seconds": self._duration(event),
            "error": event.error,
        })

    def _on_llm_completed(self, source: Any, event: LLMCallCompletedEvent) -> None:
        usage = _extract_usage(event.usage)
        self.logger.info("LLM call completed", extra={
            "event_type": event.type,
            "model": event.model,
            "call_type": event.call_type.value,
            "agent_role": event.agent_role,
            "task_name": event.task_name,
            "duration_seconds": self._duration(event),
            "finish_reason": event.finish_reason,
            **usage,
        })

    def _on_llm_failed(self, source: Any, event: LLMCallFailedEvent) -> None:
        self.logger.error("LLM call failed", extra={
            "event_type": event.type,
            "model": event.model,
            "agent_role": event.agent_role,
            "duration_seconds": self._duration(event),
            "error": event.error,
        })

    def _on_tool_finished(self, source: Any, event: ToolUsageFinishedEvent) -> None:
        extra = {
            "event_type": event.type,
            "tool_name": event.tool_name,
            "tool_class": event.tool_class,
            "agent_role": event.agent_role,
            "from_cache": event.from_cache,
            "duration_seconds": self._duration(event),
        }
        if event.failure:
            extra["failure"] = str(event.failure)
            self.logger.warning("Tool usage finished with failure", extra=extra)
        else:
            self.logger.info("Tool usage finished", extra=extra)

    def _on_tool_error(self, source: Any, event: ToolUsageErrorEvent) -> None:
        self.logger.error("Tool usage error", extra={
            "event_type": event.type,
            "tool_name": event.tool_name,
            "agent_role": event.agent_role,
            "duration_seconds": self._duration(event),
            "error": str(event.error),
        })

    def _on_flow_finished(self, source: Any, event: FlowFinishedEvent) -> None:
        self.logger.info("Flow finished", extra={
            "event_type": event.type,
            "flow_name": event.flow_name,
            "duration_seconds": self._duration(event),
        })

    def _on_flow_failed(self, source: Any, event: FlowFailedEvent) -> None:
        self.logger.error("Flow failed", extra={
            "event_type": event.type,
            "flow_name": event.flow_name,
            "duration_seconds": self._duration(event),
            "error": str(event.error),
        })

    def _on_method_finished(self, source: Any, event: MethodExecutionFinishedEvent) -> None:
        self.logger.info("Flow method finished", extra={
            "event_type": event.type,
            "flow_name": event.flow_name,
            "method_name": event.method_name,
            "duration_seconds": self._duration(event),
        })

    def _on_method_failed(self, source: Any, event: MethodExecutionFailedEvent) -> None:
        self.logger.error("Flow method failed", extra={
            "event_type": event.type,
            "flow_name": event.flow_name,
            "method_name": event.method_name,
            "duration_seconds": self._duration(event),
            "error": str(event.error),
        })