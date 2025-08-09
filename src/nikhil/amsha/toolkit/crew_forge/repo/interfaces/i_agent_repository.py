from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional, List

from nikhil.amsha.toolkit.crew_forge.domain.models.agent_data import AgentRequest, AgentResponse


class IAgentRepository(ABC):
    """
    Interface for data access operations related to Agents.
    """

    @abstractmethod
    def create_agent(self, agent: AgentRequest) -> AgentResponse:
        ...

    @abstractmethod
    def get_agent_by_id(self, agent_id: str) -> Optional[AgentResponse]:
        ...

    @abstractmethod
    def find_by_role_and_usecase(self, role: str, usecase: str) -> Optional[AgentResponse]:
        ...

    @abstractmethod
    def update_agent(self, agent_id: str, agent: AgentRequest) -> Optional[AgentResponse]:
        ...

    @abstractmethod
    def delete_agent(self, agent_id: str) -> bool:
        ...

    @abstractmethod
    def get_agents_by_usecase(self, usecase: str) -> List[AgentResponse]:
        ...
