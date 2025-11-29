# Amsha LLM Factory

The Amsha LLM Factory is a common configuration and CrewAI helper library designed to be used as a dependency in other projects. It provides a structured way to manage LLM configurations and build LLM instances using dependency injection.

## Installation

### As a Library

You can install Amsha directly via pip:

```bash
pip install amsha
```


## Core Advantage: Simplified LLM Configuration

The LLM Factory's primary strength lies in its ability to abstract complex LLM setups into a simple, readable YAML configuration file. This approach offers several key benefits:

-   **Unified Configuration**: Manage all your LLM settings in one place. Whether you're using open-source models (via Ollama, LM Studio), proprietary models (Gemini, Azure OpenAI), or routing services (OpenRouter), the factory handles them all through a consistent interface. All models are treated as OpenAI-compatible, simplifying integration.
-   **Purpose-Driven Profiles**: The factory distinguishes between two primary operational modes:
    -   **Creative**: Optimized for generation tasks where variability and creativity are desired (higher temperature).
    -   **Evaluation**: Tuned for deterministic and analytical tasks (lower temperature, consistent output).
-   **Out-of-the-Box Hyperparameters**: Sensible defaults for hyperparameters (temperature, top_p, etc.) are provided for both profiles, but can be easily overridden in the config file.
-   **Flexible Model Selection**: You can configure the same underlying model for both creative and evaluation tasks, or use entirely different models (e.g., a large model for creation and a smaller, faster one for evaluation).
-   **Dependency Injection**: The entire system is built on a robust Dependency Injection (DI) framework, making it easy to swap implementations, mock for testing, and manage lifecycles.

## Usage

### LLM Factory

Amsha provides an `LLMContainer` to easily create LLM instances based on configuration. This uses dependency injection to provide pre-configured "creative" and "evaluation" LLMs.

```python
from nikhil.amsha.llm_factory.dependency.llm_container import LLMContainer
from pathlib import Path

# Initialize the container
container = LLMContainer()

# Configure the path to your LLM config file
config_path = Path("config/llm_config.yaml")
container.config.llm.yaml_path.from_value(str(config_path))

# 1. Get a Creative LLM
try:
    creative_result = container.creative_llm()
    print(f"Creative Model: {creative_result.model_name}")
    # Use the LLM instance
    # response = creative_result.llm.call(...)
except Exception as e:
    print(f"Error: {e}")

# 2. Get an Evaluation LLM
try:
    evaluation_result = container.evaluation_llm()
    print(f"Evaluation Model: {evaluation_result.model_name}")
except Exception as e:
    print(f"Error: {e}")
```

## Configuration

The LLM configuration is managed via a YAML file. See `src/nikhil/amsha/llm_factory/example/config/llm_config.yaml` for a comprehensive example.

### Example Configuration Snippet

```yaml
llm:
  creative:
    default: gpt
    models:
      gpt:
        base_url: "http://localhost:1234/v1"
        model: "lm_studio/openai/gpt-oss-20b"
        api_key: "lm_studio"
  evaluation:
    default: gemma
    models:
      gemma:
        base_url: "http://localhost:1234/v1"
        model: "lm_studio/gemma-3-12b-it"
        api_key: ""

llm_parameters:
  creative:
    temperature: 0.8
  evaluation:
    temperature: 0.0
```

The configuration supports:
- **Creative** and **Evaluation** use cases.
- Multiple models per use case (e.g., `phi`, `llama`, `gpt`).
- Detailed parameters (temperature, top_p, etc.).


