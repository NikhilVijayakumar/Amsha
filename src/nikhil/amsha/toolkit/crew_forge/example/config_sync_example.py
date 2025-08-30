import yaml

from nikhil.amsha.toolkit.crew_forge.dependency.crew_forge_container import CrewForgeContainer

print("--- Running Config Sync Example ---")

# 1. Load configuration from a file
with open("config/app_config.yaml", "r") as f:
    config = yaml.safe_load(f)

# 2. Initialize the DI container
container = CrewForgeContainer()

# 3. Wire the configuration into the container
container.config.from_dict(config)

# 4. Get the config_sync_service from the container
print("\n[Main] Requesting the ConfigSyncService...")
config_sync_service = container.config_sync_service()

# 5. Run the service logic
print("\n[Main] Calling the synchronize method...")
config_sync_service.synchronize()

print("\n--- Config Sync Example Finished ---")