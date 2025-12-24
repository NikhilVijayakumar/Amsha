import os
import sys
import yaml
from pathlib import Path
from typing import Dict, Any

# Ensure module path resolution
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../../")))

# --- Monkeypatch print for Windows Encoding ---
import builtins
original_print = builtins.print

def safe_print(*args, **kwargs):
    try:
        original_print(*args, **kwargs)
    except UnicodeEncodeError:
        # If encoding fails, try to print with 'replace' or just ascii
        new_args = []
        for arg in args:
            if isinstance(arg, str):
                new_args.append(arg.encode(sys.stdout.encoding or 'utf-8', 'replace').decode(sys.stdout.encoding or 'utf-8'))
            else:
                new_args.append(arg)
        original_print(*new_args, **kwargs)

builtins.print = safe_print

from crewai.tools import BaseTool

from amsha.utils.yaml_utils import YamlUtils
from amsha.llm_factory.service.llm_builder import LLMBuilder
from amsha.llm_factory.settings.llm_settings import LLMSettings
from amsha.llm_factory.domain.model.llm_type import LLMType
from amsha.execution_runtime.domain.execution_mode import ExecutionMode
from amsha.execution_runtime.service.runtime_engine import RuntimeEngine
from amsha.execution_state.service.state_manager import StateManager
from amsha.crew_forge.orchestrator.file.atomic_crew_file_manager import AtomicCrewFileManager
from amsha.crew_forge.orchestrator.file.file_crew_orchestrator import FileCrewOrchestrator
from amsha.crew_forge.orchestrator.file.amsha_crew_file_application import AmshaCrewFileApplication
from amsha.crew_forge.service.atomic_yaml_builder import AtomicYamlBuilderService


# --- Config Paths ---
CONFIG_DIR = os.path.join(os.path.dirname(__file__), "config")
APP_CONFIG_PATH = os.path.join(CONFIG_DIR, "app_config.yaml")
JOB_CONFIG_PATH = os.path.join(CONFIG_DIR, "job_config_pipeline.yaml")
LLM_PROVIDERS_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "llm_factory", "config", "llm_providers.yaml")
LLM_SETTINGS_PATH = os.path.join(CONFIG_DIR, "llm_settings.yaml")


# --- Custom Tool Definition ---
class TextStatsTool(BaseTool):
    name: str = "TextStatsTool"
    description: str = "Analyzes text and returns word count and average word length. Use this to check if the story is simple enough."

    def _run(self, text: str) -> str:
        words = text.split()
        if not words:
            return "Word Count: 0, Avg Length: 0"
        avg_len = sum(len(w) for w in words) / len(words)
        return f"Word Count: {len(words)}, Avg Word Length: {avg_len:.2f}"


# --- Application Class ---
class TestPipelineApplication(AmshaCrewFileApplication):
    """
    Integration test application that runs the Bedtime Story pipeline.
    Inherits from AmshaCrewFileApplication to leverage standard orchestration.
    """

    def __init__(self, config_paths: Dict[str, str], llm_type: LLMType):
        # We need to bypass the standard __init__ slightly because AmshaCrewFileApplication 
        # attempts to build the LLM and Manager internally using its own logic, 
        # but our test environment here sets up LLM/Runtime manually for integration testing consistency.
        # However, to be true to the pattern, we SHOULD let it handle things if possible, 
        # or mock/inject the pre-built components.
        
        # Given the "reference" uses inheritance, we will try to respect that.
        # But we need to ensure the config paths point to our test configs.
        super().__init__(config_paths, llm_type)
        
        # Override the runtime/state manager if needed, or let the base class create them.
        # The base AmshaCrewFileApplication creates:
        # self.orchestrator = FileCrewOrchestrator(manager)
        # It DOES NOT assume a runtime engine is passed in __init__, so it likely uses default.
        # If we need a custom runtime (e.g. for testing execution modes), we might need to swap it.
        pass

    def run(self) -> Any:
        print(f"Starting Bedtime Story Pipeline...")
        pipeline_steps = self.job_config.get("pipeline", [])
        
        if not pipeline_steps:
             print("No pipeline steps found!")
             return

        pipeline_context = {} 
        # store outputs here to pass to next steps
        # Context usage:
        # Step 1: Output -> stored
        # Step 2: Input <- from context["Step1"]["result"] (concept)
        # Step 3: Input <- from context["Step2"]["result"] (story)

        for step_name in pipeline_steps:
            print(f"\nExecuting Step: {step_name}")
            
            # Prepare Inputs
            # typically _prepare_multiple_inputs_for reads from `input` section of job_config
            inputs = self._prepare_multiple_inputs_for(step_name)
            
            # DYNAMIC INPUT INJECTION
            if step_name == "Step2_Write":
                 # Inject concept from Step 1
                 # Assuming Step 1 Output is a string or dict. 
                 # For simplicity, we pass previous result as 'concept_title'
                 prev_result = pipeline_context.get("Step1_Concept", "A generic story about kindness")
                 inputs["concept_title"] = str(prev_result)
                 print(f"   -> Injected concept: {inputs['concept_title'][:50]}...")

            if step_name == "Step3_Polish":
                 # Inject draft from Step 2
                 prev_result = pipeline_context.get("Step2_Write", "Once upon a time...")
                 inputs["rough_draft"] = str(prev_result)
                 print(f"   -> Injected rough draft (len={len(inputs['rough_draft'])})")

            # Execute Crew
            # We use filename_suffix to keep outputs distinct if using file logging
            result = self.orchestrator.run_crew(
                crew_name=step_name,
                inputs=inputs,
                filename_suffix=step_name,
                mode=ExecutionMode.INTERACTIVE 
            )
            
            pipeline_context[step_name] = result
            print(f"Step {step_name} Completed.")
            # print(f"   Result Output: {result}")

        return pipeline_context


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
    # Redirect stdout/stderr to file to avoid Windows console encoding issues completely
    log_file_path = "test_output.log"
    with open(log_file_path, "w", encoding="utf-8") as f:
        sys.stdout = f
        sys.stderr = f
        print("Running Crew Forge Integration Test: Bedtime Story Pipeline\n")
        
        try:
            # 1. Setup LLM Config (Test Environment Specific)
            setup_llm_settings()
            
            # 2. Inject Custom Tool (for Step 3)
            original_add_agent = AtomicYamlBuilderService.add_agent
            
            def add_agent_with_tool(service_self, knowledge_sources=None, tools=None):
                # Only inject for the Editor agent
                if "Editor" in service_self.agent_yaml_file or "editor" in service_self.agent_yaml_file:
                    if tools is None: tools = []
                    tools.append(TextStatsTool())
                return original_add_agent(service_self, knowledge_sources=knowledge_sources, tools=tools)

            AtomicYamlBuilderService.add_agent = add_agent_with_tool

            try:
                # 3. Initialize Application
                configs = {
                    "llm": LLM_SETTINGS_PATH,
                    "app": APP_CONFIG_PATH,
                    "job": JOB_CONFIG_PATH
                }
                
                # Run Application
                app = TestPipelineApplication(config_paths=configs, llm_type=LLMType.CREATIVE)
                results = app.run()
                
                print("\nPipeline Finished Successfully!")
                print("Final Polished Story:")
                print("-" * 40)
                print(results.get("Step3_Polish"))
                print("-" * 40)

            except Exception as e:
                print(f"\nPipeline Failed: {e}")
                import traceback
                traceback.print_exc()
            finally:
                # Restore Patch
                AtomicYamlBuilderService.add_agent = original_add_agent
        except Exception as outer_e:
             print(f"Critical Error: {outer_e}")
             import traceback
             traceback.print_exc()
        finally:
             # Restore stdout/stderr (optional, but good practice)
             sys.stdout = sys.__stdout__
             sys.stderr = sys.__stderr__

    # Read back and print specifically safe characters to console to confirm run
    try:
        with open(log_file_path, "r", encoding="utf-8") as f:
             content = f.read()
             if "Pipeline Finished Successfully!" in content:
                 sys.__stdout__.write("VERIFICATION SUCCESS: Log file contains success message.\n")
             else:
                 sys.__stdout__.write("VERIFICATION FAILED: Check test_output.log.\n")
    except Exception as e:
         sys.__stdout__.write(f"VERIFICATION ERROR reading log: {e}\n")


if __name__ == "__main__":
    main()
