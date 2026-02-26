from enum import Enum
from typing import Dict, Type
import logging
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
from research.providers.base_provider import BaseProvider
from research.providers.openrouter_provider import OpenRouterProvider
from research.providers.gemini_provider import GeminiProvider
from research.providers.azure_openai_provider import AzureOpenAIProvider
from research.providers.lmstudio_provider import LMStudioProvider
from research.providers.amsha_llm_provider import AmshaLLMProvider
from research.providers.amsha_crew_provider import AmshaCrewProvider

class Tier(Enum):
    NATIVE_SDK = "native_sdk"
    AMSHA_LLM = "amsha_llm"
    AMSHA_CREW = "amsha_crew"

class TaskAdapter:
    """
    Routes a benchmark task to the correct provider wrapper based on the tier
    and the model provider.
    """
    
    _NATIVE_PROVIDERS: Dict[str, Type[BaseProvider]] = {
        "openrouter": OpenRouterProvider,
        "google": GeminiProvider,
        "azure": AzureOpenAIProvider,
        "lmstudio": LMStudioProvider
    }
    
    @staticmethod
    def get_provider(tier: Tier, provider_name: str) -> BaseProvider:
        """
        Instantiates the correct BaseProvider for the given tier and name.
        """
        if tier == Tier.NATIVE_SDK:
            provider_class = TaskAdapter._NATIVE_PROVIDERS.get(provider_name)
            if not provider_class:
                raise ValueError(f"No native SDK provider implemented for: {provider_name}")
            return provider_class()
            
        elif tier == Tier.AMSHA_LLM:
            return AmshaLLMProvider()
            
        elif tier == Tier.AMSHA_CREW:
            return AmshaCrewProvider()
            
        else:
            raise ValueError(f"Unknown tier: {tier}")

    @staticmethod
    @retry(
        wait=wait_exponential(multiplier=2, min=4, max=30),  # Gemini needs up to ~10s wait
        stop=stop_after_attempt(5),
        reraise=True
    )
    def run_with_retry(tier: Tier, provider_name: str, prompt: str, model_context: dict):
        provider = TaskAdapter.get_provider(tier, provider_name)
        result = provider.run(prompt=prompt, model_context=model_context)
        
        # If the provider itself caught the 429 and put it in error, we need to raise it so tenacity catches it
        if result.error and ("429" in result.error or "RateLimit" in result.error or "RESOURCE_EXHAUSTED" in result.error):
            logging.warning(f"Rate limit hit in {provider_name}, backing off...")
            raise Exception(f"Rate limit hit: {result.error}")
            
        return result
