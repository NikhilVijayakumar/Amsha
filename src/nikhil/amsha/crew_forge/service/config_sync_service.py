# src/nikhil/amsha/toolkit/crew_forge/service/config_sync_service.py
from amsha.crew_forge.domain.models.sync_config import SyncConfigData
from amsha.crew_forge.seeding.database_seeder import DatabaseSeeder


class ConfigSyncService:
    def __init__(self, data: SyncConfigData):
        self.config = data

    def synchronize(self):
        seeder = DatabaseSeeder(
            agent_repo=self.config.agent_repo,
            task_repo=self.config.task_repo,
            crew_repo=self.config.crew_repo
        )
        seeder.synchronize(root_path=self.config.domain_root_path)
