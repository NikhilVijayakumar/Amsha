from typing import Optional

from pymongo.errors import DuplicateKeyError
from bson import ObjectId

from nikhil.amsha.crewai.model import RepoData
from nikhil.amsha.crewai.repo.base_repo import BaseRepository
from nikhil.amsha.crewai.model import CrewConfigRequest, CrewConfigResponse


class CrewConfigRepository(BaseRepository):
    def __init__(self, data: RepoData):
        super().__init__(data)
        self.create_unique_compound_index(["name", "usecase"])

    def create_crew_config(self, crew_config: CrewConfigRequest) -> Optional[CrewConfigResponse]:
        try:
            crew_config_data = crew_config.model_dump(by_alias=True, exclude={"id"})
            result = self.insert_one(crew_config_data)
            if result and result.inserted_id:
                return self.get_crew_config_by_id(str(result.inserted_id))
            return None
        except DuplicateKeyError:
            raise ValueError(
                f"Crew configuration with name '{crew_config.name}' and usecase '{crew_config.usecase}' already exists."
            )

    def get_crew_config_by_id(self, crew_config_id: str) -> Optional[CrewConfigResponse]:
        try:
            obj_id = ObjectId(crew_config_id)
        except Exception:
            raise ValueError("Invalid ObjectId format for crew_config_id")

        crew_config_data = self.find_one({"_id": obj_id})
        if crew_config_data:
            crew_config_data["_id"] = str(crew_config_data["_id"])
            return CrewConfigResponse(**crew_config_data)
        return None

    def update_crew_config(self, crew_config_id: str, crew_config: CrewConfigRequest) -> Optional[CrewConfigResponse]:
        try:
            obj_id = ObjectId(crew_config_id)
        except Exception:
            raise ValueError("Invalid ObjectId format for crew_config_id")

        updated_data = crew_config.model_dump(by_alias=True, exclude_unset=True, exclude={"id"})
        result = self.update_one({"_id": obj_id}, updated_data)

        if result.modified_count > 0:
            return self.get_crew_config_by_id(crew_config_id)
        return None

    def delete_crew_config(self, crew_config_id: str) -> bool:
        try:
            obj_id = ObjectId(crew_config_id)
        except Exception:
            raise ValueError("Invalid ObjectId format for crew_config_id")

        result = self.delete_one({"_id": obj_id})
        return result.deleted_count > 0

    def get_crew_configs_by_usecase(self, usecase: str) -> list[CrewConfigResponse]:
        crew_config_list = self.find_many({"usecase": usecase})
        for crew_config_data in crew_config_list:
            crew_config_data["_id"] = str(crew_config_data["_id"])
        return [CrewConfigResponse(**crew_config_data) for crew_config_data in crew_config_list]

    def get_crew_by_name_and_usecase(self, name: str, usecase: str) -> Optional[CrewConfigResponse]:
        """Retrieves a specific crew configuration by its name and usecase."""
        crew_config_data = self.find_one({"name": name, "usecase": usecase})
        if crew_config_data:
            crew_config_data["_id"] = str(crew_config_data["_id"])
            return CrewConfigResponse(**crew_config_data)
        return None
