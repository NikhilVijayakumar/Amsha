from pymongo.errors import DuplicateKeyError


from bson import ObjectId

from nikhil.amsha.model.agent_data import AgentRequest, AgentResponse
from nikhil.amsha.model.repo_data import RepoData
from nikhil.amsha.repo.base_repo import BaseRepository


class AgentRepository(BaseRepository):
    def __init__(self, data: RepoData):
        super().__init__(data)

    def create_agent(self, agent: AgentRequest):
        """Creates a new agent in the database."""
        try:
            agent_data = agent.model_dump(by_alias=True, exclude={"id"})
            result = self.insert_one(agent_data)
            if result:
                return self.get_agent_by_id(result.inserted_id)
            return result

        except DuplicateKeyError:
            raise ValueError(f"Agent with ID '{agent.agent_id}' already exists.")

    def get_agent_by_id(self, agent_id: str):
        """Retrieves an agent by its ID."""
        try:
            obj_id = ObjectId(agent_id)
        except Exception:
            raise ValueError("Invalid ObjectId format")
        agent_data = self.find_one({"_id": obj_id})
        if agent_data:
            agent_data["_id"] = str(agent_data["_id"])
            return AgentResponse(**agent_data)
        return None

    def update_agent(self, agent_id: str, agent: AgentRequest):
        """Updates an existing agent."""
        updated_data = agent.model_dump()
        result = self.update_one({"_id": agent_id}, updated_data)
        if result.modified_count > 0:
            return self.get_agent_by_id(agent_id)
        return None

    def delete_agent(self, agent_id: str):
        """Deletes an agent by its ID."""
        result = self.delete_one({"_id": agent_id})
        return result.deleted_count > 0

    def get_agents_by_usecase(self, usecase: str):
        agent_data_list = self.find_many({"usecase": usecase})
        for agent_data in agent_data_list:
            agent_data["_id"] = str(agent_data["_id"])
        return [AgentResponse(**agent_data) for agent_data in agent_data_list]
