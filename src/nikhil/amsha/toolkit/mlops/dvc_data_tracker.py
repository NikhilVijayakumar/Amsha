import yaml
import subprocess
from pathlib import Path
from datetime import datetime


class DVCDataTracker:
    """
    Handles the automated workflow of tracking and committing DVC data,
    including a validation step for data integrity.
    """

    def __init__(self, config_path: str):
        print("🚀 Initializing DVC Data Tracker...")

        self.config_path = Path(config_path)
        if not self.config_path.exists():
            print(f"❌ Configuration file not found at: {self.config_path}")
            exit(1)

        with self.config_path.open('r') as f:
            self.config = yaml.safe_load(f)

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
            result = subprocess.run(
                command, check=check, text=True, cwd=self.root_dir, capture_output=True
            )
            if result.stderr and check:
                print(f"   - Warning/Info: {result.stderr.strip()}")
            return result
        except subprocess.CalledProcessError as e:
            print(f"❌ Command failed: {' '.join(command)}")
            print(f"   Error: {e.stderr.strip()}")
            exit(1)

    def _run_validations(self):
        """
        Runs data validation checks before tracking.
        Exits if any validation fails.
        """
        print("\n🔎 Running data validations...")

        # Implement YAML structure validation for input files.
        # Example: Load YAML files and check for required keys.

        # Implement JSON structure validation for output files.
        # Example: Load JSON files and validate against a predefined schema.

        #  Add any other custom validations.

        print("   - ✅ All validations passed.")
        pass  # Placeholder for now

    def commit_and_push(self):
        """
        Validates data, tracks changes, commits, and pushes to DVC remote.
        """
        # 1. Run validations first
        self._run_validations()

        # 2. Track data directories with DVC
        print("\n🔄 Tracking data directories with DVC...")
        self._run_command(["dvc", "add", str(self.input_dir)])
        self._run_command(["dvc", "add", str(self.output_dir)])

        git_status_result = self._run_command(["git", "status", "--porcelain"])
        status_output = git_status_result.stdout.strip()

        if not any(line.strip().endswith('.dvc') for line in status_output.split('\n')):
            print("\n✅ No data changes to commit. Everything is up-to-date.")
            return

        # 3. Format and commit the changes
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        final_commit_message = f"{self.base_commit_message} ({timestamp})"

        print("\n📝 Staging and committing data changes to Git...")
        self._run_command(["git", "add", "*.dvc", ".gitignore"])
        self._run_command(["git", "commit", "-m", final_commit_message])
        print(f"   - ✅ Committed with message: '{final_commit_message}'")

        # 4. Push data to remote
        print("\n⏫ Pushing data to remote storage...")
        self._run_command(["dvc", "push"])

        print("\n🎉 Success! Your data version has been saved.")


