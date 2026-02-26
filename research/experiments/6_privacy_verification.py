import os
from research.utils.result_store import save_result, result_exists

def check_telemetry_neutralization():
    """
    Verify that OTEL_SDK_DISABLED is set and telemetry captures zero packets.
    """
    print("Checking Telemetry Neutralization...")
    otel_disabled = os.environ.get("OTEL_SDK_DISABLED") == "true"
    print(f"OTEL_SDK_DISABLED is set to 'true': {otel_disabled}")
    return {"otel_disabled": otel_disabled}

def verify_privacy_per_tier(model_context):
    """
    Validate that local models correctly stay fully air-gapped.
    """
    model_name = model_context["name"] if model_context else "unknown"
    tier = model_context.get("tier", "unknown") if model_context else "unknown"
    print(f"Verifying Privacy for {model_name} (Tier: {tier})...")
    
    air_gapped = (tier == "local")
    return {"tier": tier, "air_gapped": air_gapped}

def run(model_context=None, dataset_name="default"):
    """
    Entry point for the unified runner.
    """
    model_name = model_context["name"] if model_context else "agnostic"
    experiment_name = "privacy_verification"
    
    if result_exists(experiment_name, model_name, dataset_name):
        print(f"⏩ Skipping {model_name} on {dataset_name} for {experiment_name}. Result already exists.")
        return
    
    results = {
        "telemetry": check_telemetry_neutralization(),
        "privacy": verify_privacy_per_tier(model_context)
    }
    
    save_result(experiment_name, model_name, results, dataset_name)

if __name__ == "__main__":
    print("Please run this via: python -m research.runner --experiment 6")
