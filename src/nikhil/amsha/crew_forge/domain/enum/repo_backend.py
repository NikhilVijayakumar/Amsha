# src/nikhil/amsha/toolkit/crew_forge/domain/enums/repo_backend.py

from enum import Enum


class RepoBackend(str, Enum):
    MONGO = "mongo"
    IN_MEMORY = "in_memory"
    COSMOS = "cosmos"
