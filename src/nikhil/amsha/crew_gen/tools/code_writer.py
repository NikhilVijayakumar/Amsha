import os
from crewai_tools import BaseTool
from pydantic import Field


class AmshaCodeWriterTool(BaseTool):
    name: str = "Amsha Code Writer"
    description: str = "Writes code or configuration to a specific file path. Automatically creates directories if they don't exist."

    file_path: str = Field(...,
                           description="The absolute or relative path where the file should be saved (e.g., src/impl/novel/crew.py)")
    content: str = Field(..., description="The full string content to write into the file.")

    def _run(self, file_path: str, content: str) -> str:
        try:
            # Ensure directory exists
            directory = os.path.dirname(file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)

            # Write file
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

            return f"✅ Successfully wrote to {file_path}"
        except Exception as e:
            return f"❌ Error writing file: {str(e)}"