from pathlib import Path
from typing import List, Optional, TextIO
import json

class JSONOutputManager:
    """
    A class to manage JSON file comparison tasks between directories,
    driven by configuration entries.
    """

    def __init__(self, intermediate_dir: str, final_dir: str, output_filepath: Optional[str] = None):
        """
        Initializes the manager with the required paths.

        Args:
            intermediate_dir (str): Path to the intermediate JSON directory.
            final_dir (str): Path to the final JSON directory.
            output_filepath (Optional[str]): Destination path for results JSON.
        """
        self.intermediate_dir = Path(intermediate_dir)
        self.final_dir = Path(final_dir)
        self.output_filepath = output_filepath

    @staticmethod
    def _find_json_files(directory: Path) -> List[Path]:
        """Recursively finds all JSON files in the given directory."""
        if not directory.is_dir():
            print(f"❌ Error: The directory '{directory}' does not exist.")
            return []
        return list(directory.rglob("*.json"))

    @staticmethod
    def _find_unique_files(source_list: List[Path], comparison_list: List[Path]) -> List[Path]:
        """Finds files in source_list not present in comparison_list by filename."""
        comparison_names = {p.name for p in comparison_list}
        return [p for p in source_list if p.name not in comparison_names]

    def _save_to_json(self, data: List[Path]):
        """Saves results to a JSON file."""
        if not self.output_filepath:
            print("ℹ️ No output filepath specified. Skipping JSON export.")
            return

        output_path = Path(self.output_filepath)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump([str(p) for p in data], f, indent=4)

        print(f"\n✅ Results successfully saved to: {output_path}")

    def run_comparison(self) -> List[Path]:
        """Finds unique intermediate files not existing in final directory and optionally saves results."""
        intermediate_files = self._find_json_files(self.intermediate_dir)
        final_files = self._find_json_files(self.final_dir)

        if not intermediate_files:
            print("⚠️ No JSON files found in the intermediate directory.")
        if not final_files:
            print("⚠️ No JSON files found in the final directory.")

        unique_files = self._find_unique_files(intermediate_files, final_files)

        if unique_files:
            print(f"\nFound {len(unique_files)} unique files in '{self.intermediate_dir}':")
            for f in unique_files:
                print(f"  - {f}")
        else:
            print("\nNo unique files found in the intermediate folder.")

        self._save_to_json(unique_files)
        return unique_files