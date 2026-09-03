# src/nikhil/amsha/llm_factory/domain/model/lmstudio_lifecycle_config.py
from typing import Optional

from pydantic import BaseModel


class LMStudioLifecycleConfig(BaseModel):
    """
    Opt-in config for managing a model's load state on a local LM Studio
    server before LLMBuilder.build() constructs the crewai.LLM(...).

    LM Studio only. Local only. Not read for any other provider.
    """
    enabled: bool = False
    model_id: str
    context_length: Optional[int] = None
    unload_other_models: bool = True
    max_load_retries: int = 0
    load_retry_delay_seconds: float = 2.0
