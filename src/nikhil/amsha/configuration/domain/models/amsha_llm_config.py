from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field

class LLMModelDefinition(BaseModel):
    base_url: Optional[str] = Field(default=None, description="Base URL of the LLM API endpoint")
    model: str = Field(..., description="Model identifier string")
    api_key: Optional[str] = Field(default=None, description="API key")
    api_key_env: Optional[str] = Field(default=None, description="Environment variable name for the API key")

class LLMTypeSection(BaseModel):
    default: str = Field(..., description="The default model key to use for this type")
    models: Dict[str, LLMModelDefinition] = Field(..., description="Dictionary of available models by key")

class LLMConfigSection(BaseModel):
    creative: LLMTypeSection = Field(..., description="Creative LLM configurations")
    evaluation: LLMTypeSection = Field(..., description="Evaluation LLM configurations")

class LLMParametersTypeSection(BaseModel):
    temperature: float = Field(..., description="Model temperature")
    top_p: float = Field(..., description="Top P sampling parameter")
    max_completion_tokens: Optional[int] = Field(default=None, description="Maximum completion tokens")
    presence_penalty: Optional[float] = Field(default=None, description="Presence penalty parameter")
    frequency_penalty: Optional[float] = Field(default=None, description="Frequency penalty parameter")
    stop: Optional[List[str]] = Field(default=None, description="Stop sequences")

class LLMParametersSection(BaseModel):
    creative: LLMParametersTypeSection = Field(..., description="Parameters for creative models")
    evaluation: LLMParametersTypeSection = Field(..., description="Parameters for evaluation models")

class AmshaLLMConfig(BaseModel):
    """
    LLM API and Parameters Configuration.
    Strictly validates connections and parameters without silent defaults.
    """
    llm: LLMConfigSection = Field(..., description="Configured LLM connections by type")
    llm_parameters: LLMParametersSection = Field(..., description="Configured LLM hyper-parameters by type")
