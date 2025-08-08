# src/nikhil/amsha/toolkit/crew_forge/domain/task_data.py
from typing import Optional

from pydantic import BaseModel, Field

class TaskRequest(BaseModel):
    name: str = Field(..., description="The name of the task.")
    description: str = Field(..., description="Description of the task to be performed.")
    expected_output: str = Field(..., description="The expected output or result of the task.")
    usecase: Optional[str] = Field(None, description="The Usecase or context for the task for its use")

class TaskResponse(BaseModel):
    id: Optional[str] = Field(None, alias="_id", description="MongoDB document ID")
    name: str = Field(..., description="The name of the task.")
    description: str = Field(..., description="Description of the task to be performed.")
    expected_output: str = Field(..., description="The expected output or result of the task.")
    usecase: Optional[str] = Field(None, description="The Usecase or context for the task for its use")
