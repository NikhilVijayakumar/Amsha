import os
import sys
import json
from typing import Dict, Any, Optional
from pathlib import Path

# Ensure module path resolution
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../../")))

# --- Monkeypatch print for Windows Encoding ---
import builtins
original_print = builtins.print

def safe_print(*args, **kwargs):
    try:
        original_print(*args, **kwargs)
    except UnicodeEncodeError:
        new_args = []
        for arg in args:
            if isinstance(arg, str):
                new_args.append(arg.encode(sys.stdout.encoding or 'utf-8', 'replace').decode(sys.stdout.encoding or 'utf-8'))
            else:
                new_args.append(arg)
        original_print(*new_args, **kwargs)

builtins.print = safe_print

from amsha.crew_forge.orchestrator.file.amsha_crew_file_application import AmshaCrewFileApplication
from amsha.llm_factory.domain.model.llm_type import LLMType
from amsha.execution_runtime.domain.execution_mode import ExecutionMode
from amsha.crew_forge.service.atomic_yaml_builder import AtomicYamlBuilderService

# --- Config Paths ---
CONFIG_DIR = os.path.join(os.path.dirname(__file__), "config")
APP_CONFIG_PATH = os.path.join(CONFIG_DIR, "app_config.yaml")
JOB_CONFIG_PATH = os.path.join(CONFIG_DIR, "job_config_retry_test.yaml") # Use corrected config
LLM_PROVIDERS_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "llm_factory", "config", "llm_providers.yaml")
LLM_SETTINGS_PATH = os.path.join(CONFIG_DIR, "llm_settings.yaml")

class GeneratePlotApplication(AmshaCrewFileApplication):
    """
    Application that mimics the user's request:
    - Runs a pipeline
    - Checks for clean JSON output
    - Retries if validation fails
    """

    def __init__(self, config_paths: Dict[str, str], llm_type: LLMType):
        super().__init__(config_paths, llm_type)
        self.validation_attempts = 0 # Track attempts for verification

    def run(self) -> Any:
        class_name = self.__class__.__name__
        print(f"{class_name} - Starting configured pipeline workflow...")
        pipeline_steps = self.job_config.get("pipeline", [])
        if not pipeline_steps:
            print("No pipeline defined in job_config.yaml. Nothing to run.")
            return

        pipeline_results = {}
        
        # For this test, we'll just run the first step to demonstrate retry logic
        # In a real scenario, we'd loop through all steps
        crew_name = pipeline_steps[0] 
        
        print(f"{class_name} - Running crew: {crew_name}")
        
        # Prepare inputs (simplified for test)
        pipeline_input = {"theme": "A story about resilience"} 
        
        # Execute with retry logic controlled by Base Application
        # We override validate_execution to provide custom logic
        result = self.execute_crew_with_retry(
            crew_name=crew_name,
            inputs=pipeline_input,
            max_retries=3,
            filename_suffix="retry_test"
        )
        
        pipeline_results[crew_name] = result
        return pipeline_results

    def validate_execution(self, result: Any, output_file: Optional[str]) -> bool:
        """
        Override base validation to check for clean JSON.
        """
        if output_file and self.custom_json_validator(output_file):
            return True
        return False

    def custom_json_validator(self, output_file: str) -> bool:
        """
        Custom validator that simulates failure on first few attempts
        to demonstrate retry logic, then passes.
        """
        self.validation_attempts += 1
        print(f"🔍 [Validator] Checking file: {output_file} (Attempt #{self.validation_attempts})")
        
        # In a real app, this would be:
        # return self.clean_json(output_file)
        
        # For this TEST, we simulate failure for the first 2 attempts
        if self.validation_attempts < 3:
            print("❌ [Validator] Simulating invalid JSON (forcing retry)...")
            return False
            
        print("✅ [Validator] JSON is clean!")
        return True

# --- Main Execution Setup ---
def setup_llm_settings():
    """Derived settings from the central provider config."""
    if not os.path.exists(LLM_SETTINGS_PATH):
        if os.path.exists(LLM_PROVIDERS_CONFIG_PATH):
            import shutil
            shutil.copy(LLM_PROVIDERS_CONFIG_PATH, LLM_SETTINGS_PATH)
        else:
             raise FileNotFoundError("LLM Providers config not found!")

def main():
    log_file_path = "test_retry_output.log"
    # Redirect stdout to file for cleaner capture in CI/Test environments
    with open(log_file_path, "w", encoding="utf-8") as f:
        sys.stdout = f
        sys.stderr = f
        print("Running GeneratePlotApplication Retry Test\n")
        
        try:
            setup_llm_settings()
            
            setup_llm_settings()
            
            # --- Mocking crewai.Crew.kickoff to avoid LLM dependency ---
            from unittest.mock import MagicMock, patch
            from crewai import Crew
            
            # We patch Crew.kickoff to return a dummy result
            with patch.object(Crew, 'kickoff', return_value={"result": "Mocked Story Content"}):
                configs = {
                    "llm": LLM_SETTINGS_PATH,
                    "app": APP_CONFIG_PATH,
                    "job": JOB_CONFIG_PATH
                }
                
                app = GeneratePlotApplication(config_paths=configs, llm_type=LLMType.CREATIVE)
                app.run()
            
            print("\nTest Finished!")
            
            # Verify attempts
            if app.validation_attempts == 3:
                 print("VERIFICATION SUCCESS: Retried exactly 3 times as expected.")
            else:
                 print(f"VERIFICATION FAILED: Expected 3 attempts, got {app.validation_attempts}")

        except Exception as e:
            print(f"Test Failed: {e}")
            import traceback
            traceback.print_exc()
        finally:
             sys.stdout = sys.__stdout__
             sys.stderr = sys.__stderr__

    # Output verification to console
    with open(log_file_path, "r", encoding="utf-8") as f:
        content = f.read()
        if "VERIFICATION SUCCESS" in content:
             print("Test PASSED: Retry logic verified.")
        else:
             print("Test FAILED: Check test_retry_output.log")
             print(content)

if __name__ == "__main__":
    main()
