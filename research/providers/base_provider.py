from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

@dataclass
class ProviderResult:
    output: str
    latency_s: float
    tokens_in: int
    tokens_out: int
    provider_name: str
    tier: str  # e.g., "native_sdk", "amsha_llm", "amsha_crew"
    error: Optional[str] = None

class BaseProvider(ABC):
    """
    Abstract interface for all LLM execution tiers to ensure
    identical benchmark collection.
    """
    
    @abstractmethod
    def run(self, prompt: str, model_context: dict, **kwargs) -> ProviderResult:
        """
        Executes a prompt using the specific provider's implementation.
        
        Args:
            prompt: The text input to process.
            model_context: Dictionary containing model, API key, endpoint, etc.
            
        Returns:
            ProviderResult containing standard metrics and output.
        """
        pass
