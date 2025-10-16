from nikhil.amsha.toolkit.mlops.dvc_setup import DVCSetup

if __name__ == "__main__":
    CONFIG_FILE_PATH = "config/app_config.yaml"

    print("=============================================")
    print("      DVC Environment Setup Tool")
    print("=============================================")

    # Create an instance of the setup class with the path to the config file
    setup = DVCSetup(config_path=CONFIG_FILE_PATH)  # Renamed instantiation

    # Run the setup process
    setup.run()