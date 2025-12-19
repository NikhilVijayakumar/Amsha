import os
import sys
import yaml
import time
from amsha.utils.yaml_utils import YamlUtils
from amsha.llm_factory.service.llm_builder import LLMBuilder
from amsha.llm_factory.settings.llm_settings import LLMSettings
from amsha.llm_factory.domain.llm_type import LLMType
from amsha.execution_runtime.domain.execution_mode import ExecutionMode
from amsha.execution_runtime.service.runtime_engine import RuntimeEngine
from amsha.execution_state.service.state_manager import StateManager
from amsha.crew_forge.orchestrator.file.atomic_crew_file_manager import AtomicCrewFileManager
from amsha.crew_forge.orchestrator.file.file_crew_orchestrator import FileCrewOrchestrator

CONFIG_DIR = os.path.join(os.path.dirname(__file__), "config")
APP_CONFIG_PATH = os.path.join(CONFIG_DIR, "app_config.yaml")
JOB_CONFIG_PATH = os.path.join(CONFIG_DIR, "job_config.yaml")

def main():
    print("Starting Amsha 2.0 Integration Demo (No Mocks)")
    
    # 1. Initialize LLM Factory
    print("[1] Building LLM...")
    # Old incorrect call removed

    
    # We need to ensure settings can load. 
    # Since LLMSettings usually loads from env or a dedicated config, 
    # we might need to mock or provide a minimal config for it if it expects one.
    # Actually, LLMBuilder uses LLMSettings. 
    # Let's check LLMSettings __init__... if it fails without file, we'll create a dummy settings file.
    # For now, let's assume default settings or provide a minimal one.
    
    # Create a valid llm_settings.yaml matching the core schema
    settings_path = os.path.join(CONFIG_DIR, "llm_settings.yaml")
    with open(settings_path, 'w') as f:
        yaml.dump({
            "llm": {
                "creative": {
                    "default": "gpt-4-config",
                    "models": {
                        "gpt-4-config": {
                            "model": "gpt-4",
                            "api_key": os.environ.get("OPENAI_API_KEY", "dummy-key")
                        }
                    }
                }
            },
            "llm_parameters": {
                "creative": {
                    "temperature": 0.7,
                    "max_completion_tokens": 1000
                }
            }
        }, f)
        
    print(f"    Loading Settings from {settings_path}")
    settings_dict = YamlUtils.yaml_safe_load(settings_path)
    llm_settings = LLMSettings(**settings_dict)
    
    llm_builder = LLMBuilder(llm_settings)
    build_result = llm_builder.build(LLMType.CREATIVE)
    llm_instance = build_result.llm 
    
    print(f"    Model Configured: {llm_settings.get_model_config('creative').model}")
    print(f"    LLM Built: {build_result.model_name}")

    # 2. Initialize Core Services
    print("[2] Initializing Runtime & State Manager...")
    runtime = RuntimeEngine(max_workers=2)
    state_manager = StateManager()

    # 3. Initialize Manager & Orchestrator
    print("[3] Initializing Orchestrator...")
    job_config = YamlUtils.yaml_safe_load(JOB_CONFIG_PATH)
    
    manager = AtomicCrewFileManager(
        llm=llm_instance,
        app_config_path=APP_CONFIG_PATH,
        job_config=job_config,
        model_name="integration-demo-v1"
    )
    
    orchestrator = FileCrewOrchestrator(
        manager=manager,
        runtime=runtime,
        state_manager=state_manager
    )

    # 4. Run Execution
    print("[4] Executing Crew in Background...")
    # NOTE: Since we are using a real LLM (gpt-4), ensure OPENAI_API_KEY is set in environment.
    # If not, this will fail. The user environment "e:\Python\Amsha" implies a local setup.
    # If API key is missing, we might want to catch that.
    
    if not os.environ.get("OPENAI_API_KEY"):
        print("WARNING: OPENAI_API_KEY not found in env. Setting a dummy key for dry-run/test integrity check only.")
        os.environ["OPENAI_API_KEY"] = "sk-dummy-key-for-integration-structure-test"
        # Without a real key, actual calls will fail, but the structure will be exercised.
    
    try:
        handle = orchestrator.run_crew(
            crew_name="IntegrationDemoCrew",
            inputs={"topic": "Integration Testing"},
            mode=ExecutionMode.BACKGROUND
        )
        
        exec_id = getattr(handle, 'execution_state_id', None)
        print(f"    Execution Started! ID: {exec_id}")
        
        # 5. Monitor
        print("[5] Monitoring Execution...")
        max_retries = 10
        for _ in range(max_retries):
            state = state_manager.get_execution(exec_id)
            print(f"    Status: {state.status}")
            
            if state.status in ["COMPLETED", "FAILED", "CANCELLED"]:
                break
            time.sleep(2)
            
        final_state = state_manager.get_execution(exec_id)
        print(f"\nFinal Status: {final_state.status}")
        print(f"   Metadata: {final_state.metadata}")
        
        if final_state.status == "FAILED":
             print(f"   Error: {final_state.metadata.get('error')}")

    except Exception as e:
        print(f"Execution Exception: {e}")
        import traceback
        traceback.print_exc()
    finally:
        runtime.shutdown()
        print("Runtime Shutdown.")

if __name__ == "__main__":
    main()
