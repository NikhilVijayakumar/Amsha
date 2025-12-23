# src/nikhil/amsha/llm_factory/adapters/crewai_adapter.py
from typing import Any
from crewai import LLM

from amsha.llm_factory.domain.provider_protocol import ILLMProvider


class CrewAIProviderAdapter(ILLMProvider):
    """
    Adapts CrewAI LLM to the ILLMProvider Protocol.
    """
    def __init__(self, crewai_llm: LLM, model_name: str):
        self._llm = crewai_llm
        self._model_name = model_name

    @property
    def model_name(self) -> str:
        return self._model_name

    def get_raw_llm(self) -> Any:
        return self._llm

