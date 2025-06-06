from typing import Optional

from pydantic import BaseModel, Field


class CrewConfigRequest(BaseModel):
    name: str = Field(..., description="The name of the task.")
    agents: dict[str, str] = Field(..., description="Dictionary of agent names to their IDs")
    tasks: dict[str, str] = Field(..., description="Dictionary of task names to their IDs")
    usecase: Optional[str] = Field(None, description="The Usecase or context for the task for its use")


class CrewConfigResponse(BaseModel):
    id: Optional[str] = Field(None, alias="_id", description="MongoDB document ID")
    name: str = Field(..., description="The name of the task.")
    agents: dict[str, str] = Field(..., description="Dictionary of agent names to their IDs")
    tasks: dict[str, str] = Field(..., description="Dictionary of task names to their IDs")
    usecase: Optional[str] = Field(None, description="The Usecase or context for the task for its use")
