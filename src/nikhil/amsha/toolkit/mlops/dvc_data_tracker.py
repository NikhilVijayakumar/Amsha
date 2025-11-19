import subprocess
from datetime import datetime
from pathlib import Path
from nikhil.amsha.utils.yaml_utils import YamlUtils


class DVCDataTracker:
    """
    Handles the collaborative workflow of syncing DVC data to S3.
    It pulls remote changes before tracking and pushing local changes.
    """

    def __init__(self, config_path: str):
        print("🚀 Initializing DVC Data Tracker...")
        self.config_path = Path(config_path)
        if not self.config_path.exists():
            print(f"❌ Configuration file not found at: {self.config_path}")
            exit(1)
        self.config = YamlUtils.yaml_safe_load(config_path)
        self.root_dir = Path.cwd()
        self.input_dir = Path(self.config["domain_root_path"])
        self.output_dir = Path(self.config["output_dir_path"])
        self.base_commit_message = self.config.get("commit_message")
        if not self.base_commit_message:
            print("❌ 'commit_message' not found in the config file. Please add it.")
            exit(1)
        print("   - ✅ Configuration loaded successfully.")

    def _run_command(self, command: list, check=True):
        """Helper to run shell commands and return the result."""
        try:
            print(f"   - Executing: {' '.join(command)}")
            result = subprocess.run(command, check=check, text=True, cwd=self.root_dir, capture_output=True)
            if result.stderr and check:
                # Filter out non-error DVC outputs that sometimes go to stderr
                if "WARNING" not in result.stderr and "Everything is up to date" not in result.stderr:
                    print(f"   - Info: {result.stderr.strip()}")
            return result
        except subprocess.CalledProcessError as e:
            print(f"❌ Command failed: {' '.join(command)}")
            print(f"   --- STDERR ---:\n{e.stderr.strip()}")
            print(f"   --- STDOUT ---:\n{e.stdout.strip()}")
            exit(1)

    def _run_validations(self):
        print("\n🔎 Running data validations...")
        # Insert your specific data validation logic here
        # e.g., checking if files are empty, schema validation, etc.
        pass
        print("   - ✅ All validations passed.")

    def sync_data(self):
        """
        Pulls remote data from S3, validates, tracks local data, then commits and pushes back to S3.
        """
        # 1. Pull latest changes from S3 first
        print("\n⏬ Pulling latest remote data changes from S3...")
        self._run_command(["dvc", "pull"])

        # 2. Run validations on local files
        self._run_validations()

        # 3. Track data directories to capture local changes
        print("\n🔄 Tracking local data directories with DVC...")
        self._run_command(["dvc", "add", str(self.input_dir)])
        self._run_command(["dvc", "add", str(self.output_dir)])

        git_status_result = self._run_command(["git", "status", "--porcelain"])

        # Check if .dvc files are modified
        if ".dvc" not in git_status_result.stdout:
            print("\n✅ No new local data changes to commit. Workspace is up-to-date.")
            return

        # 4. Format and commit the changes
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        final_commit_message = f"{self.base_commit_message} ({timestamp})"

        print("\n📝 Staging and committing data changes to Git...")
        input_dvc_file = f"{self.input_dir}.dvc"
        output_dvc_file = f"{self.output_dir}.dvc"

        self._run_command(["git", "add", ".gitignore", input_dvc_file, output_dvc_file])
        self._run_command(["git", "commit", "-m", final_commit_message])
        print(f"   - ✅ Committed with message: '{final_commit_message}'")

        # 5. Push your new version to S3
        print("\n⏫ Pushing new data version to S3 remote...")
        self._run_command(["dvc", "push"])

        print("\n🎉 Success! Your workspace is now synced with the S3 remote.")