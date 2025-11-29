# src/nikhil/vak/domain/llm_factory/domain/model.py


from typing import Dict, List, Optional, NamedTuple

from crewai import LLM
from pydantic import BaseModel


class LLMParameters(BaseModel):
    temperature: float = 0.0
    top_p: float = 1.0
    max_completion_tokens: int = 4096
    presence_penalty: float = 0.0
    frequency_penalty: float = 0.0
    stop: Optional[List[str]] = None


class LLMModelConfig(BaseModel):
    base_url: Optional[str] = None
    model: str
    api_key: Optional[str] = None
    api_version : Optional[str] = None


class LLMUseCaseConfig(BaseModel):
    default: str
    models: Dict[str, LLMModelConfig]


class LLMBuildResult(NamedTuple):
    llm: LLM
    model_name: str
