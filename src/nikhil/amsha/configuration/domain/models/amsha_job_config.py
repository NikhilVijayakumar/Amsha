from typing import List, Dict, Union, Any, Optional
from pydantic import BaseModel, Field

class CrewStep(BaseModel):
    task_key: str = Field(..., description="Task reference key")
    agent_key: str = Field(..., description="Agent reference key")

class CrewDefinition(BaseModel):
    steps: List[CrewStep] = Field(..., description="List of steps executed by the crew")
    knowledge_sources: Optional[List[str]] = Field(None, description="List of knowledge source paths")
    input: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = Field(None, description="Input definitions for the crew")
    memory: bool = Field(
        False,
        description="Whether the crew uses CrewAI's unified memory",
    )
    checkpoint: Optional[Union[bool, Dict[str, Any]]] = Field(
        None,
        description=(
            "Checkpoint configuration: a bool to enable/disable CrewAI checkpointing, "
            "or a dict with keys enabled/on_events/provider/location/max_checkpoints."
        ),
    )

class AmshaJobConfig(BaseModel):
    """
    Job Orchestration Configuration.
    Requires explicit validation of all structured job definitions.
    """
    crew_name: str = Field(..., description="Name of the overall crew execution job")
    usecase: str = Field(..., description="Usecase context for execution")
    module_name: str = Field(..., description="Module name for categorization")
    output_filepath: str = Field(..., description="File path indicating where final output is saved")
    
    crews: Dict[str, CrewDefinition] = Field(..., description="Dictionary mapping crew identifiers to their definitions")
    pipeline: List[str] = Field(..., description="Ordered list of crews defining execution sequence")
