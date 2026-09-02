# src/nikhil/amsha/toolkit/crew_forge/service/crew_builder_service.py
import os
import time
import typing
from typing import Optional
from amsha.common.logger import get_logger

from crewai import Crew, Agent, Process, Task, CheckpointConfig
from crewai.state.provider.json_provider import JsonProvider
from crewai.state.provider.sqlite_provider import SqliteProvider

from amsha.crew_forge.domain.models.agent_data import AgentRequest
from amsha.crew_forge.domain.models.crew_data import CrewData
from amsha.crew_forge.domain.models.mcp_data import McpServerConfig
from amsha.crew_forge.domain.models.task_data import TaskRequest
from amsha.crew_forge.exceptions.crew_configuration_exception import CrewConfigurationException
from amsha.crew_forge.service.tool_registry import resolve_tools

MCP_STDIO_ALLOWLIST_ENV = "AMSHA_MCP_STDIO_ALLOWLIST"


def _stdio_command_allowed(command: Optional[str]) -> bool:
    """Check a stdio MCP command against the application-owner-controlled allowlist.

    Default-deny: AMSHA_MCP_STDIO_ALLOWLIST is unset or empty -> no stdio command
    is permitted. This is intentional -- stdio MCP config (command/args/env) is a
    real subprocess-execution surface, and Amsha's agent/task YAML is meant to be
    author-editable, version-controlled config-as-code. Gating on an env var (set
    by whoever deploys/runs Amsha, not by the YAML author) keeps that surface out
    of the config-as-code trust boundary.
    """
    allowlist = {c.strip() for c in os.environ.get(MCP_STDIO_ALLOWLIST_ENV, "").split(",") if c.strip()}
    return bool(command) and command in allowlist


def _mcp_config_to_crewai(cfg: McpServerConfig):
    """Convert an Amsha McpServerConfig to the corresponding CrewAI MCP object."""
    if cfg.transport == "stdio":
        if not _stdio_command_allowed(cfg.command):
            raise CrewConfigurationException(
                f"MCP stdio command {cfg.command!r} is not permitted. Stdio MCP servers "
                f"launch a real subprocess, so they must be explicitly allowlisted by the "
                f"application owner via the {MCP_STDIO_ALLOWLIST_ENV} environment variable "
                f"(comma-separated exact command values) -- YAML config alone cannot enable it."
            )
        from crewai.mcp import MCPServerStdio
        return MCPServerStdio(
            command=cfg.command,
            args=cfg.args or [],
            env=cfg.env,
        )
    elif cfg.transport in ("http", "sse"):
        from crewai.mcp import MCPServerHTTP
        return MCPServerHTTP(url=cfg.url, headers=cfg.headers or {})
    else:
        raise ValueError(f"Unsupported MCP transport: {cfg.transport!r}")


class CrewBuilderService:

    def __init__(self, data: CrewData):
        self.logger = get_logger("crew_forge.builder")
        self.llm = data.llm
        self.module_name = data.module_name
        self.memory = data.memory
        self.checkpoint = data.checkpoint
        self.tracing = data.tracing
        if data.output_dir_path:
            timestamp = time.strftime("%Y%m%d%H%M%S")
            self.output_dir_path = data.output_dir_path
            self.output_dir = os.path.join(
                f"{self.output_dir_path}/output/{self.module_name}/output_{timestamp}/")
            self._create_output_dir()
        self._agents = []
        self._tasks = []
        self.output_files = []




    def _create_output_dir(self):
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def add_agent(self, agent_details: AgentRequest,knowledge_sources=None, tools: list = None) -> 'CrewBuilderService':

        if not agent_details:
            raise ValueError("Agent details must be provided.")

        # Resolve tool names from registry, merge with any explicitly passed tools
        resolved_tools = list(tools or [])
        if agent_details.tools:
            resolved_tools.extend(resolve_tools(agent_details.tools))

        agent_kwargs = {
            "role": agent_details.role,
            "goal": agent_details.goal,
            "backstory": agent_details.backstory,
            "llm": self.llm,
            "tools": resolved_tools
        }

        # MCP server config → CrewAI MCP objects
        if agent_details.mcp_servers:
            agent_kwargs["mcps"] = [
                _mcp_config_to_crewai(cfg) for cfg in agent_details.mcp_servers
            ]

        for field in ("max_iter", "max_rpm", "max_execution_time", "max_retry_limit",
                      "respect_context_window", "allow_delegation", "reasoning",
                      "max_reasoning_attempts", "multimodal", "skills",
                      "system_template", "prompt_template", "response_template"):
            value = getattr(agent_details, field, None)
            if value is not None:
                agent_kwargs[field] = value
        agent = Agent(**agent_kwargs)
        if knowledge_sources:
            agent.knowledge_sources = knowledge_sources

        self._agents.append(agent)
        return self

    def add_task(self, task_details: TaskRequest, agent: Agent, output_filename: str = None,
                 validation:bool=False, output_json: typing.Any = None) -> 'CrewBuilderService':
        self.logger.debug("Building crew task", extra={
            "output_filename": output_filename
        })

        if not task_details:
            raise ValueError(f"Task with name '{task_details.name}' not found.")

        task_kwargs = {
            "name": task_details.name,
            "description": task_details.description,
            "expected_output": task_details.expected_output,
            "agent": agent
        }

        # Task-level tools override agent-level tools
        if task_details.tools:
            task_kwargs["tools"] = resolve_tools(task_details.tools)

        for field in ("async_execution", "human_input", "markdown",
                      "guardrail", "guardrail_max_retries"):
            value = getattr(task_details, field, None)
            if value is not None:
                task_kwargs[field] = value
        if task_details.context:
            task_kwargs["context"] = self._resolve_context(task_details.context)
        task = Task(**task_kwargs)
        if output_filename:
            if validation:
                output_file = output_filename
            else:
                output_file = os.path.join(self.output_dir, f"{output_filename}.json")
            self.output_files.append(output_file)
            task.output_file = output_file

        if output_json:
            task.output_json = output_json


        self._tasks.append(task)
        return self

    def _resolve_context(self, context_names: list) -> list:
        """
        Resolve prerequisite task names to the actual Task instances previously
        added to this builder (CrewAI's `Task(context=[...])` expects Task
        objects, not names).
        """
        tasks_by_name = {task.name: task for task in self._tasks}
        resolved = []
        for name in context_names:
            task = tasks_by_name.get(name)
            if task is None:
                raise ValueError(
                    f"Context task '{name}' not found. Prerequisite tasks must be added before the task that references them."
                )
            resolved.append(task)
        return resolved

    def _coerce_checkpoint(self, raw) -> typing.Optional[typing.Union[bool, CheckpointConfig]]:
        """Map a YAML checkpoint block (bool or dict) to what Crew accepts.

        - ``None``/``False`` -> ``None`` (checkpointing off, today's behavior)
        - ``True`` -> ``True`` (CrewAI defaults)
        - dict -> ``enabled: false`` yields ``None``; otherwise the remaining
          keys map onto ``CheckpointConfig(on_events, provider, location,
          max_checkpoints)``, with the provider name resolved to a Json/Sqlite
          provider instance.
        """
        if raw is None or raw is False:
            return None
        if raw is True:
            return True
        config = dict(raw)
        if config.get("enabled", True) is False:
            return None
        config.pop("enabled", None)
        provider = config.pop("provider", None)
        if provider is not None:
            provider_instance = {
                "json": JsonProvider(),
                "sqlite": SqliteProvider(),
            }.get(provider.lower() if isinstance(provider, str) else "")
            if provider_instance is None:
                raise ValueError(
                    f"Unknown checkpoint provider '{provider}'. "
                    "Expected 'json' or 'sqlite'."
                )
            config["provider"] = provider_instance
        return CheckpointConfig(**config)

    def build(self, process: Process = Process.sequential,knowledge_sources=None) -> Crew:
        if not self._agents or not self._tasks:
            raise ValueError("A crew must have at least one agent and one task.")

        # CrewAI 1.8.0: stream=True causes immediate return with streaming output object
        # Remove it to allow normal execution
        crew_kwargs = {
            "agents": self._agents,
            "tasks": self._tasks,
            "process": process,
            "verbose": True,
            "stream": True,
            "memory": self.memory,
            "checkpoint": self._coerce_checkpoint(self.checkpoint),
        }
        if self.tracing is not None:
            crew_kwargs["tracing"] = self.tracing
        crew = Crew(**crew_kwargs)
        if knowledge_sources:
            crew.knowledge_sources = knowledge_sources
        return crew

    def get_last_agent(self) -> Optional[Agent]:
        """
        Returns the most recently added agent, or None if no agents have been added. 🧑‍✈️
        """
        return self._agents[-1] if self._agents else None

    def get_last_file(self) -> Optional[str]:
        """
        Returns the most recently added output files, or None if no output files have been added. 🧑‍✈
        """
        return self.output_files[-1] if self.output_files else None
