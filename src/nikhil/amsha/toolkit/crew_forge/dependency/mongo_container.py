# src/nikhil/amsha/toolkit/crew_forge/dependency/mongo_container.py

from dependency_injector import containers, providers

from nikhil.amsha.toolkit.crew_forge.repo.adapters.mongo.agent_repo import AgentRepository
from nikhil.amsha.toolkit.crew_forge.repo.adapters.mongo.task_repo import TaskRepository
from nikhil.amsha.toolkit.crew_forge.repo.adapters.mongo.crew_config_repo import CrewConfigRepository
from nikhil.amsha.toolkit.crew_forge.domain.models.repo_data import RepoData


class MongoRepoContainer(containers.DeclarativeContainer):
    """DI container for Mongo-based repositories."""

    config = providers.Configuration()

    agent_repo = providers.Factory(
        AgentRepository,
        data=providers.Factory(
            RepoData,
            mongo_uri=config.mongo.uri,
            db_name=config.mongo.db_name,
            collection_name="agents",
        ),
    )

    task_repo = providers.Factory(
        TaskRepository,
        data=providers.Factory(
            RepoData,
            mongo_uri=config.mongo.uri,
            db_name=config.mongo.db_name,
            collection_name="tasks",
        ),
    )

    crew_config_repo = providers.Factory(
        CrewConfigRepository,
        data=providers.Factory(
            RepoData,
            mongo_uri=config.mongo.uri,
            db_name=config.mongo.db_name,
            collection_name="crew_configs",
        ),
    )
