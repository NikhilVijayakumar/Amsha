from pydantic import BaseModel, Field, ConfigDict

from nikhil.amsha.repo.agent_repo import AgentRepository
from nikhil.amsha.repo.task_repo import TaskRepository


class CrewData(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    llm: str = Field(..., description="Model name")
    module_name: str = Field(..., description="The name of module")
    agent_repo: AgentRepository = Field(..., description="Agent repo")
    task_repo: TaskRepository = Field(..., description="Task repo")
    output_dir_path: str = Field(..., description="output dir path")
