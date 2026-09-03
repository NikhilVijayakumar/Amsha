# src/nikhil/amsha/llm_factory/domain/model/llm_model_capabilities.py
from pydantic import BaseModel


class LLMModelCapabilities(BaseModel):
    """
    Declarative capability tags for a model entry in llm_config.yaml.
    Not auto-detected — the config author states what the model is good for,
    so a use case with several models can be searched by capability
    (e.g. "give me the one tagged for reasoning") instead of hardcoding a
    model_key everywhere that need comes up.
    """
    reasoning: bool = False
    vision: bool = False
    tool_use: bool = False
