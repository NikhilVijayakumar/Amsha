"""
JSON cleaning utilities for output processing.
"""
import json
from pathlib import Path
from typing import Optional


class JsonCleanerUtils:
    """Utility class for cleaning and validating JSON files."""
    
    def __init__(self, input_file_path: str):
        """
        Initialize the JSON cleaner with an input file path.
        
        Args:
            input_file_path: Path to the JSON file to be cleaned
        """
        self.input_file_path = Path(input_file_path)
        self.output_file_path: Optional[str] = None
    
    def process_file(self) -> bool:
        """
        Process and clean the JSON file.
        
        Returns:
            True if the file was successfully processed and is valid JSON, False otherwise
        """
        try:
            # Check if input file exists
            if not self.input_file_path.exists():
                print(f"❌ Input file not found: {self.input_file_path}")
                return False
            
            # Read and parse the JSON file
            with open(self.input_file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            # Try to parse as JSON to validate
            json_data = json.loads(content)
            
            # If we get here, the JSON is valid
            # For now, we'll just use the same file as output
            # In a more sophisticated implementation, this could clean/format the JSON
            self.output_file_path = str(self.input_file_path)
            
            print(f"✅ JSON file is valid: {self.input_file_path}")
            return True
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing error in {self.input_file_path}: {e}")
            return False
        except Exception as e:
            print(f"❌ Error processing file {self.input_file_path}: {e}")
            return False