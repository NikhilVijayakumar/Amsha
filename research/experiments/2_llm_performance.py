import time
from typing import Dict, Any
from research.utils.result_store import save_result, result_exists
from research.tasks.task_adapter import TaskAdapter, Tier

def run_tier(tier: Tier, provider_name: str, dataset_content: str, model_context: dict) -> Dict[str, Any]:
    """
    Executes the benchmark task for a specific tier and returns the metrics.
    """
    print(f"\n  → Running Tier: {tier.value} [{provider_name}]...")
    try:
        result = TaskAdapter.run_with_retry(tier, provider_name, dataset_content, model_context)
        
        return {
            "success": True,
            "latency_s": result.latency_s,
            "tokens_in": result.tokens_in,
            "tokens_out": result.tokens_out,
            "error": result.error,
            "output_preview": result.output[:200] + "..." if len(result.output) > 200 else result.output
        }
    except Exception as e:
        print(f"    ❌ Error running {tier.value}: {e}")
        return {
            "success": False,
            "error": str(e)
        }

def run(model_context=None, dataset_name="default"):
    """
    Entry point for the unified runner.
    Runs the dataset through Tier 1 (Native SDK), Tier 2 (Amsha LLM), 
    and Tier 3 (Amsha CrewForge) to calculate comparative overhead.
    """
    if not model_context:
        print("Model context is required for LLM performance tests.")
        return
        
    model_name = model_context["name"]
    provider_name = model_context.get("provider", "unknown")
    experiment_name = "llm_performance"
    
    if result_exists(experiment_name, model_name, dataset_name):
        print(f"⏩ Skipping {model_name} on {dataset_name} for {experiment_name}. Result already exists.")
        return
        
    # Read actual dataset content
    from pathlib import Path
    dataset_content = "Default mock content"
    base_path = Path(f"research/datasets/{dataset_name}")
    for ext in [".txt", ".md", ".json"]:
        candidate = base_path.with_suffix(ext)
        if candidate.exists():
            with open(candidate, "r", encoding="utf-8") as f:
                dataset_content = f.read()
            print(f"📄 Loaded dataset '{dataset_name}' ({len(dataset_content)} chars)")
            break
    else:
        print(f"⚠️ No dataset file found for '{dataset_name}', using mock content.")
    
    # 1. Native SDK (Tier 1)
    # 2. Amsha LLM Factory directly (Tier 2) - CrewAI overhead removed
    # 3. Full Amsha CrewForge Pipeline (Tier 3)
    
    results = {
        "tier1_native": run_tier(Tier.NATIVE_SDK, provider_name, dataset_content, model_context),
        "tier2_amsha_llm": run_tier(Tier.AMSHA_LLM, provider_name, dataset_content, model_context),
        "tier3_amsha_crew": run_tier(Tier.AMSHA_CREW, provider_name, dataset_content, model_context)
    }
    
    # Calculate overheads if successful
    if results["tier1_native"]["success"] and results["tier2_amsha_llm"]["success"]:
        amsha_llm_overhead = results["tier2_amsha_llm"]["latency_s"] - results["tier1_native"]["latency_s"]
        results["analysis"] = {
            "amsha_llm_overhead_s": round(amsha_llm_overhead, 2)
        }
        
        if results["tier3_amsha_crew"]["success"]:
            crew_overhead = results["tier3_amsha_crew"]["latency_s"] - results["tier2_amsha_llm"]["latency_s"]
            results["analysis"]["amsha_crew_overhead_s"] = round(crew_overhead, 2)
    
    save_result(experiment_name, model_name, results, dataset_name)

if __name__ == "__main__":
    print("Please run this via: python -m research.runner --experiment 2 --model <name>")
