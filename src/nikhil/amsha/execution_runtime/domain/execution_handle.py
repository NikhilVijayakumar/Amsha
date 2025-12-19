from typing import Any, Protocol, Optional
from amsha.execution_state.domain.enums import ExecutionStatus

class ExecutionHandle(Protocol):
    """
    Interface for controlling and querying a running execution.
    """
    @property
    def execution_id(self) -> str:
        """Unique identifier of the execution."""
        ...
        
    def status(self) -> ExecutionStatus:
        """Current status of the execution."""
        ...
        
    def result(self, timeout: Optional[float] = None) -> Any:
        """
        Blocks until result is available or timeout.
        Returns the result or raises exception.
        """
        ...
        
    def cancel(self) -> bool:
        """
        Attempts to cancel the execution.
        Returns True if cancelled, False otherwise.
        """
        ...
