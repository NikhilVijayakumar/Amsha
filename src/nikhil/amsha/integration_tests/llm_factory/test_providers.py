import os
import sys
import yaml
import re

from amsha.llm_factory.domain.llm_type import LLMType
from amsha.llm_factory.service.llm_builder import LLMBuilder
from amsha.llm_factory.settings.llm_settings import LLMSettings

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config", "llm_providers.yaml")

def expand_env_vars(config):
    """Recursively expand environment variables in dictionary strings."""
    if isinstance(config, dict):
        return {k: expand_env_vars(v) for k, v in config.items()}
    elif isinstance(config, list):
        return [expand_env_vars(v) for v in config]
    elif isinstance(config, str):
        # Find ${VAR_NAME} patterns
        pattern = re.compile(r'\$\{([^}]+)\}')
        
        def replace(match):
            var_name = match.group(1)
            val = os.environ.get(var_name)
            if val is None:
                print(f"⚠️  Warning: Environment variable {var_name} not set.")
                return f"MISSING_{var_name}"
            return val
            
        return pattern.sub(replace, config)
    return config

def main():
    print("Running LLM Factory Integration Tests")
    print(f"Loading config from: {CONFIG_PATH}")
    
    with open(CONFIG_PATH, 'r') as f:
        raw_config = yaml.safe_load(f)
    
    expanded_config = expand_env_vars(raw_config)
    
    # We want to iterate over each model defined in the 'creative' use case
    models = expanded_config['llm']['creative']['models']
    
    results = {}
    
    for model_key, model_config in models.items():
        print(f"\n🧪 Testing Provider: {model_key} ({model_config['model']})")
        
        # Determine if we should skip based on missing keys
        api_key = model_config.get('api_key')
        if api_key and api_key.startswith("MISSING_"):
            print(f"   ⏭️  Skipping {model_key}: Missing API Key ({api_key})")
            results[model_key] = "SKIPPED (Missing Key)"
            continue
            
        # Construct a single-model settings object for this specific test
        # We temporarily overwrite the 'default' and 'models' to focus on this one
        test_settings_dict = {
            "llm": {
                "creative": {
                    "default": model_key,
                    "models": {
                        model_key: model_config
                    }
                }
            },
            "llm_parameters": expanded_config['llm_parameters']
        }
        
        try:

            settings = LLMSettings(**test_settings_dict)
            builder = LLMBuilder(settings)
            build_result = builder.build(LLMType.CREATIVE)


            
            print(f"   ✅ Built: {build_result.model_name}")
            
            # Simple Connectivity Test
            print("   📡 Sending request: 'Hello, respond with TEST_OK'")
            response = build_result.llm.call(messages=[{"role": "user", "content": "Hello, respond with TEST_OK only."}])
            print(f"   Testing: {response}")
            
            if response:
                print("   ✅ Response received")
                results[model_key] = "PASSED"
            else:
                print("   ❌ Empty response")
                results[model_key] = "FAILED (Empty Response)"

        except Exception as e:
            print(f"   ❌ Error: {e}")
            results[model_key] = f"FAILED ({str(e)})"

    print("\n--- Test Summary ---")
    for key, result in results.items():
        print(f"{key}: {result}")



if __name__ == "__main__":
    main()
