from enum import Enum

class ExecutionStatus(str, Enum):
    """
    Represents the lifecycle states of an execution.
    """
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"
