# services/config_sync_service.py

from nikhil.amsha.crewai.repo.agent_repo import AgentRepository
from nikhil.amsha.crewai.repo.task_repo import TaskRepository
from nikhil.amsha.crewai.repo.crew_config_repo import CrewConfigRepository
from nikhil.amsha.crewai.model.repo_data import RepoData
from nikhil.amsha.crewai.seeding.database_seeder import DatabaseSeeder

class ConfigSyncService:

    def __init__(self, mongo_uri: str, db_name: str, domain_root_path: str):
        if not all([mongo_uri, db_name, domain_root_path]):
            raise ValueError("mongo_uri, db_name, and domain_root_path must be provided.")

        self.domain_root_path = domain_root_path

        # Setup repositories
        agent_repo_data = RepoData(mongo_uri=mongo_uri, db_name=db_name, collection_name="agents")
        task_repo_data = RepoData(mongo_uri=mongo_uri, db_name=db_name, collection_name="tasks")
        crew_repo_data = RepoData(mongo_uri=mongo_uri, db_name=db_name, collection_name="crew_configs")

        self.agent_repo = AgentRepository(agent_repo_data)
        self.task_repo = TaskRepository(task_repo_data)
        self.crew_repo = CrewConfigRepository(crew_repo_data)


    def synchronize(self):
        seeder = DatabaseSeeder(
            agent_repo=self.agent_repo,
            task_repo=self.task_repo,
            crew_repo=self.crew_repo
        )
        seeder.synchronize(root_path=self.domain_root_path)