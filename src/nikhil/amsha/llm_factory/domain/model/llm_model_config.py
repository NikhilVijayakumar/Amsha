from typing import Optional
from pydantic import BaseModel

# Import LLMOutputConfig outside TYPE_CHECKING so Pydantic can use it at runtime
from amsha.llm_factory.domain.model.llm_output_config import LLMOutputConfig
from amsha.llm_factory.domain.model.lmstudio_lifecycle_config import LMStudioLifecycleConfig
from amsha.llm_factory.domain.model.llm_model_capabilities import LLMModelCapabilities


class LLMModelConfig(BaseModel):
    base_url: Optional[str] = None
    model: str
    api_key: Optional[str] = None
    api_version: Optional[str] = None
    output_config: Optional[LLMOutputConfig] = None
    lmstudio_lifecycle: Optional[LMStudioLifecycleConfig] = None
    capabilities: Optional[LLMModelCapabilities] = None