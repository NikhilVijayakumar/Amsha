"""
Unit tests for the tool registry: name→class mapping, resolution, and extension.
"""
import unittest

from crewai.tools import BaseTool

from amsha.crew_forge.service.tool_registry import (
    available_tools,
    register_tool,
    resolve_tools,
)


class DummyTool(BaseTool):
    name: str = "dummy_tool"
    description: str = "A dummy tool for testing"

    def _run(self) -> str:
        return "dummy"


class TestToolRegistry(unittest.TestCase):

    def test_resolve_builtin_tools(self):
        """Built-in tools resolve without error."""
        tools = resolve_tools(["file_read", "directory_read", "scrape_website"])
        self.assertEqual(len(tools), 3)
        for t in tools:
            self.assertIsInstance(t, BaseTool)

    def test_resolve_unknown_tool_raises(self):
        """Unknown tool name raises ValueError with available names."""
        with self.assertRaises(ValueError) as ctx:
            resolve_tools(["nonexistent_tool"])
        self.assertIn("nonexistent_tool", str(ctx.exception))

    def test_resolve_empty_list(self):
        """Empty input returns empty output."""
        self.assertEqual(resolve_tools([]), [])

    def test_register_custom_tool(self):
        """Custom tool can be registered and resolved."""
        register_tool("dummy", DummyTool)
        tools = resolve_tools(["dummy"])
        self.assertEqual(len(tools), 1)
        self.assertIsInstance(tools[0], DummyTool)

    def test_register_non_base_tool_raises(self):
        """Registering a non-BaseTool class raises TypeError."""
        with self.assertRaises(TypeError):
            register_tool("bad", str)

    def test_available_tools_includes_builtins(self):
        """available_tools() returns sorted list including built-ins."""
        names = available_tools()
        self.assertIn("file_read", names)
        self.assertIn("directory_read", names)
        self.assertIn("scrape_website", names)
        self.assertEqual(names, sorted(names))


if __name__ == "__main__":
    unittest.main()
