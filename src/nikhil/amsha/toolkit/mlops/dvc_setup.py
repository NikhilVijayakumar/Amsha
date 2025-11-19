import subprocess
import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
from pathlib import Path
from nikhil.amsha.utils.yaml_utils import YamlUtils


class DVCSetup:
    """
    Automates DVC setup for S3 (AWS/MinIO).
    Now includes auto-creation of S3 buckets to prevent 400 errors.
    """

    def __init__(self, config_path: str):
        print("🚀 Initializing DVC Environment Setup (S3/MinIO)...")
        self.config_path = Path(config_path)
        if not self.config_path.exists():
            print(f"❌ Configuration file not found at: {self.config_path}")
            exit(1)
        self.config = YamlUtils.yaml_safe_load(config_path)
        self.root_dir = Path.cwd()
        self.input_dir = Path(self.config["domain_root_path"])
        self.output_dir = Path(self.config["output_dir_path"])
        self.s3_config = self.config.get("s3_config")

        print(f"   - Project Root: {self.root_dir}")
        print(f"   - Input Dir: {self.input_dir}")
        print(f"   - Output Dir: {self.output_dir}")

    def _run_command(self, command: list, check=True):
        try:
            # print(f"   - Executing: {' '.join(command)}")
            # (Uncomment above for verbose logging)
            result = subprocess.run(command, check=check, text=True, cwd=self.root_dir, capture_output=True)
            if result.stderr and check:
                if "WARNING" not in result.stderr:
                    print(f"   - Info: {result.stderr.strip()}")
            return result
        except subprocess.CalledProcessError as e:
            print(f"❌ Command failed: {' '.join(command)}")
            print(f"   Error: {e.stderr.strip()}")
            exit(1)

    def _create_directories(self):
        print("\n📂 Ensuring local directories exist...")
        for dir_path in [self.input_dir, self.output_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        print("   - ✅ Directories checked.")

    def _ensure_bucket_exists(self):
        """
        Uses Boto3 to check if the bucket exists in MinIO/S3.
        Creates it if it doesn't exist. This fixes the '400 Bad Request' error.
        """
        print("\n🪣  Verifying S3 Bucket status...")
        bucket_name = self.s3_config["bucket_name"]
        endpoint = self.s3_config.get("endpoint_url")

        # Configure Boto3 Client
        # We force 'path' style addressing to ensure localhost compatibility
        s3_client = boto3.client(
            "s3",
            endpoint_url=endpoint,
            aws_access_key_id=self.s3_config["access_key_id"],
            aws_secret_access_key=self.s3_config["secret_access_key"],
            region_name=self.s3_config.get("region", "us-east-1"),
            use_ssl=self.s3_config.get("use_ssl", False),
            config=Config(s3={'addressing_style': 'path'})
        )

        try:
            s3_client.head_bucket(Bucket=bucket_name)
            print(f"   - ✅ Bucket '{bucket_name}' already exists.")
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                print(f"   - ⚠️ Bucket '{bucket_name}' not found. Creating it...")
                try:
                    s3_client.create_bucket(Bucket=bucket_name)
                    print(f"   - ✅ Bucket '{bucket_name}' created successfully!")
                except Exception as create_err:
                    print(f"   - ❌ Failed to create bucket: {create_err}")
                    exit(1)
            else:
                print(f"   - ❌ Failed to connect to S3/MinIO: {e}")
                print("     (Check your Docker container is running and ports are 9000:9000)")
                exit(1)
        except Exception as e:
            print(f"   - ❌ Unexpected connection error: {e}")
            exit(1)

    def _configure_dvc(self):
        print("\n🔄 Configuring DVC for S3...")
        if not (self.root_dir / ".dvc").exists():
            self._run_command(["dvc", "init"])

        bucket_name = self.s3_config["bucket_name"]
        remote_url = f"s3://{bucket_name}/dvc_store"

        # Add Remote
        self._run_command(["dvc", "remote", "add", "-d", "s3_storage", remote_url, "--force"])

        # S3/MinIO Config
        endpoint_url = self.s3_config.get("endpoint_url")
        if endpoint_url:
            self._run_command(["dvc", "remote", "modify", "s3_storage", "endpointurl", endpoint_url])

        self._run_command(["dvc", "remote", "modify", "s3_storage", "use_ssl", "false"])

        # Credentials (Local)
        self._run_command(["dvc", "remote", "modify", "--local", "s3_storage",
                           "access_key_id", self.s3_config["access_key_id"]])
        self._run_command(["dvc", "remote", "modify", "--local", "s3_storage",
                           "secret_access_key", self.s3_config["secret_access_key"]])
        print("   - ✅ DVC remote configured.")

    def _bootstrap_data(self):
        # Try pulling first (suppress error if empty)
        print("\n⏬ Attempting to pull existing data...")
        self._run_command(["dvc", "pull"], check=False)

        # Track and Push
        print("\n⏫ Tracking and Pushing local data...")
        self._run_command(["dvc", "add", str(self.input_dir)])
        self._run_command(["dvc", "add", str(self.output_dir)])

        # Git commit (simplified for setup)
        self._run_command(["git", "add", ".gitignore", f"{self.input_dir}.dvc", f"{self.output_dir}.dvc"])
        self._run_command(["git", "commit", "-m", "chore: Initial DVC setup"], check=False)

        # Push to S3 (The moment of truth!)
        self._run_command(["dvc", "push"])
        print("   - ✅ Data pushed to MinIO successfully.")

    def run(self):
        self._create_directories()
        self._ensure_bucket_exists()  # <--- The critical fix
        self._configure_dvc()
        self._bootstrap_data()
        print("\n🎉 Setup complete! Your local S3 environment is live.")