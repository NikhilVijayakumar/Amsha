from crewai import LLM
from pydantic import BaseModel, Field, ConfigDict

from nikhil.amsha.crewai.repo.agent_repo import AgentRepository
from nikhil.amsha.crewai.repo.task_repo import TaskRepository


class CrewData(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    llm:LLM = Field(..., description="Model name")
    module_name: str = Field(..., description="The name of module")
    agent_repo: AgentRepository = Field(..., description="Agent repo")
    task_repo: TaskRepository = Field(..., description="Task repo")
    output_dir_path: str = Field(..., description="output dir path")
