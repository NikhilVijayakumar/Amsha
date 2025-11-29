# src/nikhil/amsha/llm_factory/example/llm_example.py
from pathlib import Path

from nikhil.amsha.llm_factory.dependency.llm_container import LLMContainer
from nikhil.amsha.llm_factory.service.llm_builder import LLMBuilder


# Import the container and the builder for type hinting




# The example runner functions remain the same.
def run_example_a(builder: LLMBuilder):
    """Example A: Build the default 'creative' LLM (phi)."""
    print("   => Running Example A: Building default 'creative' LLM...")
    creative_result_default = builder.build_creative()
    print(f"      Model Name: {creative_result_default.model_name}")
    print(f"      Full Model Path: {creative_result_default.llm.model}")
    print(f"      Temperature: {creative_result_default.llm.temperature}")


def run_example_b(builder: LLMBuilder):
    """Example B: Build a specific 'creative' LLM (llama)."""
    print("   => Running Example B: Building specific 'llama' creative LLM...")
    creative_result_llama = builder.build_creative(model_key="llama")
    print(f"      Model Name: {creative_result_llama.model_name}")
    print(f"      Full Model Path: {creative_result_llama.llm.model}")
    print(f"      Temperature: {creative_result_llama.llm.temperature}")


def run_example_c(builder: LLMBuilder):
    """Example C: Build the default 'evaluation' LLM (gemma)."""
    print("   => Running Example C: Building default 'evaluation' LLM...")
    # This will also trigger the 'disable_telemetry' utility.
    evaluation_result_default = builder.build_evaluation()
    print(f"      Model Name: {evaluation_result_default.model_name}")
    print(f"      Full Model Path: {evaluation_result_default.llm.model}")
    print(f"      Temperature: {evaluation_result_default.llm.temperature}")


def main():
    """
    An example script demonstrating how to use the Amsha LLM Factory
    with a Dependency Injection Container.
    """
    print("--- Running Amsha LLM Factory Example (with DI Container) ---")

    container = LLMContainer()

    # Use the absolute path or relative path as appropriate. 
    # Here we use the path relative to the project root or the provided path.
    config_path = Path("config/llm_config.yaml")
    container.config.llm.yaml_path.from_value(str(config_path))
    print(f"   Container configured to use '{config_path}'.")

    print("2. Requesting the Creative LLM from the container...")
    try:
        creative_result = container.creative_llm()
        print(f"   Creative LLM created: {creative_result.model_name}")
        print(f"   Full Model Path: {creative_result.llm.model}")
        
        # Test the creative LLM
        print("   Testing Creative LLM with prompt 'Hello, who are you?'...")
        response = creative_result.llm.call(messages=[{"role": "user", "content": "Hello, who are you?"}])
        print(f"   Response: {response}")

    except Exception as e:
        print(f"   Error creating/using creative LLM: {e}")

    print("3. Requesting the Evaluation LLM from the container...")
    try:
        evaluation_result = container.evaluation_llm()
        print(f"   Evaluation LLM created: {evaluation_result.model_name}")
        print(f"   Full Model Path: {evaluation_result.llm.model}")

        # Test the evaluation LLM
        print("   Testing Evaluation LLM with prompt 'Hello, who are you?'...")
        response = evaluation_result.llm.call(messages=[{"role": "user", "content": "Hello, who are you?"}])
        print(f"   Response: {response}")

    except Exception as e:
        print(f"   Error creating/using evaluation LLM: {e}")

    print("--- Example Finished ---")


if __name__ == "__main__":
    main()
