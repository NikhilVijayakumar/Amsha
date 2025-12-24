import os
import sys
import yaml
from amsha.utils.yaml_utils import YamlUtils
from amsha.llm_factory.service.llm_builder import LLMBuilder
from amsha.llm_factory.settings.llm_settings import LLMSettings
from amsha.llm_factory.domain.model.llm_type import LLMType
from amsha.execution_runtime.domain.execution_mode import ExecutionMode
from amsha.execution_runtime.service.runtime_engine import RuntimeEngine
from amsha.execution_state.service.state_manager import StateManager
from amsha.crew_forge.orchestrator.file.atomic_crew_file_manager import AtomicCrewFileManager
from amsha.crew_forge.orchestrator.file.file_crew_orchestrator import FileCrewOrchestrator

CONFIG_DIR = os.path.join(os.path.dirname(__file__), "config")
APP_CONFIG_PATH = os.path.join(CONFIG_DIR, "app_config.yaml")
JOB_CONFIG_PATH = os.path.join(CONFIG_DIR, "job_config_knowledge.yaml")
# Shared config path
LLM_PROVIDERS_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "llm_factory", "config", "llm_providers.yaml")
LLM_SETTINGS_PATH = os.path.join(CONFIG_DIR, "llm_settings.yaml")

def main():
    print("Running Crew Forge Integration Test: Knowledge Integration (LM Studio / Gemini)")
    
    # 1. Ensure settings exist (rely on basic test or setup here)
    if not os.path.exists(LLM_SETTINGS_PATH):
        # Fallback logic: try to generate it using same logic as basic agent
        if os.path.exists(LLM_PROVIDERS_CONFIG_PATH):
             import shutil
             # We just copy it, but need env var expansion ideally. 
             # For simplicity in this step, let's assume basic agent ran or we proceed with potential raw vars
             # Better: just copy for now, LLMSettings might handle raw strings if builder handles it? 
             # No, builder expects values. 
             # Let's import the logic or just duplicate the read-write logic for robustness.
             with open(LLM_PROVIDERS_CONFIG_PATH, 'r') as f:
                 import yaml
                 config = yaml.safe_load(f)
             with open(LLM_SETTINGS_PATH, 'w') as f:
                 yaml.dump(config, f)
        else:
            print("   ❌ LLM Settings not found. Run basic test first.")
            return

    settings_dict = YamlUtils.yaml_safe_load(LLM_SETTINGS_PATH)
    llm_settings = LLMSettings(**settings_dict)
    llm_builder = LLMBuilder(llm_settings)
    
    try:
        build_result = llm_builder.build(LLMType.CREATIVE)
        llm = build_result.provider.get_raw_llm()
    except Exception as e:
        print(f"   ❌ LLM Build Failed: {e}")
        return

    # 2. Initialize Services
    runtime = RuntimeEngine(max_workers=1)
    state_manager = StateManager()
    
    job_config = YamlUtils.yaml_safe_load(JOB_CONFIG_PATH)
    
    manager = AtomicCrewFileManager(
        llm=llm,
        app_config_path=APP_CONFIG_PATH,
        job_config=job_config,
        model_name="test-knowledge-v1"
    )
    
    orchestrator = FileCrewOrchestrator(
        manager=manager,
        runtime=runtime,
        state_manager=state_manager
    )
    
    # 3. Run Execution
    print("   ⚡ Executing Crew with Knowledge...")
    try:
        # NOTE: This will trigger Docling import. 
        # Since we removed the top-level import, it should happen now.
        # If Docling is installed, it will try to embed the file.
        # If no embedding model/key, it might fail.
        
        result = orchestrator.run_crew(
            crew_name="KnowledgeTestCrew",
            inputs={"question": "What is the secret number?"},
            mode=ExecutionMode.INTERACTIVE
        )
        print("   ✅ Execution Completed")
        print(f"   Result: {result}")

    except Exception as e:
        print(f"   ❌ Execution Failed: {e}")
    finally:
        runtime.shutdown()

if __name__ == "__main__":
    main()
