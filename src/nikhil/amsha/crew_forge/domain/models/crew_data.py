# src/nikhil/amsha/toolkit/crew_forge/domain/crew_data.py
from typing import Any, Dict, Optional, Union

from crewai.llms.base_llm import BaseLLM
from pydantic import BaseModel, Field, ConfigDict


class CrewData(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    llm: BaseLLM = Field(..., description="Model name")
    module_name: str = Field(..., description="The name of module")
    output_dir_path: Optional[str] = Field(..., description="output dir path")
    memory: bool = Field(
        default=False,
        description="Whether the crew uses CrewAI's unified memory",
    )
    checkpoint: Optional[Union[bool, Dict[str, Any]]] = Field(
        default=None,
        description=(
            "Checkpoint configuration: a bool to enable/disable CrewAI checkpointing, "
            "or a dict with keys enabled/on_events/provider/location/max_checkpoints."
        ),
    )
    tracing: Optional[bool] = Field(
        default=None,
        description=(
            "Enable CrewAI native tracing (sends full prompt/response content "
            "to CrewAI's hosted dashboard). Off by default — requires crewai login."
        ),
    )
