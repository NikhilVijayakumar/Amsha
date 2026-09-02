# src/nikhil/amsha/toolkit/crew_forge/domain/agent_data.py
from typing import List, Optional

from pydantic import BaseModel, Field


class AgentRequest(BaseModel):
    role: str = Field(..., description="The role or persona of the agent.")
    goal: str = Field(..., description="The primary objective or goal of the agent.")
    backstory: str = Field(..., description="The backstory or context for the agent.")
    usecase: Optional[str] = Field(None, description="The Usecase or context for the agent for its use")

    # Execution tuning
    max_iter: Optional[int] = Field(None, description="Maximum number of iterations for the agent.")
    max_rpm: Optional[int] = Field(None, description="Maximum requests per minute.")
    max_execution_time: Optional[int] = Field(None, description="Maximum execution time (seconds).")
    max_retry_limit: Optional[int] = Field(None, description="Maximum number of retries on tool failure.")
    respect_context_window: Optional[bool] = Field(None, description="Respect the context window when sending messages.")
    allow_delegation: Optional[bool] = Field(None, description="Allow the agent to delegate tasks to other agents.")

    # Capabilities
    reasoning: Optional[bool] = Field(None, description="Enable reasoning model.")
    max_reasoning_attempts: Optional[int] = Field(None, description="Maximum reasoning attempts when reasoning is enabled.")
    multimodal: Optional[bool] = Field(None, description="Enable multimodal (image/audio) inputs.")
    skills: Optional[List[str]] = Field(None, description="Skill names or paths to attach to the agent.")

    # Prompt customization
    system_template: Optional[str] = Field(None, description="System template override.")
    prompt_template: Optional[str] = Field(None, description="Prompt template override.")
    response_template: Optional[str] = Field(None, description="Response template override.")
