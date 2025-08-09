# src/nikhil/amsha/toolkit/crew_forge/adapters/mongo/crew_config_repo.py
from bson import ObjectId
from pymongo.errors import DuplicateKeyError

from nikhil.amsha.toolkit.crew_forge.domain.models.repo_data import RepoData
from nikhil.amsha.toolkit.crew_forge.domain.models.task_data import TaskRequest, TaskResponse
from nikhil.amsha.toolkit.crew_forge.repo.adapters.mongo.mongo_repository import MongoRepository
from nikhil.amsha.toolkit.crew_forge.repo.interfaces.i_task_repository import ITaskRepository


class TaskRepository(MongoRepository, ITaskRepository):
    def __init__(self, data: RepoData):
        super().__init__(data)
        # 🛡️ Enforce uniqueness at the database level
        self.create_unique_compound_index(["name", "usecase"])

    def create_task(self, task: TaskRequest) -> TaskResponse:
        """Creates a new task in the database."""
        try:
            result = self.insert_one(task.model_dump())
            return self.get_task_by_id(result.inserted_id)
        except DuplicateKeyError:
            raise ValueError(f"Task with name '{task.name}' and usecase '{task.usecase}' already exists.")

    def get_task_by_id(self, task_id: str | ObjectId) -> TaskResponse | None:
        """Retrieves a task by its ID."""
        try:
            obj_id = ObjectId(task_id)
        except Exception:
            raise ValueError("Invalid ObjectId format")
        task_data = self.find_one({"_id": obj_id})
        if task_data:
            task_data["_id"] = str(task_data["_id"])
            return TaskResponse(**task_data)
        return None

    def find_by_name_and_usecase(self, name: str, usecase: str) -> TaskResponse | None:
        """Finds a task by its name and usecase."""
        query = {"name": name, "usecase": usecase}
        task_doc = self.find_one(query)
        if task_doc:
            task_doc["_id"] = str(task_doc["_id"])
            return TaskResponse(**task_doc)
        return None

    def update_task(self, task_id: str, task: TaskRequest) -> TaskResponse | None:
        """Updates an existing task."""
        updated_data = task.model_dump()
        try:
            obj_id = ObjectId(task_id)
        except Exception:
            raise ValueError("Invalid ObjectId format")
        result = self.update_one({"_id": obj_id}, updated_data)
        if result.modified_count > 0:
            return self.get_task_by_id(task_id)
        return self.get_task_by_id(task_id)  # Return existing if no fields were changed

    def delete_task(self, task_id: str) -> bool:
        """Deletes a task by its ID."""
        try:
            obj_id = ObjectId(task_id)
        except Exception:
            raise ValueError("Invalid ObjectId format")
        return self.delete_one({"_id": obj_id})

    def get_tasks_by_usecase(self, usecase: str) -> list[TaskResponse]:
        """Retrieves all tasks for a given usecase."""
        task_data_list = self.find_many({"usecase": usecase})
        return [TaskResponse(**task_data) for task_data in task_data_list]
