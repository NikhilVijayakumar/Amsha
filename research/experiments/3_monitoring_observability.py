import time
import os
import psutil
from research.utils.result_store import save_result, result_exists
from amsha.crew_forge.orchestrator.file.amsha_crew_file_application import AmshaCrewFileApplication
from amsha.llm_factory.domain.llm_type import LLMType

def run_with_monitoring_toggle(configs: dict, prompt: str, enable_monitor: bool) -> dict:
    """
    Runs the pipeline with or without the CrewPerformanceMonitor telemetry 
    to isolate its performance impact.
    """
    print(f"  → Running crew execution. Telemetry enabled: {enable_monitor}")
    try:
        app = AmshaCrewFileApplication(config_paths=configs, llm_type=LLMType.CREATIVE)
        
        # Manually disable monitor if requested
        if not enable_monitor:
            app.orchestrator.monitor = None
            
        start = time.time()
        result = app.orchestrator.run_crew(
            crew_name="research_crew", 
            inputs={"dataset_content": prompt}
        )
        elapsed = time.time() - start
        
        return {"success": True, "execution_time_s": round(elapsed, 2)}
    except Exception as e:
        return {"success": False, "error": str(e)}

def parse_dataset(dataset_name: str) -> str:
    from pathlib import Path
    base_path = Path(f"research/datasets/{dataset_name}")
    for ext in [".txt", ".md", ".json"]:
        candidate = base_path.with_suffix(ext)
        if candidate.exists():
            return candidate.read_text(encoding="utf-8")
    return "Default mock content"

def run(model_context=None, dataset_name="default"):
    """
    Entry point for the unified runner.
    """
    model_name = model_context["name"] if model_context else "agnostic"
    experiment_name = "monitoring_observability"
    
    if result_exists(experiment_name, model_name, dataset_name):
        print(f"⏩ Skipping {model_name} on {dataset_name} for {experiment_name}. Result already exists.")
        return

    dataset_content = parse_dataset(dataset_name)
    configs = {
        "llm": "research/temp_llm_config.yaml",
        "app": "research/config/app_config.yaml",
        "job": "research/config/job_config.yaml"
    }
    
    # Take baseline OS metrics before execution
    process = psutil.Process(os.getpid())
    mem_before = process.memory_info().rss / (1024 * 1024)
    
    # 1. Run WITH monitoring (standard production)
    run_monitored = run_with_monitoring_toggle(configs, dataset_content, enable_monitor=True)
    
    # 2. Run WITHOUT monitoring (bare orchestration)
    run_unmonitored = run_with_monitoring_toggle(configs, dataset_content, enable_monitor=False)
    
    # Post-execution metrics
    mem_after = process.memory_info().rss / (1024 * 1024)
    ram_delta_mb = round(mem_after - mem_before, 2)
    
    results = {
        "monitored_execution": run_monitored,
        "unmonitored_execution": run_unmonitored,
        "system_ram_delta_mb": ram_delta_mb
    }
    
    if run_monitored["success"] and run_unmonitored["success"]:
        overhead = run_monitored["execution_time_s"] - run_unmonitored["execution_time_s"]
        results["monitor_overhead_s"] = round(overhead, 2)
    
    save_result(experiment_name, model_name, results, dataset_name)

if __name__ == "__main__":
    print("Please run this via: python -m research.runner --experiment 3")
