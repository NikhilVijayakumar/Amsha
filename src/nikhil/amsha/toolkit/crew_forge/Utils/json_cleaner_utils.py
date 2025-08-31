import json
import re
import os
from pathlib import Path  # Import the Path object
from typing import Any, Optional


class JsonCleanerUtils:
    """
    A class to read an LLM output file, clean its JSON content,
    and save it to a derived, unique file path.
    """

    def __init__(self, input_file_path: str):
        """
        Initializes the cleaner with a single source file path.
        The output path is derived automatically.

        Args:
            input_file_path (str): The full path to the input file.
        """
        self.input_file_path = Path(input_file_path)

        # Derive the base output path and then find a unique version of it
        base_output_path = self._derive_output_path()
        self.output_file_path = self._get_unique_filepath(base_output_path)

        self._ensure_output_dir_exists()

    def _derive_output_path(self) -> Path:
        """
        Derives the target output path based on the input path.
        - Replaces 'intermediate' with 'final'.
        - Removes dynamic timestamp folders (e.g., 'output_20250826105817').
        """
        # 1. Replace 'intermediate' with 'final'
        # The path is treated as a string for this simple replacement
        path_str = str(self.input_file_path).replace("intermediate", "final", 1)

        # 2. Reconstruct the path, removing the dynamic folder
        p = Path(path_str)
        # Regex to match the dynamic folder pattern 'output_YYYYMMDDHHMMSS'
        # We build a new list of path parts, excluding the dynamic one
        filtered_parts = [part for part in p.parts if not re.match(r"output_\d+", part)]

        return Path(*filtered_parts)

    @staticmethod
    def _get_unique_filepath(base_path: Path) -> Path:
        """
        Checks if the base path exists. If so, appends a counter
        to the filename to make it unique (e.g., file_1.json, file_2.json).
        """
        if not base_path.exists():
            return base_path  # Path is already unique

        directory = base_path.parent
        filename_stem = base_path.stem  # Filename without extension
        extension = base_path.suffix

        count = 1
        while True:
            new_filename = f"{filename_stem}_{count}{extension}"
            new_path = directory / new_filename
            if not new_path.exists():
                return new_path
            count += 1

    def _ensure_output_dir_exists(self):
        """Ensures the directory for the final output file exists."""
        self.output_file_path.parent.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _clean_and_parse_string(content: str) -> Optional[Any]:
        """(Unchanged) Parses a JSON string, removing markdown fences."""
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            match = re.search(r"```(?:json)?\s*\n(.*?)\n\s*```", content, re.DOTALL)
            if match and (cleaned_str := match.group(1)):
                try:
                    return json.loads(cleaned_str)
                except json.JSONDecodeError:
                    return None
        return None

    def process_file(self) -> bool:
        """
        Main method to execute the full read, clean, and write process.
        """
        try:
            content = self.input_file_path.read_text(encoding='utf-8')
        except FileNotFoundError:
            print(f"❌ Error: Input file not found at {self.input_file_path}")
            return False

        return self.process_content(content)

    def process_content(self,content:str) -> bool:
        """
        Main method to execute the full read, clean, and write process.
        """

        parsed_data = self._clean_and_parse_string(content)

        if parsed_data:
            self.output_file_path.write_text(json.dumps(parsed_data, indent=4), encoding='utf-8')
            print(f"✅ Successfully processed and saved to {self.output_file_path}")
            return True
        else:
            print(f"❌ Failed to parse JSON from {self.input_file_path}. No file written.")
            return False


