import json
from research.utils.result_store import save_result, result_exists
from amsha.output_process.optimization.json_cleaner_utils import JsonCleanerUtils

def test_json_sanitization_recovery():
    """
    Feeds a series of known-malformed JSON responses through 
    the JsonCleanerUtils pipeline to measure its recovery rate vs standard json.loads.
    """
    print("  → Testing multi-stage JSON Sanitization Recovery Rate...")
    
    test_cases = {
        "valid": '{"key": "value"}',
        "markdown_fences": '```json\n{"key": "value"}\n```',
        "stray_text": 'Here is your output:\n{"key": "value"}',
        "concatenated": '{"key1": "val1"}{"key2": "val2"}',
        "stray_quotes": '{"title": ""The Matrix""}'
    }
    
    results = {}
    total = len(test_cases)
    recovered = 0
    std_loaded = 0
    
    for name, content in test_cases.items():
        # Standard load attempt
        std_success = False
        try:
            json.loads(content)
            std_success = True
            std_loaded += 1
        except Exception:
            pass
            
        # Amsha pipeline recovery
        amsha_success = False
        parsed = JsonCleanerUtils._clean_and_parse_string(content)
        if parsed is not None:
            amsha_success = True
            recovered += 1
            
        results[name] = {
            "std_loads_success": std_success,
            "amsha_cleaner_success": amsha_success
        }
        
    return {
        "total_cases": total,
        "standard_loads_success_rate": round(std_loaded / total, 2),
        "amsha_cleaner_recovery_rate": round(recovered / total, 2),
        "cases": results
    }

def run(model_context=None, dataset_name="default"):
    """
    Entry point for the unified runner.
    """
    model_name = model_context["name"] if model_context else "agnostic"
    experiment_name = "evaluation_pipeline"
    
    if result_exists(experiment_name, model_name, dataset_name):
        print(f"⏩ Skipping {model_name} on {dataset_name} for {experiment_name}. Result already exists.")
        return
    
    results = {
        "sanitization": test_json_sanitization_recovery()
    }
    
    save_result(experiment_name, model_name, results, dataset_name)

if __name__ == "__main__":
    print("Please run this via: python -m research.runner --experiment 4")
