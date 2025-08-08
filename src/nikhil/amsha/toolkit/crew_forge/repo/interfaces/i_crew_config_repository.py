from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional, List

from nikhil.amsha.toolkit.crew_forge.domain.models.crew_config_data import CrewConfigRequest, CrewConfigResponse


class ICrewConfigRepository(ABC):
    """
    Interface for data access operations related to Crew Configurations.
    """

    @abstractmethod
    def create_crew_config(self, crew_config: CrewConfigRequest) -> Optional[CrewConfigResponse]:
        ...

    @abstractmethod
    def get_crew_config_by_id(self, crew_config_id: str) -> Optional[CrewConfigResponse]:
        ...

    @abstractmethod
    def get_crew_by_name_and_usecase(self, name: str, usecase: str) -> Optional[CrewConfigResponse]:
        ...

    @abstractmethod
    def update_crew_config(self, crew_config_id: str, crew_config: CrewConfigRequest) -> Optional[CrewConfigResponse]:
        ...

    @abstractmethod
    def delete_crew_config(self, crew_config_id: str) -> bool:
        ...

    @abstractmethod
    def get_crew_configs_by_usecase(self, usecase: str) -> List[CrewConfigResponse]:
        ...