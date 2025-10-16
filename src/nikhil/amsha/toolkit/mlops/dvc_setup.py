import yaml
import subprocess
from pathlib import Path


class DVCSetup:  # Renamed class for clarity
    """
    Automates the setup of a DVC environment using a YAML configuration file.
    """

    def __init__(self, config_path: str):
        print("🚀 Initializing DVC Environment Setup...")

        # 1. Load configuration from the provided YAML file
        self.config_path = Path(config_path)
        if not self.config_path.exists():
            print(f"❌ Configuration file not found at: {self.config_path}")
            exit(1)

        with self.config_path.open('r') as f:
            self.config = yaml.safe_load(f)

        # 2. Set up paths and configurations from the loaded file
        self.root_dir = Path.cwd()  # Assumes script is run from the project root
        self.input_dir = Path(self.config["domain_root_path"])
        self.output_dir = Path(self.config["output_dir_path"])
        self.gdrive_config = self.config["google_drive"]

        print(f"   - Project Root: {self.root_dir}")
        print(f"   - Input Dir: {self.input_dir}")
        print(f"   - Output Dir: {self.output_dir}")
        print("   - ✅ Configuration loaded successfully.")

    def _run_command(self, command: list):
        """Helper to run shell commands within the project's root directory."""
        try:
            print(f"   - Executing: {' '.join(command)}")
            subprocess.run(command, check=True, text=True, cwd=self.root_dir, capture_output=True)
        except subprocess.CalledProcessError as e:
            print(f"❌ Command failed: {' '.join(command)}")
            print(f"   Error: {e.stderr.strip()}")
            exit(1)
        except FileNotFoundError:
            print("❌ Command 'dvc' not found. Is DVC installed? (pip install dvc dvc-gdrive)")
            exit(1)

    def _create_directories(self):
        """Ensures the input and output directories from the config exist."""
        print("\n📂 Ensuring all necessary directories exist...")
        for dir_path in [self.input_dir, self.output_dir]:
            # Create parent directories if they don't exist
            dir_path.mkdir(parents=True, exist_ok=True)
        print("   - ✅ Directories checked.")

    def _validate_gdrive_config(self):
        """Validates that the GDrive folder ID is present in the config."""
        print("\n🔍 Validating Google Drive configuration...")
        folder_id = self.gdrive_config.get("folder_id")
        if not folder_id or "YOUR" in folder_id:
            print("❌ 'folder_id' not found or not set in your Google Drive configuration.")
            print(f"   - Please add your actual folder ID to '{self.config_path}'.")
            exit(1)
        print("   - ✅ Google Drive folder ID is present.")

    def _configure_dvc(self):
        """Configures DVC to use the Google Drive remote."""
        print("\n🔄 Configuring DVC for Google Drive...")
        if not (self.root_dir / ".dvc").exists():
            self._run_command(["dvc", "init"])
        else:
            print("   - ✅ DVC already initialized.")

        print("   - 🔗 Configuring DVC remote 'gdrive_storage'...")
        folder_id = self.gdrive_config["folder_id"]
        remote_url = f"gdrive://{folder_id}"

        self._run_command(["dvc", "remote", "add", "-d", "gdrive_storage", remote_url, "--force"])

        print("   - ✅ DVC remote 'gdrive_storage' configured.")
        print("   - 💡 NOTE: You may be prompted to authenticate in your browser on the first 'dvc pull' or 'dvc push'.")

    def _pull_data(self):
        """Pulls the latest data from the configured DVC remote."""
        print("\n⏬ Pulling latest data and models from DVC remote...")
        self._run_command(["dvc", "pull"])

    def run(self):
        """Executes the complete setup workflow."""
        self._create_directories()
        self._validate_gdrive_config()
        self._configure_dvc()
        self._pull_data()
        print("\n🎉 Setup and bootstrap complete! Your environment is ready.")


