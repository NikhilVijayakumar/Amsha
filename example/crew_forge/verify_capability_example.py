"""
Proposal 08 verification — build the copy crew and confirm the new capability
fields actually land on the crewai.Agent / Task built from the example YAML.

This exercises the REAL path used in production:
    job_config.yaml -> AtomicCrewFileManager.build_atomic_crew()
    -> CrewParser -> AgentRequest/TaskRequest -> CrewBuilderService
    -> crewai.Agent(skills=..., max_iter=..., ...) / Task(context=[...], ...)

Run without args to just build + inspect (no LLM call):
    python example/crew_forge/verify_capability_example.py

Pass --kickoff to also run the crew directly against the configured LLM server
(proposals 01/02/04/06/07/08/09 — single-crew path):
    python example/crew_forge/verify_capability_example.py --kickoff

Pass --pipeline to run the job_config `pipeline` as a real CrewAI Flow against
the configured LLM server (proposal 03/10 — multi-crew Flow path, via the same
production entry point AmshaCrewFileApplication.run_pipeline()):
    python example/crew_forge/verify_capability_example.py --pipeline
"""
import argparse
import sys
from pathlib import Path
from typing import Dict, Any

from amsha.crew_forge.orchestrator.file.amsha_crew_file_application import AmshaCrewFileApplication
from amsha.crew_forge.orchestrator.flow import FlowCrewOrchestrator
from amsha.llm_factory.domain.model.llm_type import LLMType


class _BuildOnlyApplication(AmshaCrewFileApplication):
    """Subclass of the file application that exposes the raw manager/builder build."""

    def build_crew(self, crew_name: str = "copy_crew") -> Any:
        """Build the crew WITHOUT running it, so we can inspect the agents/tasks."""
        return self.orchestrator.manager.build_atomic_crew(crew_name)


def _verify(expected: Any, actual: Any, label: str) -> bool:
    ok = expected == actual
    print(f"  [{'PASS' if ok else 'FAIL'}] {label}: expected={expected!r} got={actual!r}")
    return ok


def main() -> int:
    parser = argparse.ArgumentParser(description="Proposal 08 capability-field verification")
    parser.add_argument("--kickoff", action="store_true", help="also run the crew against the LLM server")
    parser.add_argument("--pipeline", action="store_true", help="also run the job_config pipeline as a real Flow against the LLM server")
    args = parser.parse_args()

    configs: Dict[str, str] = {
        "llm": "example/crew_forge/example_config/llm_config.yaml",
        "app": "example/crew_forge/example_config/app_config.yaml",
        "job": "example/crew_forge/example_config/job_config.yaml",
    }

    app = _BuildOnlyApplication(config_paths=configs, llm_type=LLMType.CREATIVE)

    print("\n== [1] Building copy_crew from example YAML (no LLM call) ==")
    crew = app.build_crew()

    results = []
    for agent in crew.agents:
        print(f"\nAgent role: {agent.role!r}")
        # max_iter came from YAML (explicitly 25)
        results.append(_verify(25, agent.max_iter, f"{agent.role}.max_iter (YAML max_iter: 25)"))
        # allow_delegation default in crewai 1.15.18 is False; YAML set it true -> proves passthrough
        results.append(_verify(True, agent.allow_delegation, f"{agent.role}.allow_delegation (YAML: true, default False)"))
        # reasoning commented out in YAML -> should fall back to crewai default (False)
        results.append(_verify(False, agent.reasoning, f"{agent.role}.reasoning (commented out -> default False)"))
        # skills: "domain-skills" from YAML should resolve to the <module>/skills/domain-skills
        # search path, which crewai then loads into Skill objects (path under .../domain-skills).
        skill_paths = [str(getattr(s, "path", "")).replace("\\", "/") for s in (agent.skills or [])]
        expected_skill_root = "example/crew_forge/example_config/crew_configs/copy/skills/domain-skills"
        results.append(_verify(
            True, any(expected_skill_root in p for p in skill_paths),
            f"{agent.role}.skills loaded from {expected_skill_root} (got {skill_paths})",
        ))

    for task in crew.tasks:
        print(f"\nTask name: {task.name!r}")
        results.append(_verify(True, task.markdown, f"{task.name}.markdown (YAML: true)"))
        results.append(_verify(True, isinstance(task.guardrail, str) and "JSON array" in task.guardrail,
                               f"{task.name}.guardrail set (YAML guardrail)"))
        results.append(_verify(2, task.guardrail_max_retries, f"{task.name}.guardrail_max_retries (YAML: 2)"))

    print("\n== Knowledge sources on crew ==")
    ks = crew.knowledge_sources
    sources = ks if isinstance(ks, list) else [ks]
    json_sources = [s for s in sources if s is not None and getattr(s, "source_type", None) == "json"]
    results.append(_verify(True, len(json_sources) == 1, f"crew has a JSON knowledge source (found {len(json_sources)})"))

    print("\n== Memory & checkpointing (proposals 04/05) ==")
    # memory: true in YAML -> Crew(memory=True)
    results.append(_verify(True, crew.memory is True, f"crew.memory (YAML: true, default False)"))
    # checkpoint dict -> resolved CheckpointConfig carrying the YAML location
    ckpt = crew.checkpoint
    ckpt_location = getattr(ckpt, "location", None)
    results.append(_verify(
        "./.Amsha/execution/checkpoints",
        str(ckpt_location).replace("\\", "/"),
        f"crew.checkpoint.location (YAML location) got={ckpt!r}",
    ))

    print("\n== Flow pipeline (proposal 03) ==")
    pipeline = app.job_config.get("pipeline") or []
    if pipeline:
        flow_orch = FlowCrewOrchestrator(app.orchestrator, pipeline)
        step_name = f"run_{pipeline[0]}"
        results.append(_verify(
            True,
            hasattr(flow_orch.flow, step_name),
            f"flow step '{step_name}' builds from the pipeline without an LLM call",
        ))
    else:
        results.append(_verify(True, False, "job_config declares a pipeline (expected ['copy_crew'])"))

    passed = all(results)
    print(f"\n== Build inspection: {'ALL PASS' if passed else 'SOME FAILED'} ({sum(results)}/{len(results)}) ==")

    if not passed:
        print("Build inspection failed; refusing to run kickoff.")
        return 1

    if args.kickoff:
        print("\n== [2] Running copy_crew.kickoff() against configured LLM server ==")
        result = app.orchestrator.run_crew(crew_name="copy_crew", inputs={})
        print("\n-- CrewOutput raw (first 500 chars) --")
        print(str(getattr(result, "raw", result))[:500])
        out_file = app.orchestrator.get_last_output_file()
        if out_file:
            print(f"\nOutput file: {out_file}")

    if args.pipeline:
        print("\n== [3] Running job_config pipeline as a real Flow (proposal 03/10) ==")
        # Real production entry point -- not FlowCrewOrchestrator directly, so this
        # exercises exactly what a caller running `app.run_pipeline()` would get.
        pipeline_app = AmshaCrewFileApplication(config_paths=configs, llm_type=LLMType.CREATIVE)
        outputs = pipeline_app.run_pipeline()
        print(f"\n-- Pipeline outputs (crew name -> raw, first 300 chars each) --")
        for crew_name, raw in (outputs or {}).items():
            print(f"[{crew_name}] {str(raw)[:300]}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
