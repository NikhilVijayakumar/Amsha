from typing import Optional
from pydantic import BaseModel

# Import LLMOutputConfig outside TYPE_CHECKING so Pydantic can use it at runtime
from amsha.llm_factory.domain.model.llm_output_config import LLMOutputConfig


class LLMModelConfig(BaseModel):
    base_url: Optional[str] = None
    model: str
    api_key: Optional[str] = None
    api_version: Optional[str] = None
    output_config: Optional[LLMOutputConfig] = None