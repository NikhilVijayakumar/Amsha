from bson import ObjectId
from pymongo.errors import DuplicateKeyError



from src.nikhil.amsha.model.repo_data import RepoData
from src.nikhil.amsha.model.task_data import TaskRequest, TaskResponse
from src.nikhil.amsha.repo.base_repo import BaseRepository


class TaskRepository(BaseRepository):
    def __init__(self, data:RepoData):
        super().__init__(data)

    def create_task(self, task: TaskRequest):
        """Creates a new task in the database."""
        try:
            result = self.insert_one(task.model_dump())
            if result:
                return self.get_task_by_id(result.inserted_id)
            return result
        except DuplicateKeyError:
            raise ValueError(f"Task with ID '{task.task_id}' already exists.")

    def get_task_by_id(self, task_id: str):
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


    def update_task(self, task_id: str, task: TaskRequest):
        """Updates an existing task."""
        updated_data = task.model_dump()
        result = self.update_one({"task_id": task_id}, updated_data)
        if result.modified_count > 0:
            return self.get_task_by_id(task_id)
        return None

    def delete_task(self, task_id: str):
        """Deletes a task by its ID."""
        result = self.delete_one({"task_id": task_id})
        return result.deleted_count > 0

    def get_tasks_by_usecase(self,usecase: str):
        """Retrieves a list of all tasks."""
        task_data_list = self.find_many({"usecase": usecase})
        for task_data in task_data_list:
            task_data["_id"] = str(task_data["_id"])
        return [TaskResponse(**task_data) for task_data in task_data_list]


