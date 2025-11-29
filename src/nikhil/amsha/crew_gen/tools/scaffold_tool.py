import os
from pathlib import Path

from crewai.tools import BaseTool
from pydantic import Field


class AmshaStructScaffolderTool(BaseTool):
    name: str = "Amsha Structure Scaffolder"
    description: str = (
        "Creates the standardized Amsha directory structure for a new feature. "
        "It sets up a Python package for the feature and creates separate configuration "
        "folders for agents, tasks, metrics, and job configs."
    )

    base_path: str = Field(
        ...,
        description="The root directory where the feature should be created (e.g., 'src/nikhil/impl')."
    )
    feature_name: str = Field(
        ...,
        description="The technical name of the feature (snake_case), which will be the folder name (e.g., 'seed_plot_crew')."
    )

    def _run(self, base_path: str, feature_name: str) -> str:
        try:
            # Construct the root path for this specific feature
            # e.g. src/nikhil/impl/seed_plot_crew
            root = Path(base_path) / feature_name

            # 1. Create Python Source Directory (The Feature Package)
            if not root.exists():
                root.mkdir(parents=True, exist_ok=True)

            # Critical: Create __init__.py so Python treats this as a package
            (root / "__init__.py").touch()

            # 2. Create Config Directory Structure
            # We need a 'config' folder containing specific subfolders
            config_root = root / "config"

            subdirs = [
                "agents",  # For agents.yaml
                "tasks",  # For tasks.yaml
                "metrics",  # For rubric.json
                "job"  # For job_config.yaml
            ]

            created_paths = []

            for sub in subdirs:
                # e.g. src/nikhil/impl/seed_plot_crew/config/agents
                dir_path = config_root / sub
                dir_path.mkdir(parents=True, exist_ok=True)
                created_paths.append(str(dir_path))

                # Note: We do NOT add __init__.py to config folders
                # because they contain YAML/JSON, not importable Python code.

            return (
                f"✅ Scaffolding Complete for '{feature_name}':\n"
                f"   - Python Package Root: {root}\n"
                f"   - Config Structure: {config_root}/[{', '.join(subdirs)}]"
            )

        except Exception as e:
            return f"❌ Error scaffolding directories: {str(e)}"