# nikhil/amsha/crewai/__init__.py

from .model.repo_data import RepoData
from .repo.agent_repo import AgentRepository
from .repo.task_repo import TaskRepository
from .repo.crew_config_repo import CrewConfigRepository
from .seeding import DatabaseSeeder

def synchronize_configs_from_yaml(mongo_uri: str, db_name: str, domain_root_path: str):
    """
    Initializes repositories and runs the database seeder to synchronize
    all YAML-based agent, task, and crew configurations.
    """
    if not all([mongo_uri, db_name, domain_root_path]):
        raise ValueError("mongo_uri, db_name, and domain_root_path must be provided.")

    # Initialize all three repositories
    agent_repo_data = RepoData(mongo_uri=mongo_uri, db_name=db_name, collection_name="agents")
    task_repo_data = RepoData(mongo_uri=mongo_uri, db_name=db_name, collection_name="tasks")
    crew_repo_data = RepoData(mongo_uri=mongo_uri, db_name=db_name, collection_name="crew_configs")

    agent_repo = AgentRepository(agent_repo_data)
    task_repo = TaskRepository(task_repo_data)
    crew_repo = CrewConfigRepository(crew_repo_data)

    # Initialize and run the seeder with all three repositories
    seeder = DatabaseSeeder(
        agent_repo=agent_repo,
        task_repo=task_repo,
        crew_repo=crew_repo
    )
    seeder.synchronize(root_path=domain_root_path)