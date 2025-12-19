from enum import Enum

class ExecutionMode(str, Enum):
    """
    Defines the mode of execution for the runtime.
    """
    INTERACTIVE = "interactive"
    BACKGROUND = "background"
    SCHEDULED = "scheduled"
