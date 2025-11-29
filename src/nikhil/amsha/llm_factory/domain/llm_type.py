# src/nikhil/vak/domain/llm_factory/domain/llm_type.py
from enum import Enum


class LLMType(str, Enum):
    CREATIVE = "creative"
    EVALUATION = "evaluation"
