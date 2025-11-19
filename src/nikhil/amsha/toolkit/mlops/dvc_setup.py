import subprocess
from pathlib import Path
from nikhil.amsha.utils.yaml_utils import YamlUtils


class DVCSetup:
    """
    Automates DVC setup for S3 (AWS/MinIO/Docker).
    It intelligently decides whether to push initial data or pull existing data.
    """

    def __init__(self, config_path: str):
        print("🚀 Initializing DVC Environment Setup (S3 Mode)...")
        self.config_path = Path(config_path)
        if not self.config_path.exists():
            print(f"❌ Configuration file not found at: {self.config_path}")
            exit(1)
        self.config = YamlUtils.yaml_safe_load(config_path)
        self.root_dir = Path.cwd()
        self.input_dir = Path(self.config["domain_root_path"])
        self.output_dir = Path(self.config["output_dir_path"])

        # Changed from google_drive to s3_config
        self.s3_config = self.config.get("s3_config")

        print(f"   - Project Root: {self.root_dir}")
        print(f"   - Input Dir: {self.input_dir}")
        print(f"   - Output Dir: {self.output_dir}")
        print("   - ✅ Configuration loaded successfully.")

    def _run_command(self, command: list, check=True):
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
            print("❌ Command 'dvc' not found. Is DVC installed? (pip install dvc dvc-s3)")
            exit(1)

    def _create_directories(self):
        print("\n📂 Ensuring all necessary directories exist...")
        for dir_path in [self.input_dir, self.output_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        print("   - ✅ Directories checked.")

    def _validate_s3_config(self):
        print("\n🔍 Validating S3 configuration...")
        if not self.s3_config:
            print("❌ 's3_config' block missing in YAML.")
            exit(1)

        required_keys = ["bucket_name", "access_key_id", "secret_access_key"]
        for key in required_keys:
            value = self.s3_config.get(key)
            if not value or "YOUR_" in str(value):
                print(f"❌ '{key}' not found or not set correctly in S3 configuration.")
                exit(1)
        print("   - ✅ S3 configuration is complete.")

    def _configure_dvc(self):
        print("\n🔄 Configuring DVC for S3 Storage...")

        # 1. Initialize DVC
        if not (self.root_dir / ".dvc").exists():
            self._run_command(["dvc", "init"])
        else:
            print("   - ✅ DVC already initialized.")

        # 2. Setup Remote
        print("   - 🔗 Configuring DVC remote 's3_storage'...")

        bucket_name = self.s3_config["bucket_name"]
        remote_url = f"s3://{bucket_name}/dvc_store"  # Organizing inside a subfolder

        # Add remote (force overwrites if exists)
        self._run_command(["dvc", "remote", "add", "-d", "s3_storage", remote_url, "--force"])

        # 3. Configure S3 Specifics (Endpoint, Region, SSL)
        # If using Docker/MinIO, endpoint_url is critical
        endpoint_url = self.s3_config.get("endpoint_url")
        if endpoint_url:
            self._run_command(["dvc", "remote", "modify", "s3_storage", "endpointurl", endpoint_url])

        region = self.s3_config.get("region")
        if region:
            self._run_command(["dvc", "remote", "modify", "s3_storage", "region", region])

        use_ssl = self.s3_config.get("use_ssl", True)
        if not use_ssl:
            self._run_command(["dvc", "remote", "modify", "s3_storage", "use_ssl", "false"])

        # 4. Configure Secrets (Using --local to prevent git commit of secrets)
        print("   - 🔐 Configuring secrets (locally)...")
        self._run_command(["dvc", "remote", "modify", "--local", "s3_storage",
                           "access_key_id", self.s3_config["access_key_id"]])
        self._run_command(["dvc", "remote", "modify", "--local", "s3_storage",
                           "secret_access_key", self.s3_config["secret_access_key"]])

        print("   - ✅ DVC remote configured for S3.")

    def _pull_data(self):
        """Pulls the latest data from the configured DVC remote."""
        print("\n⏬ Pulling latest data and models from S3...")
        # We use check=False because if the bucket is empty (first run), pull might fail harmlessly
        res = self._run_command(["dvc", "pull"], check=False)
        if res.returncode == 0:
            print("   - ✅ Data pull complete.")
        else:
            print("   - ⚠️ Data pull skipped or failed (Remote might be empty).")

    def _initial_track_and_push(self):
        """Performs the first 'dvc add', 'git commit', and 'dvc push'."""
        print("\n🛰️  Performing initial tracking of data directories...")
        self._run_command(["dvc", "add", str(self.input_dir)])
        self._run_command(["dvc", "add", str(self.output_dir)])

        git_status_result = self._run_command(["git", "status", "--porcelain"])
        if ".dvc" not in git_status_result.stdout:
            print("   - ✅ No new data to track. Directories might be empty or unchanged.")
            return

        print("\n📝 Creating initial Git commit for data tracking...")
        input_dvc_file = f"{self.input_dir}.dvc"
        output_dvc_file = f"{self.output_dir}.dvc"

        # Ensure .gitignore is updated by DVC
        self._run_command(["git", "add", ".gitignore", input_dvc_file, output_dvc_file])
        self._run_command(["git", "commit", "-m", "chore: Initial data tracking with DVC (S3)"], check=False)

        print("\n⏫ Pushing initial data to S3...")
        self._run_command(["dvc", "push"])
        print("   - ✅ Initial data push complete.")

    def _bootstrap_data(self):
        self._pull_data()
        self._initial_track_and_push()

    def run(self):
        """Executes the complete setup workflow."""
        self._create_directories()
        self._validate_s3_config()
        self._configure_dvc()
        self._bootstrap_data()
        print("\n🎉 Setup and bootstrap complete! Your S3 environment is ready.")