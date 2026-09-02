"""
Unit tests for CrewParser field parsing, including new capability fields.
"""
import unittest
import tempfile
import os

from amsha.crew_forge.seeding.parser.crew_parser import CrewParser


class TestCrewParser(unittest.TestCase):
    """Test cases for CrewParser."""

    def setUp(self):
        self.parser = CrewParser()
        self.tmp_dir = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp_dir)

    def _write(self, content: str) -> str:
        path = os.path.join(self.tmp_dir, "config.yaml")
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return path

    def test_parse_agent_basic(self):
        """Test legacy 3-field agent YAML still parses."""
        path = self._write("agent:\n  role: r\n  goal: g\n  backstory: b\n")
        agent = self.parser.parse_agent(path)
        self.assertEqual(agent.role, "r")
        self.assertEqual(agent.goal, "g")
        self.assertEqual(agent.backstory, "b")
        self.assertIsNone(agent.reasoning)
        self.assertIsNone(agent.max_iter)

    def test_parse_agent_with_capability_fields(self):
        """Test new optional agent fields flow through from YAML."""
        path = self._write(
            "agent:\n"
            "  role: r\n"
            "  goal: g\n"
            "  backstory: b\n"
            "  reasoning: true\n"
            "  max_iter: 5\n"
            "  skills: [web_search]\n"
        )
        agent = self.parser.parse_agent(path)
        self.assertTrue(agent.reasoning)
        self.assertEqual(agent.max_iter, 5)
        self.assertEqual(agent.skills, ["web_search"])

    def test_parse_task_with_capability_fields(self):
        """Test new optional task fields flow through from YAML."""
        path = self._write(
            "task:\n"
            "  name: n\n"
            "  description: d\n"
            "  expected_output: o\n"
            "  async_execution: true\n"
            "  context: [research]\n"
        )
        task = self.parser.parse_task(path)
        self.assertTrue(task.async_execution)
        self.assertEqual(task.context, ["research"])

    def test_parse_task_basic(self):
        """Test legacy 3-field task YAML still parses."""
        path = self._write("task:\n  name: n\n  description: d\n  expected_output: o\n")
        task = self.parser.parse_task(path)
        self.assertEqual(task.name, "n")
        self.assertIsNone(task.async_execution)
        self.assertIsNone(task.context)

    def test_parse_agent_with_tools(self):
        """Test tools field flows through from YAML."""
        path = self._write(
            "agent:\n"
            "  role: r\n"
            "  goal: g\n"
            "  backstory: b\n"
            "  tools: [file_read, directory_read]\n"
        )
        agent = self.parser.parse_agent(path)
        self.assertEqual(agent.tools, ["file_read", "directory_read"])

    def test_parse_agent_with_mcp_servers(self):
        """Test mcp_servers field flows through from YAML."""
        path = self._write(
            "agent:\n"
            "  role: r\n"
            "  goal: g\n"
            "  backstory: b\n"
            "  mcp_servers:\n"
            "    - transport: stdio\n"
            "      command: python\n"
            "      args: [server.py]\n"
        )
        agent = self.parser.parse_agent(path)
        self.assertEqual(len(agent.mcp_servers), 1)
        self.assertEqual(agent.mcp_servers[0].transport, "stdio")
        self.assertEqual(agent.mcp_servers[0].command, "python")

    def test_parse_task_with_tools(self):
        """Test task tools field flows through from YAML."""
        path = self._write(
            "task:\n"
            "  name: n\n"
            "  description: d\n"
            "  expected_output: o\n"
            "  tools: [scrape_website]\n"
        )
        task = self.parser.parse_task(path)
        self.assertEqual(task.tools, ["scrape_website"])


if __name__ == '__main__':
    unittest.main()