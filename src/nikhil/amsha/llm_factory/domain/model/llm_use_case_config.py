from typing import Dict

from amsha.llm_factory.domain.state import LLMModelConfig
from pydantic import BaseModel


class LLMUseCaseConfig(BaseModel):
    default: str
    models: Dict[str, LLMModelConfig]