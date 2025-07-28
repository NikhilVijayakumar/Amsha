from pymongo.errors import DuplicateKeyError
from bson import ObjectId

from nikhil.amsha.crewai.model.agent_data import AgentRequest, AgentResponse
from nikhil.amsha.crewai.model.repo_data import RepoData
from nikhil.amsha.crewai.repo.base_repo import BaseRepository

class AgentRepository(BaseRepository):
    def __init__(self, data: RepoData):
        super().__init__(data)
        # 🛡️ Enforce uniqueness at the database level
        self.create_unique_compound_index(["role", "usecase"])

    def create_agent(self, agent: AgentRequest) -> AgentResponse:
        """Creates a new agent in the database."""
        try:
            agent_data = agent.model_dump(by_alias=True, exclude={"id"})
            result = self.insert_one(agent_data)
            return self.get_agent_by_id(result.inserted_id)
        except DuplicateKeyError:
            raise ValueError(f"Agent with role '{agent.role}' and usecase '{agent.usecase}' already exists.")

    def get_agent_by_id(self, agent_id: str | ObjectId) -> AgentResponse | None:
        """Retrieves an agent by its ID."""
        try:
            obj_id = ObjectId(agent_id)
        except Exception:
            raise ValueError("Invalid ObjectId format")
        agent_data = self.find_one({"_id": obj_id})
        if agent_data:
            return AgentResponse(**agent_data)
        return None

    def find_by_role_and_usecase(self, role: str, usecase: str) -> AgentResponse | None:
        """Finds an agent by its role and usecase."""
        query = {"role": role, "usecase": usecase}
        agent_doc = self.find_one(query)
        if agent_doc:
            return AgentResponse(**agent_doc)
        return None

    def update_agent(self, agent_id: str, agent: AgentRequest) -> AgentResponse | None:
        """Updates an existing agent."""
        updated_data = agent.model_dump()
        try:
            obj_id = ObjectId(agent_id)
        except Exception:
            raise ValueError("Invalid ObjectId format")
        result = self.update_one({"_id": obj_id}, updated_data)
        if result.modified_count > 0:
            return self.get_agent_by_id(agent_id)
        return self.get_agent_by_id(agent_id) # Return existing if no fields were changed

    def delete_agent(self, agent_id: str) -> bool:
        """Deletes an agent by its ID."""
        try:
            obj_id = ObjectId(agent_id)
        except Exception:
            raise ValueError("Invalid ObjectId format")
        result = self.delete_one({"_id": obj_id})
        return result.deleted_count > 0

    def get_agents_by_usecase(self, usecase: str) -> list[AgentResponse]:
        """Retrieves all agents for a given usecase."""
        agent_data_list = self.find_many({"usecase": usecase})
        return [AgentResponse(**agent_data) for agent_data in agent_data_list]