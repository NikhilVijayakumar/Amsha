from pydantic import BaseModel, Field
from typing import Dict, Optional

class GPUMetrics(BaseModel):
    utilization_percent: float
    memory_change_mb: float
    memory_start_mb: float
    memory_end_mb: float

class GeneralMetrics(BaseModel):
    model_name: Optional[str] = None
    total_tokens: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    duration_seconds: float
    cpu_usage_end_percent: float
    memory_usage_change_mb: float
    memory_usage_start_bytes: int
    memory_usage_end_bytes: int

class PerformanceMetrics(BaseModel):
    general: GeneralMetrics
    gpu: Dict[str, GPUMetrics]