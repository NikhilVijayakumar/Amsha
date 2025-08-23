# src/nikhil/amsha/toolkit/crew_linter/domain/models/keyword_coverage_data.py
from typing import List

from pydantic import BaseModel, Field


class KeywordCoverageInput(BaseModel):
    text: str = Field(..., description="The text to check for keyword coverage.")
    keywords: List[str] = Field(..., description="A list of keywords to look for.")

class KeywordCoverageResult(BaseModel):
    all_keywords_present: bool = Field(..., description="True if all keywords are found in the text.")
    missing_keywords: List[str] = Field(..., description="A list of keywords not found in the text.")
    present_keywords: List[str] = Field(..., description="A list of keywords found in the text.")
    coverage_ratio: float = Field(..., description="The proportion of keywords found (present / total).")