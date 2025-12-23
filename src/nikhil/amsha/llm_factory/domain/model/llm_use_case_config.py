from typing import Dict

from amsha.llm_factory.domain.model.llm_model_config import LLMModelConfig
from pydantic import BaseModel


class LLMUseCaseConfig(BaseModel):
    default: str
    models: Dict[str, LLMModelConfig]