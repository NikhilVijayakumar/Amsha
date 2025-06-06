from typing import Optional

from pydantic import BaseModel, Field

class AgentRequest(BaseModel):
    role: str = Field(..., description="The role or persona of the agent.")
    goal: str = Field(..., description="The primary objective or goal of the agent.")
    backstory: str = Field(..., description="The backstory or context for the agent.")
    usecase: Optional[str] = Field(None, description="The Usecase or context for the agent for its use")


class AgentResponse(BaseModel):
    id: Optional[str] = Field(None, alias="_id", description="MongoDB document ID")
    role: str = Field(..., description="The role or persona of the agent.")
    goal: str = Field(..., description="The primary objective or goal of the agent.")
    backstory: str = Field(..., description="The backstory or context for the agent.")
    usecase: Optional[str] = Field(None, description="The Usecase or context for the agent for its use")
