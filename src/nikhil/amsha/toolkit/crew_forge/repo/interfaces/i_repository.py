# src/nikhil/amsha/toolkit/crew_forge/interfaces/i_repository.py
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Optional, List


class IRepository(ABC):
    """
    A generic repository interface defining common data access methods.
    """

    @abstractmethod
    def find_one(self, query: dict) -> Optional[Any]:
        ...

    @abstractmethod
    def find_many(self, query: dict) -> List[Any]:
        ...

    @abstractmethod
    def insert_one(self, data: dict) -> Any:
        ...

    @abstractmethod
    def update_one(self, query: dict, data: dict) -> Any:
        ...

    @abstractmethod
    def delete_one(self, query: dict) -> bool:
        ...
