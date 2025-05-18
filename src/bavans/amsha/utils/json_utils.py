import json
from typing import Any, Dict

class JsonUtils:

    def load_json(self, json_file: str) -> Dict[str, Any]:
        try:
            with open(json_file, 'r', encoding='utf8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Error: JSON file not found at {json_file}")
            return {}
        except json.JSONDecodeError:
            print(f"Error: Could not decode JSON from {json_file}")
            return {}

