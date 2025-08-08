from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional, List

from nikhil.amsha.toolkit.crew_forge.domain.models.task_data import TaskRequest, TaskResponse


class ITaskRepository(ABC):
    """
    Interface for data access operations related to Tasks.
    """
    @abstractmethod
    def create_task(self, task: TaskRequest) -> TaskResponse:
        ...

    @abstractmethod
    def get_task_by_id(self, task_id: str) -> Optional[TaskResponse]:
        ...

    @abstractmethod
    def find_by_name_and_usecase(self, name: str, usecase: str) -> Optional[TaskResponse]:
        ...

    @abstractmethod
    def update_task(self, task_id: str, task: TaskRequest) -> Optional[TaskResponse]:
        ...

    @abstractmethod
    def delete_task(self, task_id: str) -> bool:
        ...

    @abstractmethod
    def get_tasks_by_usecase(self, usecase: str) -> List[TaskResponse]:
        ...