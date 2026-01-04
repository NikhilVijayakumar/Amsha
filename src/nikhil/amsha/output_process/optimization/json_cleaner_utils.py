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

    def __init__(self, input_file_path: str,output_folder: Optional[str] = None):
        """
        Initializes the cleaner with a single source file path.
        The output path is derived automatically.

        Args:
            input_file_path (str): The full path to the input file.
            output_folder: output folder inside final directory. if not provided will be ignored
        """
        self.input_file_path = Path(input_file_path)
        self.output_folder = output_folder

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
        path_str = str(self.input_file_path).replace("intermediate", "final", 1)

        # 2. Reconstruct the path, removing the dynamic folder
        p = Path(path_str)
        # Regex to match the dynamic folder pattern 'output_YYYYMMDDHHMMSS'
        # We build a new list of path parts, excluding the dynamic one
        filtered_parts = [part for part in p.parts if not re.match(r"output_\d+", part)]

        if self.output_folder:
            try:
                # Find the index of the 'output' folder to use as a anchor
                output_idx = filtered_parts.index("output")

                # Insert the category (Photosynthesis) immediately after 'output'
                new_parts = (
                        filtered_parts[:output_idx + 1] +
                        [self.output_folder] +
                        filtered_parts[output_idx + 1:]
                )
                return Path(*new_parts)
            except ValueError:
                new_parts = filtered_parts[:-1] + [self.output_folder] + [filtered_parts[-1]]
                return Path(*new_parts)

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
        """
        Cleans and parses JSON strings, even if:
        - There’s junk text above ```json or ``` fences.
        - There are multiple JSON objects concatenated (e.g., {...}{...}).
        - There are stray quotes or escape errors in keys/values.
        """

        # If content contains ```json, keep only what comes after it.
        if "```json" in content:
            # Keep only the text after the first ```json
            content = content.split("```json", 1)[1]
            # Remove any trailing ``` at the end
            content = re.sub(r"```$", "", content.strip(), flags=re.MULTILINE)
        elif "```" in content:
            # Handle ``` without 'json'
            content = content.split("```", 1)[1]
            content = re.sub(r"```$", "", content.strip(), flags=re.MULTILINE)

        # Remove any markdown fences that survived
        content = re.sub(r"^```(?:json)?", "", content, flags=re.MULTILINE).strip()
        content = re.sub(r"```$", "", content, flags=re.MULTILINE).strip()

        # Try direct JSON parsing
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            pass

        # Handle multiple concatenated JSON objects like {...}{...}
        json_objects = re.findall(r"\{.*?\}", content, re.DOTALL)
        if json_objects:
            try:
                parsed_objects = [json.loads(obj) for obj in json_objects]
                # If there’s only one valid JSON, return that; else return a list
                return parsed_objects[0] if len(parsed_objects) == 1 else parsed_objects
            except json.JSONDecodeError:
                pass

        # Try to fix minor double-quote issues (e.g., '"Cliffhanger" Hook')
        fixed = re.sub(r'"\s*([\'"])', '"', content)
        try:
            return json.loads(fixed)
        except json.JSONDecodeError:
            print("❌ JSON cleaning failed. Could not parse content.")
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
        print(f"process_content:parsed_data\n{parsed_data}")

        if parsed_data:
            self.output_file_path.write_text(json.dumps(parsed_data, indent=4), encoding='utf-8')
            print(f"✅ Successfully processed and saved to {self.output_file_path}")
            return True
        else:
            print(f"❌ Failed to parse JSON from {self.input_file_path}. No file written.")
            return False


