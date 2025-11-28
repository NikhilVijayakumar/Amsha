import os

from nikhil.amsha.crew_forge.sync.manager.sync_crew_config_manager import SyncCrewConfigManager




def main():
    """
    Main function to run the crew configuration synchronization process.
    """
    print("🚀 Starting crew configuration sync job...")

    config_file_path = os.path.join("configs", "job_config.yaml")

    try:
        sync_manager = SyncCrewConfigManager(app_config_path="config/app_config.yaml", job_config_path="config/job_config.yaml")
        sync_manager.sync()

        print("✅ Sync job completed successfully.")

    except (ValueError, FileNotFoundError) as e:
        print(f"❌ An error occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()