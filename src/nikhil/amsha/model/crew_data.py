from pydantic import BaseModel, Field

from src.nikhil.amsha.config.lm_studio_config import LMStudioConfig
from src.nikhil.amsha.repo.agent_repo import AgentRepository
from src.nikhil.amsha.repo.task_repo import TaskRepository


class CrewData(BaseModel):
    llm: LMStudioConfig.ModelNames = Field(..., description="Model name")
    module_name: str = Field(..., description="The name of module")
    agent_repo: AgentRepository = Field(..., description="Agent repo")
    task_repo: TaskRepository = Field(..., description="Task repo")
    output_dir_path: str = Field(..., description="output dir path")
