import subprocess
from pathlib import Path

from nikhil.amsha.utils.yaml_utils import YamlUtils


class DVCSetup:
    """
    Automates DVC setup for both NEW and EXISTING projects.
    It intelligently decides whether to push initial data or pull existing data.
    """
    def __init__(self, config_path: str):
        # ... (no changes in __init__)
        print("🚀 Initializing DVC Environment Setup...")
        self.config_path = Path(config_path)
        if not self.config_path.exists():
            print(f"❌ Configuration file not found at: {self.config_path}")
            exit(1)
        self.config = YamlUtils.yaml_safe_load(config_path)
        self.root_dir = Path.cwd()
        self.input_dir = Path(self.config["domain_root_path"])
        self.output_dir = Path(self.config["output_dir_path"])
        self.gdrive_config = self.config["google_drive"]
        print(f"   - Project Root: {self.root_dir}")
        print(f"   - Input Dir: {self.input_dir}")
        print(f"   - Output Dir: {self.output_dir}")
        print("   - ✅ Configuration loaded successfully.")


    def _run_command(self, command: list, check=True):
        # ... (no changes in _run_command)
        try:
            print(f"   - Executing: {' '.join(command)}")
            result = subprocess.run(command, check=check, text=True, cwd=self.root_dir, capture_output=True)
            if result.stderr and check:
                 print(f"   - Info: {result.stderr.strip()}")
            return result
        except subprocess.CalledProcessError as e:
            print(f"❌ Command failed: {' '.join(command)}")
            print(f"   Error: {e.stderr.strip()}")
            exit(1)
        except FileNotFoundError:
            print("❌ Command 'dvc' not found. Is DVC installed? (pip install dvc dvc-gdrive)")
            exit(1)


    def _create_directories(self):
        # ... (no changes here)
        print("\n📂 Ensuring all necessary directories exist...")
        for dir_path in [self.input_dir, self.output_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        print("   - ✅ Directories checked.")


    def _validate_gdrive_config(self):
        # ... (no changes here)
        print("\n🔍 Validating Google Drive configuration...")
        required_keys = ["folder_id", "gdrive_client_id", "gdrive_client_secret"]
        for key in required_keys:
            value = self.gdrive_config.get(key)
            if not value or "YOUR_" in value:
                print(f"❌ '{key}' not found or not set in your Google Drive configuration.")
                exit(1)
        print("   - ✅ Google Drive configuration is complete.")


    def _configure_dvc(self):
        # ... (no changes here)
        print("\n🔄 Configuring DVC for Google Drive...")
        if not (self.root_dir / ".dvc").exists():
            self._run_command(["dvc", "init"])
        else:
            print("   - ✅ DVC already initialized.")
        print("   - 🔗 Configuring DVC remote 'gdrive_storage'...")
        folder_id = self.gdrive_config["folder_id"]
        client_id = self.gdrive_config["gdrive_client_id"]
        client_secret = self.gdrive_config["gdrive_client_secret"]
        remote_url = f"gdrive://{folder_id}"
        self._run_command(["dvc", "remote", "add", "-d", "gdrive_storage", remote_url, "--force"])
        self._run_command(["dvc", "remote", "modify", "gdrive_storage", "gdrive_client_id", client_id])
        self._run_command(["dvc", "remote", "modify", "gdrive_storage", "gdrive_client_secret", client_secret])
        print("   - ✅ DVC remote configured.")

    # --- THIS METHOD IS FOR THE 'CHECKOUT' SCENARIO ---
    def _pull_data(self):
        """Pulls the latest data from the configured DVC remote."""
        print("\n⏬ Pulling latest data and models from DVC remote...")
        self._run_command(["dvc", "pull"])
        print("   - ✅ Data pull complete.")

    # --- THIS METHOD IS FOR THE 'NEW PROJECT' SCENARIO ---
    def _initial_track_and_push(self):
        """Performs the first 'dvc add', 'git commit', and 'dvc push'."""
        print("\n🛰️  Performing initial tracking of data directories...")
        self._run_command(["dvc", "add", str(self.input_dir)])
        self._run_command(["dvc", "add", str(self.output_dir)])
        git_status_result = self._run_command(["git", "status", "--porcelain"])
        if not ".dvc" in git_status_result.stdout:
            print("   - ✅ No new data to track. Directories might be empty or unchanged.")
            return
        print("\n📝 Creating initial Git commit for data tracking...")
        input_dvc_file = f"{self.input_dir}.dvc"
        output_dvc_file = f"{self.output_dir}.dvc"
        self._run_command(["git", "add", ".gitignore", input_dvc_file, output_dvc_file])
        self.  _run_command(["git", "commit", "-m", "chore: Initial data tracking with DVC"], check=False)
        print("\n⏫ Pushing initial data to remote storage...")
        self._run_command(["dvc", "push"])
        print("   - ✅ Initial data push complete.")

    # --- NEW METHOD TO DECIDE WHICH ACTION TO TAKE ---
    def _bootstrap_data(self):
        """Checks if data is already tracked and decides whether to pull or push."""
        input_dvc_file = self.root_dir / f"{self.input_dir}.dvc"
        output_dvc_file = self.root_dir / f"{self.output_dir}.dvc"
        self._pull_data()
        self._initial_track_and_push()



    # --- MODIFIED RUN METHOD ---
    def run(self):
        """Executes the complete setup workflow."""
        self._create_directories()
        self._validate_gdrive_config()
        self._configure_dvc()
        self._bootstrap_data() # This now handles both scenarios
        print("\n🎉 Setup and bootstrap complete! Your environment is ready.")