from typing import Any, Dict, Optional, Protocol, Union

class ILLMProvider(Protocol):
    """
    Protocol defining the interface for LLM providers.
    This abstracts away the specific implementation (e.g. crewai, langchain).
    """
    
    @property
    def model_name(self) -> str:
        """Returns the name of the model being used."""
        ...
        
    def generate_text(self, prompt: str, **kwargs) -> str:
        """
        Generates text based on the prompt.
        """
        ...
        
    def get_raw_llm(self) -> Any:
        """
        Returns the underlying LLM object for backward compatibility 
        or framework-specific usage.
        """
        ...
