# src/nikhil/amsha/toolkit/crew_forge/domain/crew_data.py
from typing import Optional

from crewai.llms.base_llm import BaseLLM
from pydantic import BaseModel, Field, ConfigDict


class CrewData(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    llm: BaseLLM = Field(..., description="Model name")
    module_name: str = Field(..., description="The name of module")
    output_dir_path: Optional[str] = Field(..., description="output dir path")
