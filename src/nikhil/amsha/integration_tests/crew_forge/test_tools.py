import os
import sys
import yaml
from crewai.tools import BaseTool

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
JOB_CONFIG_PATH = os.path.join(CONFIG_DIR, "job_config_tools.yaml")
# Shared config path
LLM_PROVIDERS_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "llm_factory", "config", "llm_providers.yaml")
LLM_SETTINGS_PATH = os.path.join(CONFIG_DIR, "llm_settings.yaml")

class SquareTool(BaseTool):
    name: str = "SquareTool"
    description: str = "Calculates the square of a number. Input should be a number."

    def _run(self, number: str) -> str:
        try:
            val = float(number)
            return str(val * val)
        except ValueError:
            return "Invalid input"

def main():
    print("Running Crew Forge Integration Test: Custom Tools (LM Studio / Gemini)")
    
    # 1. Load LLM Settings
    if not os.path.exists(LLM_SETTINGS_PATH):
         # Same fallback
        if os.path.exists(LLM_PROVIDERS_CONFIG_PATH):
             import shutil
             # We just copy for now
             shutil.copy(LLM_PROVIDERS_CONFIG_PATH, LLM_SETTINGS_PATH)
        else:
            print("   ❌ LLM Settings not found. Run basic test first.")
            return

    settings_dict = YamlUtils.yaml_safe_load(LLM_SETTINGS_PATH)
    llm_settings = LLMSettings(**settings_dict)
    llm_builder = LLMBuilder(llm_settings)
    
    try:
        build_result = llm_builder.build(LLMType.CREATIVE)
        llm = build_result.llm
    except Exception as e:
        print(f"   ❌ LLM Build Failed: {e}")
        return

    # 2. Initialize Services
    runtime = RuntimeEngine(max_workers=1)
    state_manager = StateManager()
    
    job_config = YamlUtils.yaml_safe_load(JOB_CONFIG_PATH)
    
    # 3. Inject Custom Tool via MonkeyPatching
    # We patch AtomicYamlBuilderService.add_agent to inject our tool
    from unittest.mock import patch
    from amsha.crew_forge.service.atomic_yaml_builder import AtomicYamlBuilderService
    
    original_add_agent = AtomicYamlBuilderService.add_agent
    
    def add_agent_with_tool(self, knowledge_sources=None, tools=None):
        if tools is None:
            tools = []
        # Inject our tool
        print("   🔧 Injecting SquareTool...")
        tools.append(SquareTool())
        return original_add_agent(self, knowledge_sources=knowledge_sources, tools=tools)

    # Apply the patch permanently for this process or context
    AtomicYamlBuilderService.add_agent = add_agent_with_tool

    manager = AtomicCrewFileManager(
        llm=llm,
        app_config_path=APP_CONFIG_PATH,
        job_config=job_config,
        model_name="test-tools-v1"
    )
    
    orchestrator = FileCrewOrchestrator(
        manager=manager,
        runtime=runtime,
        state_manager=state_manager
    )
    
    # 4. Run Execution
    print("   ⚡ Executing Crew with Tool...")
    try:
        result = orchestrator.run_crew(
            crew_name="ToolTestCrew",
            inputs={"number": "5"},
            mode=ExecutionMode.INTERACTIVE
        )
        print("   ✅ Execution Completed")
        print(f"   Result: {result}")

    except Exception as e:
        print(f"   ❌ Execution Failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        runtime.shutdown()
        # Restore original if needed (good practice, though script ends)
        AtomicYamlBuilderService.add_agent = original_add_agent

if __name__ == "__main__":
    main()
