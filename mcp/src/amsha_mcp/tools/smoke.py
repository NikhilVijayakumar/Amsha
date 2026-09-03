from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

from crewai.llms.base_llm import BaseLLM

_SMOKE_TIMEOUT_SECONDS = 30.0


class _StubLLM(BaseLLM):
    """Offline stand-in for a CrewAI LLM. Build never calls kickoff(), so the
    no-op call/acall are never reached; they exist only to satisfy the ABC."""

    def call(self, *args, **kwargs):
        raise RuntimeError("smoke_test stub LLM cannot actually generate; build is offline by design")

    async def acall(self, *args, **kwargs):
        return self.call(*args, **kwargs)


def _parse_one(model_cls, data: dict) -> Optional[str]:
    try:
        model_cls(**data)
        return None
    except Exception as e:
        return f"{type(e).__name__}: {e}"


def dry_run_parse(crew_dir: str | Path) -> dict:
    """Fastest gate: parse every agent/task YAML against the real Pydantic
    schemas (CrewParser's models) with NO execution.

    Args:
        crew_dir: path to the crew configuration directory.

    Returns:
        dict with {'ok', 'parsed': [files], 'errors': [{file, error}], 'summary'}.
    """
    import yaml
    from amsha.crew_forge.domain.models.agent_data import AgentRequest
    from amsha.crew_forge.domain.models.task_data import TaskRequest

    root = Path(crew_dir)
    if not root.exists():
        return {"ok": False, "parsed": [], "errors": [{"file": str(root), "error": "directory not found"}],
                "summary": "crew directory not found"}

    parsed: list[dict] = []
    errors: list[dict] = []

    for f in sorted(root.glob("agents/*_agent.yaml")):
        data = (yaml.safe_load(f.read_text(encoding="utf-8")) or {}).get("agent", {})
        err = _parse_one(AgentRequest, data)
        (errors if err else parsed).append({"file": str(f), "error": err} if err else {"file": str(f), "type": "agent"})

    for f in sorted(root.glob("tasks/*_task.yaml")):
        data = (yaml.safe_load(f.read_text(encoding="utf-8")) or {}).get("task", {})
        err = _parse_one(TaskRequest, data)
        (errors if err else parsed).append({"file": str(f), "error": err} if err else {"file": str(f), "type": "task"})

    ok = not errors and bool(parsed)
    return {"ok": ok, "parsed": parsed, "errors": errors,
            "summary": f"parsed {len(parsed)} definition(s), {len(errors)} error(s)"}


def _build_crew(crew_dir: str | Path, module_name: str, output_dir: str) -> dict:
    """Parse + assemble the crew graph offline. Runs in a subprocess so a hung
    build can be killed by the hard timeout rather than joining a stuck thread."""
    import traceback

    root = Path(crew_dir)
    if not root.exists():
        return {"ok": False, "agents": 0, "tasks": 0,
                "summary": f"crew directory not found: {root}", "traceback": ""}
    try:
        from amsha.crew_forge.domain.models.crew_data import CrewData
        from amsha.crew_forge.seeding.parser.crew_parser import CrewParser
        from amsha.crew_forge.service.atomic_yaml_builder import AtomicYamlBuilderService
    except Exception:
        return {"ok": False, "agents": 0, "tasks": 0,
                "summary": f"could not import builders: {traceback.format_exc().splitlines()[-1]}",
                "traceback": traceback.format_exc()}

    crew_data = CrewData(
        llm=_StubLLM(model="stub-offline"), module_name=module_name,
        output_dir_path=str(Path(output_dir)),
        memory=False, checkpoint=None, tracing=None,
    )

    parser = CrewParser()
    agent_files = sorted(root.glob("agents/*_agent.yaml"))
    task_files = sorted(root.glob("tasks/*_task.yaml"))
    built = 0
    total = 0
    errors: list[str] = []
    for af in agent_files:
        for tf in task_files:
            total += 1
            try:
                builder = AtomicYamlBuilderService(
                    data=crew_data, parser=parser,
                    agent_yaml_file=str(af), task_yaml_file=str(tf))
                builder.add_agent()
                builder.add_task(agent=builder.get_last_agent())
                if builder.build() is not None:
                    built += 1
            except Exception as e:
                errors.append(f"{af.name}+{tf.name}: {type(e).__name__}: {e}")
    ok = built == total and total > 0 and not errors
    return {"ok": ok, "agents": len(agent_files), "tasks": len(task_files),
            "summary": f"assembled {built}/{total} crew(s) from {len(agent_files)} agent(s) x {len(task_files)} task(s)",
            "traceback": "\n".join(errors)}


def _worker_main() -> int:
    """Subprocess entrypoint: reads args from argv, prints JSON result to stdout."""
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("crew_dir")
    p.add_argument("--module", default="module")
    p.add_argument("--output", default=".Amsha/smoke")
    a = p.parse_args()
    print(json.dumps(_build_crew(a.crew_dir, a.module, a.output)))
    return 0


def smoke_test(crew_dir: str | Path, module_name: str = "module",
               output_dir: str | Path = ".Amsha/smoke") -> dict:
    """Bounded smoke test: parse AND assemble the crew graph offline through the
    real CrewParser + AtomicYamlBuilderService, under a hard subprocess timeout.

    Runs the build in an isolated subprocess so a hung build is killed, never a
    stuck thread. Offline stub LLM; never kickoff() and never the network.

    Args:
        crew_dir: path to the crew configuration directory.
        module_name: module name passed into CrewData.
        output_dir: scratch output dir path for CrewData.

    Returns:
        dict with {'ok', 'agents', 'tasks', 'summary', 'traceback'}.
    """
    import tempfile

    src = str(Path(__file__).resolve().parent.parent.parent)
    code = (
        "import sys; sys.path.insert(0, {src!r}); "
        "from amsha_mcp.tools.smoke import _worker_main; sys.exit(_worker_main())"
    ).format(src=src)
    env = dict(os.environ)
    env.setdefault("PYTHONIOENCODING", "utf-8")
    try:
        proc = subprocess.run(
            [sys.executable, "-c", code, str(crew_dir), "--module", module_name,
             "--output", str(output_dir)],
            capture_output=True, text=True, timeout=_SMOKE_TIMEOUT_SECONDS, env=env,
            stdin=subprocess.DEVNULL,
        )
    except subprocess.TimeoutExpired:
        return {"ok": False, "agents": 0, "tasks": 0,
                "summary": f"smoke test exceeded {_SMOKE_TIMEOUT_SECONDS}s timeout",
                "traceback": "timeout"}
    try:
        return json.loads(proc.stdout.strip())
    except json.JSONDecodeError:
        return {"ok": False, "agents": 0, "tasks": 0,
                "summary": f"smoke worker failed ({proc.returncode})",
                "traceback": (proc.stderr or proc.stdout)[-2000:]}


if __name__ == "__main__":
    raise SystemExit(_worker_main())
