# src/nikhil/amsha/crew_forge/service/tool_registry.py
"""Lightweight registry mapping string names to crewai tool classes.

Tools are instantiated with defaults on resolution; callers can extend
the registry via ``register_tool`` for custom tools.
"""
from typing import Any, Callable, Dict, Type

from crewai.tools import BaseTool


_REGISTRY: Dict[str, Type[BaseTool]] = {}


def register_tool(name: str, tool_cls: Type[BaseTool]) -> None:
    """Register a custom tool class under *name*."""
    if not (isinstance(tool_cls, type) and issubclass(tool_cls, BaseTool)):
        raise TypeError(f"Expected a BaseTool subclass, got {tool_cls!r}")
    _REGISTRY[name] = tool_cls


def resolve_tools(names: list[str]) -> list[BaseTool]:
    """Resolve a list of tool names to instantiated BaseTool objects.

    Raises ``ValueError`` for any unrecognised name.
    """
    tools = []
    for name in names:
        tool_cls = _REGISTRY.get(name)
        if tool_cls is None:
            available = ", ".join(sorted(_REGISTRY)) or "(none)"
            raise ValueError(
                f"Unknown tool '{name}'. Available tools: {available}"
            )
        tools.append(tool_cls())
    return tools


def available_tools() -> list[str]:
    """Return sorted list of registered tool names."""
    return sorted(_REGISTRY.keys())


# ── Built-in tools (imported lazily to avoid hard dependency at import time) ──

def _bootstrap() -> None:
    """Populate the registry with commonly needed crewai-tools."""
    if _REGISTRY:
        return
    from crewai_tools import FileReadTool, DirectoryReadTool, ScrapeWebsiteTool
    _REGISTRY.update({
        "file_read": FileReadTool,
        "directory_read": DirectoryReadTool,
        "scrape_website": ScrapeWebsiteTool,
    })


_bootstrap()
