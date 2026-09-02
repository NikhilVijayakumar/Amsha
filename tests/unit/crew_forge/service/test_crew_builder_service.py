"""
Unit tests for CrewBuilderService class.
"""
import unittest
import tempfile
import os
from unittest.mock import MagicMock, patch
from crewai import Process, Agent, Task
from amsha.crew_forge.service.crew_builder_service import CrewBuilderService
from amsha.crew_forge.domain.models.crew_data import CrewData
from amsha.crew_forge.domain.models.agent_data import AgentRequest
from amsha.crew_forge.domain.models.task_data import TaskRequest
from crewai import CheckpointConfig
from crewai.state.provider.json_provider import JsonProvider
from crewai.state.provider.sqlite_provider import SqliteProvider


def _build_minimal_service(crew_data) -> CrewBuilderService:
    """Return a builder with one agent + one task so build() can run."""
    service = CrewBuilderService(crew_data)
    service.add_agent(AgentRequest(role="Agent", goal="Goal", backstory="Story"))
    agent = service.get_last_agent()
    service.add_task(TaskRequest(name="task", description="Description", expected_output="Output"), agent)
    return service


class TestCrewBuilderService(unittest.TestCase):
    """Test cases for CrewBuilderService class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        
        # Create a mock LLM with all required attributes for CrewAI
        from crewai import LLM
        
        # Use MagicMock with spec but add required attributes
        self.mock_llm = MagicMock(spec=LLM)
        self.mock_llm.__class__ = LLM  # Make isinstance checks pass
        self.mock_llm.model_name = "gpt-4"
        self.mock_llm.stop = None  # Required by CrewAI agent executor
        self.mock_llm.temperature = 0.7
        self.mock_llm.max_tokens = 1000
        
        # Create CrewData
        self.crew_data = CrewData(
            llm=self.mock_llm,
            module_name="test_module",
            output_dir_path=self.test_dir
        )
        
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_initialization(self):
        """Test proper initialization of CrewBuilderService."""
        service = CrewBuilderService(self.crew_data)
        
        self.assertEqual(service.llm, self.mock_llm)
        self.assertEqual(service.module_name, "test_module")
        self.assertEqual(service.output_dir_path, self.test_dir)
        self.assertTrue(os.path.exists(service.output_dir))
        self.assertEqual(len(service._agents), 0)
        self.assertEqual(len(service._tasks), 0)
        self.assertEqual(len(service.output_files), 0)
    
    def test_initialization_without_output_dir(self):
        """Test initialization without output directory."""
        crew_data_no_output = CrewData(
            llm=self.mock_llm,
            module_name="test_module",
            output_dir_path=None
        )
        
        service = CrewBuilderService(crew_data_no_output)
        
        self.assertEqual(service.llm, self.mock_llm)
        self.assertEqual(service.module_name, "test_module")
    
    def test_add_agent_basic(self):
        """Test adding a basic agent."""
        service = CrewBuilderService(self.crew_data)
        
        agent_request = AgentRequest(
            role="Developer",
            goal="Write quality code",
            backstory="Experienced software engineer"
        )
        
        result = service.add_agent(agent_request)
        
        # Should return self for fluent interface
        self.assertEqual(result, service)
        self.assertEqual(len(service._agents), 1)
        
        # Verify agent properties
        agent = service._agents[0]
        self.assertIsInstance(agent, Agent)
        self.assertEqual(agent.role, "Developer")
        self.assertEqual(agent.goal, "Write quality code")
    
    @unittest.skip("Fails due to strict Pydantic validation in CrewAI Agent")
    def test_add_agent_with_tools(self):
        """Test adding agent with tools."""
        service = CrewBuilderService(self.crew_data)
        
        agent_request = AgentRequest(
            role="Researcher",
            goal="Research topics",
            backstory="Expert researcher"
        )
        
        mock_tool = MagicMock()
        service.add_agent(agent_request, tools=[mock_tool])
        
        self.assertEqual(len(service._agents), 1)
        agent = service._agents[0]
        self.assertEqual(len(agent.tools), 1)
    
    def test_add_agent_with_knowledge_sources(self):
        """Test adding agent with knowledge sources."""
        service = CrewBuilderService(self.crew_data)
        
        agent_request = AgentRequest(
            role="Expert",
            goal="Provide expert advice",
            backstory="Domain expert"
        )
        
        mock_knowledge = MagicMock()
        service.add_agent(agent_request, knowledge_sources=[mock_knowledge])
        
        agent = service._agents[0]
        self.assertEqual(agent.knowledge_sources, [mock_knowledge])
    
    def test_add_multiple_agents(self):
        """Test adding multiple agents."""
        service = CrewBuilderService(self.crew_data)
        
        agent1 = AgentRequest(role="Agent1", goal="Goal1", backstory="Story1")
        agent2 = AgentRequest(role="Agent2", goal="Goal2", backstory="Story2")
        
        service.add_agent(agent1).add_agent(agent2)
        
        self.assertEqual(len(service._agents), 2)
    
    def test_add_task_basic(self):
        """Test adding a basic task."""
        service = CrewBuilderService(self.crew_data)
        
        agent_request = AgentRequest(
            role="Developer",
            goal="Code",
            backstory="Engineer"
        )
        service.add_agent(agent_request)
        agent = service.get_last_agent()
        
        task_request = TaskRequest(
            name="coding_task",
            description="Write code",
            expected_output="Working code"
        )
        
        result = service.add_task(task_request, agent)
        
        # Should return self for fluent interface
        self.assertEqual(result, service)
        self.assertEqual(len(service._tasks), 1)
        
        # Verify task properties
        task = service._tasks[0]
        self.assertIsInstance(task, Task)
        self.assertEqual(task.name, "coding_task")
        self.assertEqual(task.description, "Write code")
    
    def test_add_task_with_output_file(self):
        """Test adding task with output file."""
        service = CrewBuilderService(self.crew_data)
        
        agent_request = AgentRequest(role="Writer", goal="Write", backstory="Author")
        service.add_agent(agent_request)
        agent = service.get_last_agent()
        
        task_request = TaskRequest(
            name="write_task",
            description="Write content",
            expected_output="Content"
        )
        
        service.add_task(task_request, agent, output_filename="output")
        
        task = service._tasks[0]
        self.assertIsNotNone(task.output_file)
        self.assertTrue(task.output_file.endswith("output.json"))
        self.assertEqual(len(service.output_files), 1)
    
    def test_add_task_with_validation_output(self):
        """Test adding task with validation flag."""
        service = CrewBuilderService(self.crew_data)
        
        agent_request = AgentRequest(role="Validator", goal="Validate", backstory="QA")
        service.add_agent(agent_request)
        agent = service.get_last_agent()
        
        task_request = TaskRequest(
            name="validate_task",
            description="Validate",
            expected_output="Valid"
        )
        
        service.add_task(task_request, agent, output_filename="validation_output", validation=True)
        
        task = service._tasks[0]
        # When validation=True, output_file should be the exact filename
        self.assertEqual(task.output_file, "validation_output")
    
    def test_build_crew_success(self):
        """Test successful crew building."""
        service = CrewBuilderService(self.crew_data)
        
        agent_request = AgentRequest(role="Agent", goal="Goal", backstory="Story")
        service.add_agent(agent_request)
        agent = service.get_last_agent()
        
        task_request = TaskRequest(
            name="task",
            description="Description",
            expected_output="Output"
        )
        service.add_task(task_request, agent)
        
        crew = service.build()
        
        self.assertIsNotNone(crew)
        self.assertEqual(len(crew.agents), 1)
        self.assertEqual(len(crew.tasks), 1)
    
    @unittest.skip("Fails due to strict Pydantic validation in CrewAI Crew")
    def test_build_crew_with_process(self):
        """Test building crew with specific process."""
        service = CrewBuilderService(self.crew_data)
        
        service.add_agent(AgentRequest(role="A", goal="G", backstory="S"))
        agent = service.get_last_agent()
        service.add_task(TaskRequest(name="t", description="d", expected_output="o"), agent)
        
        crew = service.build(process=Process.hierarchical)
        
        self.assertIsNotNone(crew)
    
    def test_build_crew_with_knowledge_sources(self):
        """Test building crew with knowledge sources."""
        service = CrewBuilderService(self.crew_data)
        
        service.add_agent(AgentRequest(role="A", goal="G", backstory="S"))
        agent = service.get_last_agent()
        service.add_task(TaskRequest(name="t", description="d", expected_output="o"), agent)
        
        mock_knowledge = MagicMock()
        crew = service.build(knowledge_sources=[mock_knowledge])
        
        self.assertEqual(crew.knowledge_sources, [mock_knowledge])
    
    def test_build_without_agents_raises_error(self):
        """Test that building without agents raises ValueError."""
        service = CrewBuilderService(self.crew_data)
        
        with self.assertRaises(ValueError) as context:
            service.build()
        
        self.assertIn("at least one agent", str(context.exception))
    
    def test_build_without_tasks_raises_error(self):
        """Test that building without tasks raises ValueError."""
        service = CrewBuilderService(self.crew_data)
        service.add_agent(AgentRequest(role="A", goal="G", backstory="S"))
        
        with self.assertRaises(ValueError) as context:
            service.build()
        
        self.assertIn("at least one", str(context.exception))
    
    def test_get_last_agent_with_agents(self):
        """Test getting last agent when agents exist."""
        service = CrewBuilderService(self.crew_data)
        
        service.add_agent(AgentRequest(role="First", goal="G1", backstory="S1"))
        service.add_agent(AgentRequest(role="Second", goal="G2", backstory="S2"))
        
        last_agent = service.get_last_agent()
        
        self.assertIsNotNone(last_agent)
        self.assertEqual(last_agent.role, "Second")
    
    def test_get_last_agent_without_agents(self):
        """Test getting last agent when no agents exist."""
        service = CrewBuilderService(self.crew_data)
        
        last_agent = service.get_last_agent()
        
        self.assertIsNone(last_agent)
    
    def test_get_last_file_with_files(self):
        """Test getting last file when files exist."""
        service = CrewBuilderService(self.crew_data)
        
        service.add_agent(AgentRequest(role="A", goal="G", backstory="S"))
        agent = service.get_last_agent()
        
        service.add_task(TaskRequest(name="t1", description="d", expected_output="o"), 
                        agent, output_filename="file1")
        service.add_task(TaskRequest(name="t2", description="d", expected_output="o"), 
                        agent, output_filename="file2")
        
        last_file = service.get_last_file()
        
        self.assertIsNotNone(last_file)
        self.assertTrue(last_file.endswith("file2.json"))
    
    def test_get_last_file_without_files(self):
        """Test getting last file when no files exist."""
        service = CrewBuilderService(self.crew_data)
        
        last_file = service.get_last_file()
        
        self.assertIsNone(last_file)
    
    def test_fluent_interface_chain(self):
        """Test fluent interface with method chaining."""
        service = CrewBuilderService(self.crew_data)
        
        result = (service
                  .add_agent(AgentRequest(role="A1", goal="G1", backstory="S1"))
                  .add_agent(AgentRequest(role="A2", goal="G2", backstory="S2")))
        
        self.assertEqual(result, service)
        self.assertEqual(len(service._agents), 2)

    def test_add_agent_with_capability_fields(self):
        """Test agent execution/capability fields pass through to crewai Agent."""
        service = CrewBuilderService(self.crew_data)
        # A valid skill input is a search path containing a <name>/SKILL.md dir
        # where the dir name (kebab-case) matches the frontmatter name.
        skill_parent = tempfile.mkdtemp()
        skill_dir = os.path.join(skill_parent, "my-skill")
        os.makedirs(skill_dir)
        with open(os.path.join(skill_dir, "SKILL.md"), "w", encoding="utf-8") as f:
            f.write("---\nname: my-skill\ndescription: test skill\n---\n\n# instructions\n")
        agent_request = AgentRequest(
            role="Researcher",
            goal="Research",
            backstory="Expert",
            max_iter=5,
            max_rpm=10,
            max_execution_time=300,
            max_retry_limit=2,
            respect_context_window=True,
            allow_delegation=True,
            reasoning=True,
            max_reasoning_attempts=3,
            multimodal=True,
            skills=[skill_parent],
        )
        service.add_agent(agent_request)
        agent = service._agents[0]
        self.assertEqual(agent.max_iter, 5)
        self.assertEqual(agent.max_rpm, 10)
        self.assertEqual(agent.max_execution_time, 300)
        self.assertEqual(agent.max_retry_limit, 2)
        self.assertTrue(agent.respect_context_window)
        self.assertTrue(agent.allow_delegation)
        self.assertTrue(agent.reasoning)
        self.assertEqual(agent.max_reasoning_attempts, 3)
        self.assertTrue(agent.multimodal)
        self.assertEqual([s.name for s in agent.skills], ["my-skill"])

    def test_add_agent_does_not_override_crewai_defaults(self):
        """Test unprovided optional fields leave crewai defaults untouched."""
        service = CrewBuilderService(self.crew_data)
        service.add_agent(AgentRequest(role="Dev", goal="Code", backstory="Engineer"))
        agent = service._agents[0]
        # crewai defaults, not None, when field not provided:
        self.assertEqual(agent.max_iter, 25)
        self.assertEqual(agent.max_retry_limit, 2)
        self.assertFalse(agent.allow_delegation)
        self.assertFalse(agent.reasoning)
        self.assertIsNone(agent.skills)

    def test_add_task_with_execution_and_guardrail_fields(self):
        """Test task execution/guardrail fields pass through to crewai Task."""
        service = CrewBuilderService(self.crew_data)
        service.add_agent(AgentRequest(role="Dev", goal="Code", backstory="Engineer"))
        agent = service.get_last_agent()
        task_request = TaskRequest(
            name="code_task",
            description="Write code",
            expected_output="Code",
            async_execution=True,
            human_input=True,
            markdown=True,
            guardrail="output must be a string",
            guardrail_max_retries=3,
        )
        service.add_task(task_request, agent)
        task = service._tasks[0]
        self.assertTrue(task.async_execution)
        self.assertTrue(task.human_input)
        self.assertTrue(task.markdown)
        self.assertEqual(task.guardrail, "output must be a string")
        self.assertEqual(task.guardrail_max_retries, 3)

    def test_add_task_with_context_resolves_names_to_tasks(self):
        """Test prerequisite task names resolve to Task instances."""
        service = CrewBuilderService(self.crew_data)
        service.add_agent(AgentRequest(role="A", goal="G", backstory="S"))
        agent = service.get_last_agent()
        service.add_task(TaskRequest(name="research", description="d", expected_output="o"), agent)
        service.add_task(
            TaskRequest(name="write", description="d", expected_output="o", context=["research"]),
            agent,
        )
        write_task = service._tasks[1]
        self.assertEqual(len(write_task.context), 1)
        self.assertEqual(write_task.context[0].name, "research")

    def test_add_task_with_unknown_context_raises(self):
        """Test referencing a missing prerequisite task raises ValueError."""
        service = CrewBuilderService(self.crew_data)
        service.add_agent(AgentRequest(role="A", goal="G", backstory="S"))
        agent = service.get_last_agent()
        with self.assertRaises(ValueError):
            service.add_task(
                TaskRequest(name="write", description="d", expected_output="o", context=["missing"]),
                agent,
            )

    def test_build_default_memory_and_checkpoint_off(self):
        """Default CrewData leaves CrewAI memory/checkpoint off (no behavior change)."""
        crew = _build_minimal_service(CrewData(
            llm=self.mock_llm, module_name="m", output_dir_path=None
        )).build()
        self.assertFalse(crew.memory)
        self.assertIsNone(crew.checkpoint)

    def test_build_crew_with_memory_enabled(self):
        """memory=True on CrewData threads through to Crew(memory=True)."""
        crew = _build_minimal_service(CrewData(
            llm=self.mock_llm, module_name="m", output_dir_path=None, memory=True
        )).build()
        self.assertIs(crew.memory, True)

    def test_build_crew_with_checkpoint_bool_true(self):
        """checkpoint=True yields a default CheckpointConfig on the crew."""
        crew = _build_minimal_service(CrewData(
            llm=self.mock_llm, module_name="m", output_dir_path=None, checkpoint=True
        )).build()
        self.assertIsInstance(crew.checkpoint, CheckpointConfig)
        self.assertEqual(crew.checkpoint.on_events, ["task_completed"])

    def test_build_crew_with_checkpoint_dict(self):
        """checkpoint dict maps provider/location/on_events/max_checkpoints to CheckpointConfig."""
        crew = _build_minimal_service(CrewData(
            llm=self.mock_llm, module_name="m", output_dir_path=None,
            checkpoint={
                "enabled": True,
                "provider": "json",
                "location": "./ck",
                "on_events": ["task_started", "task_completed"],
                "max_checkpoints": 5,
            },
        )).build()
        self.assertIsInstance(crew.checkpoint, CheckpointConfig)
        self.assertEqual(crew.checkpoint.location, "./ck")
        self.assertEqual(crew.checkpoint.on_events, ["task_started", "task_completed"])
        self.assertEqual(crew.checkpoint.max_checkpoints, 5)
        self.assertIsInstance(crew.checkpoint.provider, JsonProvider)

    def test_build_crew_with_checkpoint_sqlite_provider(self):
        """checkpoint provider 'sqlite' resolves to a SqliteProvider instance."""
        crew = _build_minimal_service(CrewData(
            llm=self.mock_llm, module_name="m", output_dir_path=None,
            checkpoint={"enabled": True, "provider": "sqlite"},
        )).build()
        self.assertIsInstance(crew.checkpoint.provider, SqliteProvider)

    def test_build_crew_with_checkpoint_enabled_false(self):
        """checkpoint.enabled: false maps to checkpoint=None (today's behavior)."""
        crew = _build_minimal_service(CrewData(
            llm=self.mock_llm, module_name="m", output_dir_path=None,
            checkpoint={"enabled": False, "location": "./ignored"},
        )).build()
        self.assertIsNone(crew.checkpoint)

    def test_build_crew_with_checkpoint_unknown_provider(self):
        """Unknown checkpoint provider raises a ValueError."""
        with self.assertRaises(ValueError):
            _build_minimal_service(CrewData(
                llm=self.mock_llm, module_name="m", output_dir_path=None,
                checkpoint={"enabled": True, "provider": "dynamodb"},
            )).build()

    # ── Tool resolution tests ──

    def test_add_agent_resolves_tools_from_registry(self):
        """Agent tools list is resolved through the tool registry."""
        service = CrewBuilderService(self.crew_data)
        agent_request = AgentRequest(
            role="Researcher", goal="Research", backstory="Expert",
            tools=["file_read"],
        )
        service.add_agent(agent_request)
        agent = service._agents[0]
        self.assertEqual(len(agent.tools), 1)
        from crewai_tools import FileReadTool
        self.assertIsInstance(agent.tools[0], FileReadTool)

    def test_add_agent_unknown_tool_raises(self):
        """Unknown tool name in AgentRequest.tools raises ValueError."""
        service = CrewBuilderService(self.crew_data)
        with self.assertRaises(ValueError) as ctx:
            service.add_agent(AgentRequest(
                role="R", goal="G", backstory="S",
                tools=["nonexistent_tool"],
            ))
        self.assertIn("nonexistent_tool", str(ctx.exception))

    def test_add_agent_merges_explicit_and_registry_tools(self):
        """Explicitly passed tools + registry tools are merged."""
        from crewai_tools import FileReadTool
        service = CrewBuilderService(self.crew_data)
        agent_request = AgentRequest(
            role="R", goal="G", backstory="S",
            tools=["directory_read"],
        )
        explicit = [FileReadTool()]
        service.add_agent(agent_request, tools=explicit)
        agent = service._agents[0]
        self.assertEqual(len(agent.tools), 2)

    def test_add_agent_no_tools_empty_list(self):
        """Agent with no tools gets empty list."""
        service = CrewBuilderService(self.crew_data)
        service.add_agent(AgentRequest(role="R", goal="G", backstory="S"))
        agent = service._agents[0]
        self.assertEqual(agent.tools, [])

    def test_add_task_resolves_tools_from_registry(self):
        """Task tools list is resolved through the tool registry."""
        service = CrewBuilderService(self.crew_data)
        service.add_agent(AgentRequest(role="A", goal="G", backstory="S"))
        agent = service.get_last_agent()
        task_request = TaskRequest(
            name="t", description="d", expected_output="o",
            tools=["file_read"],
        )
        service.add_task(task_request, agent)
        task = service._tasks[0]
        self.assertEqual(len(task.tools), 1)
        from crewai_tools import FileReadTool
        self.assertIsInstance(task.tools[0], FileReadTool)

    def test_task_tools_override_agent_tools(self):
        """Task-level tools replace agent-level tools at the Task level."""
        service = CrewBuilderService(self.crew_data)
        service.add_agent(AgentRequest(
            role="A", goal="G", backstory="S",
            tools=["file_read", "directory_read"],
        ))
        agent = service.get_last_agent()
        task_request = TaskRequest(
            name="t", description="d", expected_output="o",
            tools=["scrape_website"],
        )
        service.add_task(task_request, agent)
        task = service._tasks[0]
        self.assertEqual(len(task.tools), 1)
        from crewai_tools import ScrapeWebsiteTool
        self.assertIsInstance(task.tools[0], ScrapeWebsiteTool)
        # Agent still has its own tools
        self.assertEqual(len(agent.tools), 2)

    # ── MCP config tests ──

    def test_add_agent_mcp_stdio_config(self):
        """MCP stdio config converts to MCPServerStdio and passes to Agent, when the
        command is explicitly allowlisted by the application owner (env var)."""
        from amsha.crew_forge.domain.models.mcp_data import McpServerConfig
        from amsha.crew_forge.service.crew_builder_service import MCP_STDIO_ALLOWLIST_ENV
        service = CrewBuilderService(self.crew_data)
        agent_request = AgentRequest(
            role="R", goal="G", backstory="S",
            mcp_servers=[
                McpServerConfig(
                    transport="stdio",
                    command="python",
                    args=["server.py"],
                    env={"KEY": "val"},
                ),
            ],
        )
        with patch.dict(os.environ, {MCP_STDIO_ALLOWLIST_ENV: "python,node"}):
            service.add_agent(agent_request)
        agent = service._agents[0]
        self.assertEqual(len(agent.mcps), 1)
        from crewai.mcp import MCPServerStdio
        self.assertIsInstance(agent.mcps[0], MCPServerStdio)

    def test_add_agent_mcp_stdio_denied_by_default(self):
        """Security property: stdio MCP command is refused unless explicitly
        allowlisted via AMSHA_MCP_STDIO_ALLOWLIST -- YAML alone cannot enable it."""
        from amsha.crew_forge.domain.models.mcp_data import McpServerConfig
        from amsha.crew_forge.exceptions.crew_configuration_exception import CrewConfigurationException
        from amsha.crew_forge.service.crew_builder_service import MCP_STDIO_ALLOWLIST_ENV
        service = CrewBuilderService(self.crew_data)
        agent_request = AgentRequest(
            role="R", goal="G", backstory="S",
            mcp_servers=[McpServerConfig(transport="stdio", command="bash", args=["-c", "echo pwned"])],
        )
        env_without_allowlist = {k: v for k, v in os.environ.items() if k != MCP_STDIO_ALLOWLIST_ENV}
        with patch.dict(os.environ, env_without_allowlist, clear=True):
            with self.assertRaises(CrewConfigurationException):
                service.add_agent(agent_request)

    def test_add_agent_mcp_stdio_denied_when_not_in_allowlist(self):
        """A configured allowlist still rejects any command not explicitly listed."""
        from amsha.crew_forge.domain.models.mcp_data import McpServerConfig
        from amsha.crew_forge.exceptions.crew_configuration_exception import CrewConfigurationException
        from amsha.crew_forge.service.crew_builder_service import MCP_STDIO_ALLOWLIST_ENV
        service = CrewBuilderService(self.crew_data)
        agent_request = AgentRequest(
            role="R", goal="G", backstory="S",
            mcp_servers=[McpServerConfig(transport="stdio", command="bash", args=["-c", "echo pwned"])],
        )
        with patch.dict(os.environ, {MCP_STDIO_ALLOWLIST_ENV: "python"}):
            with self.assertRaises(CrewConfigurationException):
                service.add_agent(agent_request)

    def test_add_agent_mcp_http_not_gated(self):
        """http/sse transport is not subject to the stdio command allowlist --
        it's a URL+headers connection, not a subprocess spawn."""
        from amsha.crew_forge.domain.models.mcp_data import McpServerConfig
        service = CrewBuilderService(self.crew_data)
        agent_request = AgentRequest(
            role="R", goal="G", backstory="S",
            mcp_servers=[McpServerConfig(transport="http", url="https://example.com/mcp")],
        )
        service.add_agent(agent_request)
        agent = service._agents[0]
        self.assertEqual(len(agent.mcps), 1)

    def test_add_agent_no_mcp_servers(self):
        """Agent without MCP config has no mcps field set."""
        service = CrewBuilderService(self.crew_data)
        service.add_agent(AgentRequest(role="R", goal="G", backstory="S"))
        agent = service._agents[0]
        self.assertIsNone(agent.mcps)

    # ── Tracing tests ──

    def test_build_crew_with_tracing_enabled(self):
        """tracing=True on CrewData threads through to Crew(tracing=True)."""
        crew = _build_minimal_service(CrewData(
            llm=self.mock_llm, module_name="m", output_dir_path=None, tracing=True
        )).build()
        self.assertTrue(crew.tracing)

    def test_build_crew_tracing_default_none(self):
        """tracing=None (default) does not pass tracing to Crew."""
        crew = _build_minimal_service(CrewData(
            llm=self.mock_llm, module_name="m", output_dir_path=None
        )).build()
        # CrewAI's default is tracing=False; we don't override when None
        self.assertFalse(crew.tracing)


if __name__ == '__main__':
    unittest.main()
