from typing import List

from pydantic import BaseModel

from .core_principle import CorePrinciple
from .key_actor import KeyActor
from .process_step import ProcessStep


class ScienceKnowledgeBase(BaseModel):
    scientific_concept: str
    core_concept: str
    key_actors_and_components: List[KeyActor]
    story_of_process: List[ProcessStep]
    core_principles: List[CorePrinciple]
    relevant_vocabulary: List[str]