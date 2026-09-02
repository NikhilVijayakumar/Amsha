"""CrewAI Flow-based orchestration path for multi-crew job_config pipelines.

Additive to ``BaseCrewOrchestrator`` / ``FileCrewOrchestrator``: single-crew
runs keep using ``run_crew()`` unchanged. A ``job_config.yaml`` ``pipeline``
(an ordered list of crew names) can instead be run as a CrewAI ``Flow`` whose
steps each delegate to the injected orchestrator's ``run_crew()`` — so every
crew still gets its execution state, performance monitoring, and CrewAI
checkpoint recording (see proposal 05 wiring in ``BaseCrewOrchestrator``).
"""
import re
from typing import Any, Dict, List, Optional, Type, Union

from pydantic import BaseModel, Field

from crewai import Flow
from crewai.flow import listen, start

from amsha.crew_forge.service.base_crew_orchestrator import BaseCrewOrchestrator
from amsha.execution_runtime.domain.execution_handle import ExecutionHandle
from amsha.execution_runtime.domain.execution_mode import ExecutionMode


class PipelineState(BaseModel):
    """Flow state model mapped from a job_config ``pipeline``.

    ``inputs`` feeds every crew step (one shared input set for the pipeline);
    ``outputs`` accumulates each crew's raw result under its crew name.
    """

    inputs: Dict[str, Any] = Field(default_factory=dict)
    outputs: Dict[str, Any] = Field(default_factory=dict)


class _CrewPipelineFlow(Flow[PipelineState]):
    """Static generic base so dynamic per-pipeline subclasses inherit the typed state."""
    pass


def _crew_method_name(crew_name: str) -> str:
    """Stable Flow method name for a crew (used as the @listen topic)."""
    clean = re.sub(r"\W+", "_", crew_name)
    return f"run_{clean}" if clean else "run_crew"


def _build_flow_class(
    orchestrator: BaseCrewOrchestrator,
    pipeline: List[str],
    filename_suffix: Optional[str],
) -> Type[_CrewPipelineFlow]:
    """Build a ``Flow`` subclass with one @start/@listen method per pipeline crew.

    Each step blocks on ``orchestrator.run_crew(..., INTERACTIVE)`` so the next
    step only fires after its predecessor completes (listener ordering), and
    stores ``result.raw`` (falling back to the raw value) under the crew name.
    """
    methods: Dict[str, Any] = {}

    def _make_step(crew_name: str):
        def step(self: _CrewPipelineFlow):
            result = orchestrator.run_crew(
                crew_name, self.state.inputs, filename_suffix, ExecutionMode.INTERACTIVE
            )
            raw = getattr(result, "raw", result)
            self.state.outputs[crew_name] = raw
            return raw

        return step

    for index, crew_name in enumerate(pipeline):
        method = _make_step(crew_name)
        method.__name__ = _crew_method_name(crew_name)
        if index == 0:
            method = start()(method)
        else:
            method = listen(_crew_method_name(pipeline[index - 1]))(method)
        methods[method.__name__] = method

    return type("CrewPipelineFlow", (_CrewPipelineFlow,), methods)


class FlowCrewOrchestrator:
    """Runs an ordered list of crews as a CrewAI Flow.

    Args:
        orchestrator: Backing orchestrator whose ``run_crew`` executes each
            pipeline step (state tracking + checkpoint recording live here).
        pipeline: Ordered crew names from ``job_config.yaml``'s ``pipeline``.
        filename_suffix: Optional suffix for output files of every crew step.

    Raises:
        ValueError: If ``pipeline`` is empty.
    """

    def __init__(
        self,
        orchestrator: BaseCrewOrchestrator,
        pipeline: List[str],
        filename_suffix: Optional[str] = None,
    ):
        if not pipeline:
            raise ValueError("pipeline must not be empty")
        self.orchestrator = orchestrator
        self.pipeline = list(pipeline)
        self.filename_suffix = filename_suffix
        flow_class = _build_flow_class(orchestrator, pipeline, filename_suffix)
        self.flow: _CrewPipelineFlow = flow_class()

    def kickoff(
        self,
        inputs: Optional[Dict[str, Any]] = None,
        mode: ExecutionMode = ExecutionMode.INTERACTIVE,
    ) -> Union[Dict[str, Any], ExecutionHandle]:
        """Run the pipeline.

        INTERACTIVE blocks and returns ``PipelineState.outputs`` (crew name →
        raw result). BACKGROUND submits the whole flow to the backing
        orchestrator's ``RuntimeEngine`` and returns an ``ExecutionHandle``;
        the wrapper replaces RuntimeEngine's per-crew dispatch, not the
        flow-level async distinction proposal 03 item 4 calls for.
        """
        def _run_pipeline() -> Dict[str, Any]:
            self.flow.kickoff(inputs={"inputs": dict(inputs or {})})
            return self.flow.state.outputs

        if mode == ExecutionMode.BACKGROUND:
            return self.orchestrator.runtime.submit(_run_pipeline, mode=mode)
        return _run_pipeline()

    def get_last_output(self, crew_name: Optional[str] = None) -> Any:
        """Last pipeline output, or a specific crew's output if named."""
        outputs = self.flow.state.outputs
        if crew_name:
            return outputs.get(crew_name)
        return list(outputs.values())[-1] if outputs else None