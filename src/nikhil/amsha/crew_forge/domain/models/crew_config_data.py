# src/nikhil/amsha/toolkit/crew_forge/domain/crew_config_data.py
from typing import Optional

from pydantic import BaseModel, Field


class CrewConfigRequest(BaseModel):
    name: str = Field(..., description="The name of the crew.")
    agents: dict[str, str] = Field(..., description="Dictionary of agent names to their IDs")
    tasks: dict[str, str] = Field(..., description="Dictionary of task names to their IDs")
    usecase: Optional[str] = Field(None, description="The Usecase or context for the crew for its use")


class CrewConfigResponse(BaseModel):
    id: Optional[str] = Field(None, alias="_id", description="document ID")
    name: str = Field(..., description="The name of the crew.")
    agents: dict[str, str] = Field(..., description="Dictionary of agent names to their IDs")
    tasks: dict[str, str] = Field(..., description="Dictionary of task names to their IDs")
    usecase: Optional[str] = Field(None, description="The Usecase or context for the crew for its use")
