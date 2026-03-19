import yaml
from pathlib import Path

def generate_temp_llm_config(model_context: dict, output_path: str = "research/temp_llm_config.yaml"):
    """
    Translates a runner model_context flat dictionary into the nested 
    YAML layout required natively by Amsha's LLMContainer.
    """
    if not model_context:
        # If running model-agnostic experiments (e.g. standard DB tests)
        return
        
    tier = model_context.get("tier", "cloud")
    provider = model_context.get("provider", "unknown")
    name = model_context.get("name", "unknown")
    
    # Extract endpoint (base_url in Amsha naming) and api_key
    base_url = model_context.get("endpoint", "")
    api_key = model_context.get("api_key", "")
    api_version = model_context.get("api_version", "")
    
    # Amsha expects a "model" field that is often prefixed or specific.
    # We will use the explicit "id" if present, otherwise fallback to "name".
    model_identifier = model_context.get("id", name)
    
    # Provider-aware model prefixing for litellm routing:
    # - Google models need "gemini/" prefix so litellm uses Gemini API (API key auth)
    #   instead of Vertex AI (which requires Google Cloud ADC credentials)
    # - Azure models already have "azure/" prefix in config.yaml
    # - OpenRouter/local models pass through as-is (base_url handles routing)
    if provider == "google" and not model_identifier.startswith("gemini/"):
        model_identifier = f"gemini/{model_identifier}"
    
    # If it's a local model using lm_studio, we don't necessarily need a prefix if the base_url is set,
    # but the native config expects exactly this nested structure:
    # llm: -> creative: -> models: -> <model_key>: -> base_url, model, api_key
    
    # For simplicity, we create a single default model setting for both creative and evaluation
    # so that the DB Application always uses the model we are currently benchmarking.
    
    # Build model config — for Google, omit base_url since gemini/ prefix auto-routes.
    # For Azure/OpenRouter/local, base_url is required for routing.
    model_config = {
        "model": model_identifier,
        "api_key": api_key
    }
    if provider != "google" and base_url:
        model_config["base_url"] = base_url
    
    config_layout = {
        "llm": {
            "creative": {
                "default": "benchmark_model",
                "models": {
                    "benchmark_model": dict(model_config)
                }
            },
            "evaluation": {
                "default": "benchmark_model",
                "models": {
                    "benchmark_model": dict(model_config)
                }
            }
        },
        "llm_parameters": {
            "creative": {
                "temperature": 0.3,
                "top_p": 0.9,
                "max_completion_tokens": 8192,
                "presence_penalty": 0.0,
                "frequency_penalty": 0.0,
                "stop": ["###"]
            },
            "evaluation": {
                "temperature": 0.0,
                "top_p": 0.5,
                "presence_penalty": 0.0,
                "frequency_penalty": 0.0,
                "stop": ["###"]
            }
        }
    }
    
    # Inject api_version if needed (e.g., for azure)
    if api_version:
        config_layout["llm"]["creative"]["models"]["benchmark_model"]["api_version"] = api_version
        config_layout["llm"]["evaluation"]["models"]["benchmark_model"]["api_version"] = api_version
    
    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(out_file, "w", encoding="utf-8") as f:
        yaml.safe_dump(config_layout, f, default_flow_style=False, sort_keys=False)
        
    print(f"🔗 Generated dynamic Amsha LLM config at: {output_path}")
    return str(out_file)
