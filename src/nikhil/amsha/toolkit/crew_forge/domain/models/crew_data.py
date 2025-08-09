# src/nikhil/amsha/toolkit/crew_forge/domain/crew_data.py
from crewai import LLM
from pydantic import BaseModel, Field, ConfigDict


class CrewData(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    llm: LLM = Field(..., description="Model name")
    module_name: str = Field(..., description="The name of module")
    output_dir_path: str = Field(..., description="output dir path")
