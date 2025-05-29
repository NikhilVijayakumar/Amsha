from enum import Enum

from typing import Dict, Tuple

from pydantic import BaseModel, Field


class SimilarityInput(BaseModel):
    source: str = Field(..., description="the first data")
    target: str = Field(..., description="The second data.")
    ratio:float = Field(..., description="The ratio data.")
    partial_ratio: float = Field(..., description="The partial_ratio data.")
    token_sort_ratio: float = Field(..., description="The token_sort_ratio data.")
    threshold_cosine:float= Field(..., description="The threshold_cosine data.")

class SimilarityResult(BaseModel):
    inference_ratio:Tuple[float, str] = Field(..., description="inference ratio")
    inference_partial: Tuple[float, str] = Field(..., description="inference ratio")
    inference_token_sort: Tuple[float, str] = Field(..., description="inference ratio")
    inference_cosine: Tuple[float, str] = Field(..., description="inference ratio")

class SimilarityConstants(str, Enum):
    SIMILAR = "Similar"
    NOT_SIMILAR = "Not similar"
    POTENTIALLY_RELATED = "Potentially related"
    UNLIKELY_RELATED = "Unlikely related"
    ANAGRAMMATIC_MATCH = "Anagrammatic/Token match"
    DIFFERENT_TOKEN_ORDER = "Different token order"
    SEMANTICALLY_SIMILAR = "Semantically similar"
    SEMANTICALLY_DIFFERENT = "Semantically different"