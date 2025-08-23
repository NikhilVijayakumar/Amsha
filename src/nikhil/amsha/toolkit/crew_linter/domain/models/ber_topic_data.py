# src/nikhil/amsha/toolkit/crew_linter/domain/models/ber_topic_data.py
from typing import List, Dict, Tuple

from pydantic import BaseModel, Field


class BERTopicInput(BaseModel):
    texts: List[str] = Field(..., description="A list of texts to analyze for topics.")
    reference_topics: List[str] = Field(..., description="List of keywords representing expected/reference topics.")
    top_n_words: int = Field(10, description="Number of words to represent each topic.")
    similarity_threshold: float = Field(0.5, description="Threshold for topic similarity.")

class BERTopicResult(BaseModel):
    extracted_topics: Dict[int, Tuple[str, List[str]]]
    topic_similarity_scores: List[float]
    overall_alignment: bool