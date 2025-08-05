from enum import Enum


class LLMType(str, Enum):
    CREATIVE = "creative"
    EVALUATION = "evaluation"
