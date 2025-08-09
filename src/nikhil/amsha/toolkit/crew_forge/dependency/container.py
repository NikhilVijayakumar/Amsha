from dependency_injector import containers, providers

from nikhil.amsha.toolkit.crew_forge.domain.models.crew_data import CrewData
from nikhil.amsha.toolkit.crew_forge.domain.models.sync_config import SyncConfigData
from nikhil.amsha.toolkit.crew_forge.dependency.mongo_container import MongoRepoContainer
from nikhil.amsha.toolkit.crew_forge.service.config_sync_service import ConfigSyncService
from nikhil.amsha.toolkit.crew_forge.service.crew_blueprint_service import CrewBluePrintService
from nikhil.amsha.toolkit.crew_forge.service.crew_builder_service import CrewBuilderService


class Container(containers.DeclarativeContainer):
    """Main DI container for the application."""
    config = providers.Configuration()

    mongo_container = providers.Container(MongoRepoContainer, config=config)

    selected_container = providers.Selector(
        config.backend,
        mongo=mongo_container
    )

    agent_repo = selected_container.provided.agent_repo
    task_repo = selected_container.provided.task_repo
    crew_config_repo = selected_container.provided.crew_config_repo

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

    config_sync_service = providers.Factory(
        ConfigSyncService,
        data=sync_config_data.provided,
    )

    crew_builder_service = providers.Callable(
        lambda llm, agent_repo, task_repo, module_name, output_dir_path: CrewBuilderService(
            data=CrewData(llm=llm, module_name=module_name, output_dir_path=output_dir_path),
            agent_repo=agent_repo(),
            task_repo=task_repo(),
        ),
        agent_repo=agent_repo,
        task_repo=task_repo
    )

    crew_blueprint_service = providers.Callable(
        lambda crew_repo: CrewBluePrintService(crew_repo=crew_repo()),
        crew_repo=crew_config_repo,
    )
