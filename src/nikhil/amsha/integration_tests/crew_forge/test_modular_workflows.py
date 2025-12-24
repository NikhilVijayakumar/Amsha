
import os
import sys
import yaml
from pathlib import Path
from typing import Dict, Any, List

# Add the src directory to sys.path
current_dir = Path(__file__).resolve().parent
src_dir = current_dir.parents[2]
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from crewai.tools import BaseTool
from pydantic import Field, PrivateAttr

from amsha.crew_forge.orchestrator.file.amsha_crew_file_application import AmshaCrewFileApplication
from amsha.crew_forge.orchestrator.file.file_crew_orchestrator import FileCrewOrchestrator
from amsha.crew_forge.service.atomic_yaml_builder import AtomicYamlBuilderService
from amsha.llm_factory.domain.model.llm_type import LLMType
from amsha.utils.yaml_utils import YamlUtils
from amsha.execution_runtime.domain.execution_mode import ExecutionMode

# --- Custom Tool Definition ---
class TextStatsTool(BaseTool):
    name: str = "TextStatsTool"
    description: str = "Analyzes text statistics."

    def _run(self, text: str) -> str:
        return f"Text analysis: {len(text.split())} words."

# --- Shared Base Paths ---
CONFIG_DIR = current_dir / "config"
PIPELINE_CONFIG_DIR = CONFIG_DIR / "pipeline"

# --- 1. Basic Application ---
class BedtimeStoryBasicApp(AmshaCrewFileApplication):
    def __init__(self, llm_type: LLMType):
        config_paths = {
            "llm": str(CONFIG_DIR / "llm_settings.yaml"),
            "app": str(CONFIG_DIR / "app_config.yaml"),
            "job": str(PIPELINE_CONFIG_DIR / "job_basic.yaml"), # Points to basic job
        }
        super().__init__(config_paths, llm_type)

    def run(self, theme: str) -> str:
        print(f"\n🚀 Running Basic App with theme: '{theme}'")
        inputs = {"theme": theme}
        result = self.orchestrator.run_crew(
            crew_name="Step1_Concept",
            inputs=inputs,
            filename_suffix="basic",
            mode=ExecutionMode.INTERACTIVE
        )
        return result

# --- 2. Knowledge Application ---
class BedtimeStoryKnowledgeApp(AmshaCrewFileApplication):
    def __init__(self, llm_type: LLMType):
        config_paths = {
            "llm": str(CONFIG_DIR / "llm_settings.yaml"),
            "app": str(CONFIG_DIR / "app_config.yaml"),
            "job": str(PIPELINE_CONFIG_DIR / "job_knowledge.yaml"), # Points to knowledge job
        }
        super().__init__(config_paths, llm_type)
        
    def run(self, concept_title: str) -> str:
        print(f"\n📘 Running Knowledge App with concept: '{concept_title}'")
        
        # Load character profiles from file
        char_file = current_dir / "data" / "character_profiles.md"
        with open(char_file, "r", encoding="utf-8") as f:
            characters = f.read()

        inputs = {
            "characters": characters,
            "concept_title": concept_title
        }
        
        result = self.orchestrator.run_crew(
            crew_name="Step2_Write",
            inputs=inputs,
            filename_suffix="knowledge",
            mode=ExecutionMode.INTERACTIVE
        )
        return result

# --- 3. Tools Application ---
class BedtimeStoryToolsApp(AmshaCrewFileApplication):
    def __init__(self, llm_type: LLMType):
        config_paths = {
            "llm": str(CONFIG_DIR / "llm_settings.yaml"),
            "app": str(CONFIG_DIR / "app_config.yaml"),
            "job": str(PIPELINE_CONFIG_DIR / "job_tools.yaml"), # Points to tools job
        }
        super().__init__(config_paths, llm_type)
        
        # Monkey-patch specifically for this instance's class flow if needed, 
        # but here we can just target the global service since we run sequentially.
        self._inject_tools()

    def _inject_tools(self):
         # Monkey-patch AtomicYamlBuilderService.add_agent to inject our tool
        original_add_agent = AtomicYamlBuilderService.add_agent

        def add_agent_with_tool(service_self, knowledge_sources=None, tools=None):
            # Only inject for the Editor agent
            if "Editor" in service_self.agent_yaml_file: # Check filename or key
                print(f"🔧 Injecting TextStatsTool for Editor agent...")
                tools = tools or []
                tools.append(TextStatsTool())
            return original_add_agent(service_self, knowledge_sources=knowledge_sources, tools=tools)

        AtomicYamlBuilderService.add_agent = add_agent_with_tool

    def run(self, rough_draft: str) -> str:
        print(f"\n🛠️ Running Tools App with rough draft (len={len(rough_draft)})")
        
        inputs = {"rough_draft": rough_draft}
        
        result = self.orchestrator.run_crew(
            crew_name="Step3_Polish",
            inputs=inputs,
            filename_suffix="tools",
            mode=ExecutionMode.INTERACTIVE
        )
        return result

# --- Main Coordinator ---
def main():
    # Redirect stdout/stderr to avoid Windows encoding issues in console
    log_file_path = "test_modular_output.log"
    original_stdout = sys.stdout
    original_stderr = sys.stderr
    
    # Simple print patch for encoding safety inside the redirection
    original_print = __builtins__.print
    def safe_print(*args, **kwargs):
        try:
            original_print(*args, **kwargs)
        except UnicodeEncodeError:
            encoded_args = [str(arg).encode('utf-8', errors='ignore').decode('utf-8') for arg in args]
            original_print(*encoded_args, **kwargs)
    __builtins__.print = safe_print

    print(f"Running Modular Workflow Test. Logs at: {log_file_path}")

    with open(log_file_path, "w", encoding="utf-8") as f:
        sys.stdout = f
        sys.stderr = f
        
        print("Starting Modular Bedtime Story Workflows...")
        
        try:
            # 1. Basic Workflow
            app_basic = BedtimeStoryBasicApp(LLMType.CREATIVE)
            concept_output = app_basic.run(theme="Space Adventure")
            
            # Extract content from result (CrewOutput object)
            concept_text = str(concept_output)
            print(f"\n[Result Step 1]: {concept_text[:100]}...")

            # 2. Knowledge Workflow
            app_knowledge = BedtimeStoryKnowledgeApp(LLMType.CREATIVE)
            story_output = app_knowledge.run(concept_title=concept_text)
            
            story_text = str(story_output)
            print(f"\n[Result Step 2]: {story_text[:100]}...")

            # 3. Tools Workflow
            app_tools = BedtimeStoryToolsApp(LLMType.CREATIVE)
            final_output = app_tools.run(rough_draft=story_text)
            
            final_text = str(final_output)
            
            print("\n✅ All Modular Workflows Completed Successfully!")
            print("Final Polished Story:")
            print("-" * 40)
            print(final_text)
            print("-" * 40)

        except Exception as e:
            print(f"\n❌ Workflow Failed: {e}")
            import traceback
            traceback.print_exc()
        finally:
            sys.stdout = original_stdout
            sys.stderr = original_stderr
            __builtins__.print = original_print
            print("Test execution finished. Check log file.")

if __name__ == "__main__":
    main()
