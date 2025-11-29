from pydantic import BaseModel, Field
from typing import List, Optional, Dict

class CrewGenRequest(BaseModel):
    """The initial input protocol provided by the library user."""
    feature_name: str
    description: str
    target_directory: str
    data_directory: str

class ArchitectureBlueprint(BaseModel):
    """Output of the Designer Crew. Input for the Generator Crew."""
    feature_snake_case: str
    package_root: str
    config_root: str
    required_files: List[str]
    twin_structure: Dict[str, str]  # e.g. {'feature': 'path', 'evaluator': 'path'}

class GenerationResult(BaseModel):
    """Output of the Generator Crew. Input for the Optimizer."""
    success: bool
    generated_files: List[str]
    feature_entry_point: str
    evaluator_entry_point: str

class CrewGenState(BaseModel):
    """The Global State object passed through the Flow."""
    request: CrewGenRequest
    blueprint: Optional[ArchitectureBlueprint] = None
    generation: Optional[GenerationResult] = None
    optimization_history: Optional[List[Dict]] = None