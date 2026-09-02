# src/nikhil/amsha/toolkit/crew_forge/domain/task_data.py
from typing import List, Optional

from pydantic import BaseModel, Field


class TaskRequest(BaseModel):
    name: str = Field(..., description="The name of the task.")
    description: str = Field(..., description="Description of the task to be performed.")
    expected_output: str = Field(..., description="The expected output or result of the task.")
    usecase: Optional[str] = Field(None, description="The Usecase or context for the task for its use")

    # Execution
    context: Optional[List[str]] = Field(None, description="Names of prerequisite TaskRequests whose output feeds this task.")
    async_execution: Optional[bool] = Field(None, description="Execute this task asynchronously.")
    human_input: Optional[bool] = Field(None, description="Require human input before final output.")
    markdown: Optional[bool] = Field(None, description="Render the task output as markdown.")

    # Guardrails
    guardrail: Optional[str] = Field(None, description="LLM-based guardrail description for validating task output.")
    guardrail_max_retries: Optional[int] = Field(None, description="Maximum retries when the guardrail fails.")
