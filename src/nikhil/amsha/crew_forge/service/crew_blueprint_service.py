# src/nikhil/amsha/toolkit/crew_forge/service/crew_blueprint_service.py
from typing import Optional, List

from nikhil.amsha.crew_forge.domain.models.crew_config_data import CrewConfigResponse
from nikhil.amsha.crew_forge.repo.interfaces.i_crew_config_repository import ICrewConfigRepository


class CrewBluePrintService:
    def __init__(self, crew_repo: ICrewConfigRepository):
        print("CrewBluePrintService __init__")
        self.crew_repo: ICrewConfigRepository = crew_repo

    def get_config(self, name: str, usecase: str) -> Optional[CrewConfigResponse]:
        return self.crew_repo.get_crew_by_name_and_usecase(name, usecase)

    def get_all_config(self) -> List[CrewConfigResponse]:
        print("CrewBluePrintService get_all_config")
        return self.crew_repo.get_all_crew_configs()
