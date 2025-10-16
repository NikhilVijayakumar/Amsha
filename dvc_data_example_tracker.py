
from nikhil.amsha.toolkit.mlops.dvc_data_tracker import DVCDataTracker

if __name__ == "__main__":
    CONFIG_FILE_PATH = "config/app_config.yaml"

    print("=============================================")
    print("      Automated DVC Data Sync Tool")
    print("=============================================")

    tracker = DVCDataTracker(config_path=CONFIG_FILE_PATH)

    # Call the new, more robust sync method
    tracker.sync_data()