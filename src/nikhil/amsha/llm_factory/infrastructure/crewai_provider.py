from typing import Any
from crewai import LLM
from amsha.llm_factory.domain.provider_protocol import ILLMProvider
from amsha.llm_factory.domain.state import LLMBuildResult, LLMModelConfig

class CrewAILLMProvider(ILLMProvider):
    """
    Adapter for CrewAI's LLM implementation.
    """
    def __init__(self, llm: LLM):
        self._llm = llm
        
    @property
    def model_name(self) -> str:
        return self._llm.model
        
    def generate_text(self, prompt: str, **kwargs) -> str:
        # CrewAI LLM typically uses .call() or similar, but for now we map to the standard call
        # Note: crewai.LLM api might differ, using call for now based on inspection
        return self._llm.call(messages=[{"role": "user", "content": prompt}], **kwargs)
        
    def get_raw_llm(self) -> Any:
        return self._llm
