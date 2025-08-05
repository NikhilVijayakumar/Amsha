import yaml
from pathlib import Path

from nikhil.amsha.llm_factory.dependency.llm_builder import LLMBuilder
from nikhil.amsha.llm_factory.settings.llm_settings import LLMSettings


def run_example_a(builder: LLMBuilder):
    """Example A: Build the default 'creative' LLM (phi)."""
    print("\n   => Running Example A: Building default 'creative' LLM...")
    creative_result_default = builder.build_creative()
    print(f"      Model Name: {creative_result_default.model_name}")
    print(f"      Full Model Path: {creative_result_default.llm.model}")
    print(f"      Temperature: {creative_result_default.llm.temperature}")

def run_example_b(builder: LLMBuilder):
    """Example B: Build a specific 'creative' LLM (llama)."""
    print("\n   => Running Example B: Building specific 'llama' creative LLM...")
    creative_result_llama = builder.build_creative(model_key="llama")
    print(f"      Model Name: {creative_result_llama.model_name}")
    print(f"      Full Model Path: {creative_result_llama.llm.model}")
    print(f"      Temperature: {creative_result_llama.llm.temperature}")

def run_example_c(builder: LLMBuilder):
    """Example C: Build the default 'evaluation' LLM (gemma)."""
    print("\n   => Running Example C: Building default 'evaluation' LLM...")
    # This will also trigger the 'disable_telemetry' utility.
    evaluation_result_default = builder.build_evaluation()
    print(f"      Model Name: {evaluation_result_default.model_name}")
    print(f"      Full Model Path: {evaluation_result_default.llm.model}")
    print(f"      Temperature: {evaluation_result_default.llm.temperature}")


def main():
    """
    An example script demonstrating how to use the Amsha LLM Factory.
    """
    print("--- Running Amsha LLM Factory Example ---")

    # Define the path to your configuration file
    # This assumes you run the script from the project root directory
    config_path = Path("config/llm_config.yaml")

    if not config_path.exists():
        print(f"Error: Configuration file not found at '{config_path}'")
        return

    # --- Step 1: Client Application Loads and Validates Configuration ---
    print(f"\n1. Loading configuration from '{config_path}'...")
    try:
        with open(config_path, "r") as f:
            raw_config_data = yaml.safe_load(f)

        # This is the crucial validation step using Pydantic.
        # If the YAML is malformed, this will raise a detailed error.
        settings = LLMSettings(**raw_config_data)
        print("   Configuration loaded and validated successfully.")
    except Exception as e:
        print(f"   Error validating configuration: {e}")
        return

    # --- Step 2: Client Injects Settings into the Builder ---
    print("\n2. Initializing the LLMBuilder with the validated settings...")
    builder = LLMBuilder(settings=settings)
    print("   LLMBuilder created.")

    # --- Step 3: Run the desired example ---
    # To run a different example, comment out the current line
    # and uncomment the one you want to test.
    run_example_a(builder)
    # run_example_b(builder)
    # run_example_c(builder)

    print("\n--- Example Finished ---")


if __name__ == "__main__":
    main()
