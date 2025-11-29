from pydantic import BaseModel

from amsha.crew_forge.repo.interfaces.i_agent_repository import IAgentRepository
from amsha.crew_forge.repo.interfaces.i_crew_config_repository import ICrewConfigRepository
from amsha.crew_forge.repo.interfaces.i_task_repository import ITaskRepository


class SyncConfigData(BaseModel):
    agent_repo: IAgentRepository
    task_repo: ITaskRepository
    crew_repo: ICrewConfigRepository
    domain_root_path: str

    class Config:
        arbitrary_types_allowed = True
