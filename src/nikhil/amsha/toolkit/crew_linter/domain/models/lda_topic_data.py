# src/nikhil/amsha/toolkit/crew_linter/domain/models/lda_topic_data.py
from typing import List, Tuple

from pydantic import BaseModel, Field


class LdaTopicInput(BaseModel):
    texts: List[str] = Field(..., description="A list of texts to analyze for topics.")
    reference_topics: List[str] = Field(..., description="List of keywords representing expected/reference topics.")
    num_topics: int = Field(5, description="Number of topics to extract.")
    similarity_threshold: float = Field(0.7, description="Threshold for topic similarity.")

class LdaTopicResult(BaseModel):
    extracted_topics: List[Tuple[int, List[Tuple[str, float]]]]
    topic_alignment_scores: List[float]
    overall_alignment: bool