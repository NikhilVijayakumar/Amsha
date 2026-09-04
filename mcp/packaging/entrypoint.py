"""PyInstaller entry point — thin wrapper so a real .py script exists to bundle.
Equivalent to the amsha-mcp console script (amsha_mcp.server:main)."""
from amsha_mcp.server import main

if __name__ == "__main__":
    main()
