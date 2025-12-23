import os

import yaml

from amsha.crew_forge.orchestrator.file.atomic_crew_file_manager import AtomicCrewFileManager
from amsha.crew_forge.orchestrator.file.file_crew_orchestrator import FileCrewOrchestrator
from amsha.execution_runtime.domain.execution_mode import ExecutionMode
from amsha.execution_runtime.service.runtime_engine import RuntimeEngine
from amsha.execution_state.service.state_manager import StateManager
from amsha.llm_factory.domain.llm_type import LLMType
from amsha.llm_factory.service.llm_builder import LLMBuilder
from amsha.llm_factory.settings.llm_settings import LLMSettings
from amsha.utils.yaml_utils import YamlUtils

CONFIG_DIR = os.path.join(os.path.dirname(__file__), "config")
APP_CONFIG_PATH = os.path.join(CONFIG_DIR, "app_config.yaml")
JOB_CONFIG_PATH = os.path.join(CONFIG_DIR, "job_config_basic.yaml")
# Shared config path
LLM_PROVIDERS_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "llm_factory", "config", "llm_providers.yaml")
LLM_SETTINGS_PATH = os.path.join(CONFIG_DIR, "llm_settings.yaml")

def setup_llm_settings():
    """Derived settings from the central provider config."""
    if not os.path.exists(LLM_PROVIDERS_CONFIG_PATH):
        raise FileNotFoundError(f"Provider config not found at {LLM_PROVIDERS_CONFIG_PATH}")
    
    with open(LLM_PROVIDERS_CONFIG_PATH, 'r') as f:
        config = yaml.safe_load(f)
    
    # We use the 'default' set in llm_providers.yaml (which is lm_studio_model)
    # Expand env vars if needed (simple version)
    import re
    def expand_vars(text):
        if not isinstance(text, str): return text
        pattern = re.compile(r'\$\{([^}]+)\}')
        return pattern.sub(lambda m: os.environ.get(m.group(1), f"MISSING_{m.group(1)}"), text)

    # Deep expand
    def expand_dict(d):
        new_d = {}
        for k, v in d.items():
            if isinstance(v, dict):
                new_d[k] = expand_dict(v)
            elif isinstance(v, str):
                new_d[k] = expand_vars(v)
            else:
                new_d[k] = v
        return new_d

    expanded_config = expand_dict(config)
    
    # Save to local settings path for usage
    with open(LLM_SETTINGS_PATH, 'w') as f:
        yaml.dump(expanded_config, f)

def main():
    print("Running Crew Forge Integration Test: Basic Agent (LM Studio / Gemini)")
    
    # 1. Setup LLM Settings
    try:
        setup_llm_settings()
    except Exception as e:
        print(f"   ❌ Config Setup Failed: {e}")
        return

    settings_dict = YamlUtils.yaml_safe_load(LLM_SETTINGS_PATH)
    llm_settings = LLMSettings(**settings_dict)
    
    llm_builder = LLMBuilder(llm_settings)
    
    try:
        build_result = llm_builder.build(LLMType.CREATIVE)
        llm = build_result.llm
        print(f"   ✅ LLM Built: {build_result.model_name}")
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
        model_name="test-basic-v1"
    )
    
    orchestrator = FileCrewOrchestrator(
        manager=manager,
        runtime=runtime,
        state_manager=state_manager
    )
    
    # 3. Run Execution
    print("   ⚡ Executing Crew...")
    try:
        result = orchestrator.run_crew(
            crew_name="BasicTestCrew",
            inputs={"topic": "Integration Test"},
            mode=ExecutionMode.INTERACTIVE # Interactive for immediate feedback
        )
        print("   ✅ Execution Completed")
        print(f"   Result: {result}")
        
        # Verify State Persistence
        handle = list(orchestrator.get_last_performance_stats().__dict__.keys()) if orchestrator.get_last_performance_stats() else []
        print(f"   Performance Stats Available: {bool(handle)}")

    except Exception as e:
        print(f"   ❌ Execution Failed: {e}")
    finally:
        runtime.shutdown()

if __name__ == "__main__":
    main()
