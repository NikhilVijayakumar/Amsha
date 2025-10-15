# src/nikhil/amsha/toolkit/crew_forge/dependency/crew_forge_container.py
from dependency_injector import containers, providers

from nikhil.amsha.toolkit.crew_forge.domain.models.crew_data import CrewData
from nikhil.amsha.toolkit.crew_forge.domain.models.sync_config import SyncConfigData
from nikhil.amsha.toolkit.crew_forge.dependency.mongo_container import MongoRepoContainer
from nikhil.amsha.toolkit.crew_forge.seeding.parser.crew_parser import CrewParser
from nikhil.amsha.toolkit.crew_forge.service.atomic_db_builder import AtomicDbBuilderService
from nikhil.amsha.toolkit.crew_forge.service.atomic_yaml_builder import AtomicYamlBuilderService
from nikhil.amsha.toolkit.crew_forge.service.config_sync_service import ConfigSyncService
from nikhil.amsha.toolkit.crew_forge.service.crew_blueprint_service import CrewBluePrintService
from nikhil.amsha.toolkit.crew_forge.service.crew_builder_service import CrewBuilderService


class CrewForgeContainer(containers.DeclarativeContainer):
    """Main DI container for the application."""
    config = providers.Configuration()

    mongo_container = providers.Container(MongoRepoContainer, config=config)

    # selected_container = providers.Selector(
    #     config.backend,
    #     mongo=mongo_container
    # )

    agent_repo = mongo_container.provided.agent_repo
    task_repo = mongo_container.provided.task_repo
    crew_config_repo = mongo_container.provided.crew_config_repo

    sync_config_data = providers.Callable(
        lambda agent_repo, task_repo, crew_repo, domain_root_path: SyncConfigData(
            agent_repo=agent_repo(),
            task_repo=task_repo(),
            crew_repo=crew_repo(),
            domain_root_path=domain_root_path,
        ),
        agent_repo=agent_repo,
        task_repo=task_repo,
        crew_repo=crew_config_repo,
        domain_root_path=config.domain_root_path,
    )



    crew_parser = providers.Singleton(CrewParser)

    config_sync_service = providers.Factory(
        ConfigSyncService,
        data=sync_config_data.provided,
    )

    crew_data = providers.Dependency(instance_of=CrewData)
    crew_builder_service =providers.Factory(
        CrewBuilderService,
        data=crew_data,
    )

    atomic_db_builder = providers.Factory(
        AtomicDbBuilderService,
        agent_repo=agent_repo(),
        task_repo=task_repo(),

    )

    atomic_yaml_builder = providers.Factory(
        AtomicYamlBuilderService,
        parser=crew_parser,
    data=providers.Factory(CrewData),  # Runtime args for CrewData
        # agent_yaml_file and task_yaml_file are passed when you call the provider
    )

    crew_blueprint_service = providers.Callable(
        lambda crew_repo: CrewBluePrintService(crew_repo=crew_repo()),
        crew_repo=crew_config_repo,
    )


