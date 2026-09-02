# src/nikhil/amsha/crew_forge/domain/models/mcp_data.py
"""MCP server configuration models for YAML config-as-code.

These models constrain what's expressible in YAML — no raw dict passthrough.
"""
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class McpServerConfig(BaseModel):
    """Structured MCP server configuration — Amsha's YAML-facing schema.

    ``transport`` discriminates which fields are relevant:
    - ``stdio``: ``command`` + ``args`` + ``env``
    - ``http`` / ``sse``: ``url`` + ``headers``
    """

    transport: Literal["stdio", "http", "sse"] = Field(
        ...,
        description="MCP transport type.",
    )
    # stdio fields
    command: Optional[str] = Field(
        None,
        description="Command to execute for stdio transport (e.g. 'python', 'node').",
    )
    args: Optional[List[str]] = Field(
        None,
        description="Command arguments for stdio transport.",
    )
    env: Optional[Dict[str, str]] = Field(
        None,
        description="Environment variables for stdio transport (replaces parent env).",
    )
    # http / sse fields
    url: Optional[str] = Field(
        None,
        description="Server URL for http/sse transport.",
    )
    headers: Optional[Dict[str, str]] = Field(
        None,
        description="HTTP headers for http/sse transport (e.g. auth tokens).",
    )
    # common
    connect_timeout: int = Field(
        30,
        description="Connection timeout in seconds.",
    )
