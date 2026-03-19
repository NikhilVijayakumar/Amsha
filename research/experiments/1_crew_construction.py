import time
from research.utils.result_store import save_result, result_exists
from amsha.crew_forge.orchestrator.file.amsha_crew_file_application import AmshaCrewFileApplication
from amsha.llm_factory.domain.llm_type import LLMType

def measure_crew_initialization(configs: dict) -> dict:
    """
    Measures the wall-clock time required to load YAML configs, 
    instantiate the LLM via the factory, and boot the Application layer.
    """
    print("  → Measuring Application Initialization Overhead...")
    start = time.time()
    try:
        app = AmshaCrewFileApplication(config_paths=configs, llm_type=LLMType.CREATIVE)
        elapsed = time.time() - start
        return {"success": True, "init_time_s": round(elapsed, 4)}
    except Exception as e:
        return {"success": False, "error": str(e)}

def measure_crew_assembly(configs: dict) -> dict:
    """
    Measures the time it takes CrewBuilderService to parse the YAMLs
    and assemble the live agents and tasks into a functional Crew instance.
    """
    print("  → Measuring Atomic Crew Assembly Time...")
    try:
        app = AmshaCrewFileApplication(config_paths=configs, llm_type=LLMType.CREATIVE)
        
        start = time.time()
        # Trigger the internal crew build process programmatically bypassing the full run loop
        crew_instance = app.orchestrator.manager.build_atomic_crew("research_crew", None)
        elapsed = time.time() - start
        
        return {
            "success": True, 
            "assembly_time_s": round(elapsed, 4),
            "agents_built": len(crew_instance.agents),
            "tasks_built": len(crew_instance.tasks)
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def run(model_context=None, dataset_name="default"):
    """
    Entry point for Experiment 1.
    """
    model_name = model_context["name"] if model_context else "agnostic"
    experiment_name = "crew_construction"
    
    if result_exists(experiment_name, model_name, dataset_name):
        print(f"⏩ Skipping {model_name} on {dataset_name} for {experiment_name}. Result already exists.")
        return
        
    configs = {
        "llm": "research/temp_llm_config.yaml",
        "app": "research/config/app_config.yaml",
        "job": "research/config/job_config.yaml"
    }
    
    results = {
        "initialization": measure_crew_initialization(configs),
        "assembly": measure_crew_assembly(configs)
    }
    
    save_result(experiment_name, model_name, results, dataset_name)

if __name__ == "__main__":
    print("Please run this via: python -m research.runner --experiment 1 --model <name>")
