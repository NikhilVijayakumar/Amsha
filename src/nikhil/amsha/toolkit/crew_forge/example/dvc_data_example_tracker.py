
from nikhil.amsha.toolkit.mlops.dvc_data_tracker import DVCDataTracker

if __name__ == "__main__":
    CONFIG_FILE_PATH = "config/app_config.yaml"

    print("=============================================")
    print("      Automated DVC Data Tracking Tool")
    print("=============================================")

    tracker = DVCDataTracker(config_path=CONFIG_FILE_PATH)
    tracker.commit_and_push()