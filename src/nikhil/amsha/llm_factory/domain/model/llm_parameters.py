from typing import Optional, List

from pydantic import BaseModel


class LLMParameters(BaseModel):
    temperature: float = 0.0
    top_p: float = 1.0
    max_completion_tokens: int = 4096
    presence_penalty: float = 0.0
    frequency_penalty: float = 0.0
    stop: Optional[List[str]] = None