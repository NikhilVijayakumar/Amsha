import argparse
import os
import yaml
from pathlib import Path

from research.utils.result_store import aggregate_results
from research.utils.config_bridge import generate_temp_llm_config

# Define experiments registry
EXPERIMENTS = {
    "1": "research.experiments.1_crew_construction",
    "2": "research.experiments.2_llm_performance",
    "3": "research.experiments.3_monitoring_observability",
    "4": "research.experiments.4_evaluation_pipeline",
    "5": "research.experiments.5_end_to_end",
    "6": "research.experiments.6_privacy_verification"
}

def load_config():
    config_path = Path("research/config.yaml")
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found at {config_path}")
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def get_models_by_tier(config, tier="cloud"):
    models = []
    for provider, details in config.get("providers", {}).items():
        if details.get("tier") == tier:
            for m in details.get("models", []):
                # Attach provider info for context
                m["provider"] = provider
                
                # Extract api key based on config
                api_key_env = details.get("api_key_env")
                if api_key_env:
                    m["api_key"] = os.environ.get(api_key_env)
                    
                # Extract endpoint based on config
                endpoint_env = details.get("endpoint_env")
                if endpoint_env:
                    m["endpoint"] = os.environ.get(endpoint_env)
                elif "endpoint" in details:
                    m["endpoint"] = details["endpoint"]
                    
                # Extract api version
                api_version_env = details.get("api_version_env")
                if api_version_env:
                    m["api_version"] = os.environ.get(api_version_env)
                    
                models.append(m)
    return models

def get_model_by_name(config, model_name):
    for provider, details in config.get("providers", {}).items():
        for m in details.get("models", []):
            if m.get("name") == model_name:
                m["provider"] = provider
                
                # Extract api key based on config
                api_key_env = details.get("api_key_env")
                if api_key_env:
                    m["api_key"] = os.environ.get(api_key_env)
                    
                # Extract endpoint based on config
                endpoint_env = details.get("endpoint_env")
                if endpoint_env:
                    m["endpoint"] = os.environ.get(endpoint_env)
                elif "endpoint" in details:
                    m["endpoint"] = details["endpoint"]
                    
                # Extract api version
                api_version_env = details.get("api_version_env")
                if api_version_env:
                    m["api_version"] = os.environ.get(api_version_env)
                    
                return m
    return None

def run_experiment(exp_id, model_context=None, dataset_name="default"):
    if exp_id not in EXPERIMENTS:
        print(f"Unknown experiment ID: {exp_id}")
        return
        
    module_name = EXPERIMENTS[exp_id]
    print(f"--- Running Experiment {exp_id}: {module_name} on dataset: {dataset_name} ---")
    
    # Import the module dynamically
    import importlib
    try:
        exp_module = importlib.import_module(module_name)
        if hasattr(exp_module, "run"):
            exp_module.run(model_context, dataset_name)
        else:
            print(f"Module {module_name} does not have a run(model_context, dataset_name) function.")
    except Exception as e:
        print(f"Error running {module_name}: {e}")

def main():
    # Load .env variables so that API keys are automatically available in os.environ
    try:
        import logging
        from dotenv import load_dotenv
        # The user has semicolons in their .env for comments which causes 
        # python-dotenv to spam warnings via its logger.
        logging.getLogger("dotenv.main").setLevel(logging.ERROR)
        load_dotenv(verbose=False)
    except ImportError:
        print("Warning: python-dotenv not installed. Relying on existing environment variables.")

    parser = argparse.ArgumentParser(description="Amsha Research Framework Runner")
    parser.add_argument("--aggregate", action="store_true", help="Aggregate all JSON results in research/results/")
    parser.add_argument("--experiment", type=str, choices=list(EXPERIMENTS.keys()) + ["all"], help="Specific experiment ID to run (1-6) or 'all'")
    
    model_group = parser.add_mutually_exclusive_group()
    model_group.add_argument("--model", type=str, help="Specific model name to run (e.g. 'qwen3-14b')")
    model_group.add_argument("--all-remote", action="store_true", help="Run with all cloud-tier models defined in config")
    model_group.add_argument("--all-local", action="store_true", help="Run with all local-tier models defined in config")

    args = parser.parse_args()

    if args.aggregate:
        print("Aggregating intermediate JSON results...")
        aggregate_results()
        return

    config = load_config()

    # Determine which models to run against
    target_models = []
    if args.model:
        m = get_model_by_name(config, args.model)
        if m:
            target_models.append(m)
        else:
            print(f"Model '{args.model}' not found in config.yaml")
            return
    elif args.all_remote:
        target_models = get_models_by_tier(config, tier="cloud")
    elif args.all_local:
        target_models = get_models_by_tier(config, tier="local")
    else:
        # If no model specified, run with a None context (useful for non-model specific tests like Crew Construction)
        target_models = [None] 

    # Determine which experiments to run
    exps_to_run = list(EXPERIMENTS.keys()) if args.experiment == "all" else [args.experiment] if args.experiment else []
    
    if not exps_to_run:
        parser.print_help()
        return

    import time
    DATASETS = ["simple_task", "medium_task", "complex_task"]
    
    for exp_id in exps_to_run:
        for idx, model in enumerate(target_models):
            if model:
                print(f"\n>> Executing with Model Context: {model.get('name')} ({model.get('provider')})")
                generate_temp_llm_config(model)
                
            for dataset in DATASETS:
                run_experiment(exp_id, model_context=model, dataset_name=dataset)
            
            # Sleep 2 seconds between remote model calls if we are batch running multiple to respect rate limits
            if len(target_models) > 1 and idx < len(target_models) - 1:
                print("Sleeping for 2 seconds to respect remote API rate limits...")
                time.sleep(2)

if __name__ == "__main__":
    main()
