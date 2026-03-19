import os
import json
import time
import time
import platform
import psutil
from datetime import datetime
from pathlib import Path

try:
    import pynvml
    HAS_NVML = True
except ImportError:
    HAS_NVML = False

# Assuming you are running from the project root
RESULTS_DIR = Path("research/results")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

def _get_system_info():
    """Captures OS, CPU, RAM, and GPU information."""
    info = {
        "os": platform.platform(),
        "cpu_cores": psutil.cpu_count(logical=True),
        "ram_gb": round(psutil.virtual_memory().total / (1024**3), 2),
        "gpu": "None"
    }
    
    if HAS_NVML:
        try:
            pynvml.nvmlInit()
            device_count = pynvml.nvmlDeviceGetCount()
            if device_count > 0:
                handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                gpu_name = pynvml.nvmlDeviceGetName(handle)
                if isinstance(gpu_name, bytes):
                    gpu_name = gpu_name.decode('utf-8')
                info["gpu"] = gpu_name
            pynvml.nvmlShutdown()
        except Exception as e:
            print(f"Warning: Could not capture GPU info: {e}")
            
    return info

def _get_filename(experiment_name: str, model_id: str, dataset_name: str = "default"):
    """Standardizes the filename structure for results."""
    safe_model = model_id.replace("/", "_").replace(":", "_")
    safe_dataset = dataset_name.replace("/", "_").replace(":", "_")
    return f"{experiment_name}_{safe_model}_{safe_dataset}.json"

def result_exists(experiment_name: str, model_id: str, dataset_name: str = "default") -> bool:
    """
    Checks if a result chunk already exists. 
    Returns True if found, allowing the runner to lazily skip redundant execution.
    """
    filename = _get_filename(experiment_name, model_id, dataset_name)
    filepath = RESULTS_DIR / filename
    return filepath.exists()

def save_result(experiment_name: str, model_id: str, data: dict, dataset_name: str = "default"):
    """
    Saves an intermediate JSON result chunk for a specific model's run
    of a specific experiment, injecting hardware context.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = _get_filename(experiment_name, model_id, dataset_name)
    filepath = RESULTS_DIR / filename
    
    wrapper = {
        "experiment": experiment_name,
        "model_id": model_id,
        "dataset": dataset_name,
        "timestamp": timestamp,
        "system_info": _get_system_info(),
        "data": data
    }
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(wrapper, f, indent=4)
        
    print(f"✅ Saved result chunk to {filepath}")
    return filepath

def load_all_results():
    """
    Loads all JSON files in the results directory.
    """
    all_results = []
    if not RESULTS_DIR.exists():
        return all_results
        
    for file in RESULTS_DIR.glob("*.json"):
        try:
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)
                all_results.append(data)
        except Exception as e:
            print(f"Warning: Failed to load {file}: {e}")
            
    return all_results

def aggregate_results():
    """
    Aggregates all disparate JSON chunks into a single dictionary
    organized by experiment and model.
    """
    raw_results = load_all_results()
    print(f"Found {len(raw_results)} result chunks in {RESULTS_DIR}")
    
    aggregated = {}
    
    for r in raw_results:
        exp = r.get("experiment")
        model = r.get("model_id")
        dataset = r.get("dataset", "default")
        
        if not exp or not model:
            continue
            
        if exp not in aggregated:
            aggregated[exp] = {}
        if model not in aggregated[exp]:
            aggregated[exp][model] = {}
            
        aggregated[exp][model][dataset] = r.get("data", {})
        
    # Save the master aggregation
    master_path = RESULTS_DIR / "MASTER_AGGREGATION.json"
    with open(master_path, "w", encoding="utf-8") as f:
        json.dump(aggregated, f, indent=4)
        
    print(f"🎉 Successfully aggregated all results to {master_path}")
    return aggregated
