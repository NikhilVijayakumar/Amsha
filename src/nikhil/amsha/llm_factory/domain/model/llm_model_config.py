from typing import Optional

from pydantic import BaseModel


class LLMModelConfig(BaseModel):
    base_url: Optional[str] = None
    model: str
    api_key: Optional[str] = None
    api_version : Optional[str] = None