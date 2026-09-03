"""Amsha MCP — a stdio MCP server exposing Amsha's features, modules, and crew-design methodology.

Package layout:
    amsha_mcp/
        server.py         stdio entrypoint, tool registration
        docs_loader.py    target-repo + bundled methodology docs (docs/) from disk
        repo_schemas.py   eager-imports real crew schemas from the target repo (deadlock guard)
        docs/             bundled methodology docs (prerequisite/implementation/proposal)
        tools/            one module per group of tools
            modules.py    list_amsha_modules, explain_module
            install.py    get_install_instructions, get_quickstart
            methodology.py get_prerequisite_stage, get_implementation_guide
            search.py     search_amsha_docs
"""

__version__ = "0.1.0"