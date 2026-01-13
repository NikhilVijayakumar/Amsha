from pydantic import BaseModel
from src.bavans.akashvani.bala.kadha.application.domain.common.model.input_types import DirectInputItem

class ScientificKnowledgeInput(BaseModel):
    scientific_concept: DirectInputItem
    podcast_name: DirectInputItem
