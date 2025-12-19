import concurrent.futures
from typing import Any, Callable, Dict, Optional
from uuid import uuid4

from amsha.execution_state.domain.enums import ExecutionStatus
from amsha.execution_runtime.domain.execution_handle import ExecutionHandle
from amsha.execution_runtime.domain.execution_mode import ExecutionMode

class LocalExecutionHandle(ExecutionHandle):
    def __init__(self, execution_id: str, future: Optional[concurrent.futures.Future] = None, result_value: Any = None):
        self._execution_id = execution_id
        self._future = future
        self._result_value = result_value
        self._status = ExecutionStatus.PENDING if future else ExecutionStatus.COMPLETED
        self._cancelled = False
        
    @property
    def execution_id(self) -> str:
        return self._execution_id
        
    def status(self) -> ExecutionStatus:
        if self._cancelled:
            return ExecutionStatus.CANCELLED
            
        if self._future:
            if self._future.running():
                return ExecutionStatus.RUNNING
            elif self._future.done():
                if self._future.cancelled():
                    return ExecutionStatus.CANCELLED
                try:
                    self._future.result(timeout=0) # check for exception
                    return ExecutionStatus.COMPLETED
                except Exception:
                    return ExecutionStatus.FAILED
            else:
                 return ExecutionStatus.PENDING # Scheduled but not running?
        
        return self._status # If no future, it's completed (sync)
        
    def result(self, timeout: Optional[float] = None) -> Any:
        if self._future:
            try:
                return self._future.result(timeout=timeout)
            except concurrent.futures.TimeoutError:
                raise TimeoutError("Execution timed out")
            except concurrent.futures.CancelledError:
                raise RuntimeError("Execution was cancelled")
        return self._result_value
        
    def cancel(self) -> bool:
        if self._future:
             cancelled = self._future.cancel()
             if cancelled:
                 self._cancelled = True
             return cancelled
        return False

class RuntimeEngine:
    """
    Executes tasks based on the requested mode.
    """
    def __init__(self, max_workers: int = 4):
        self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
        
    def submit(self, task: Callable[..., Any], *args, mode: ExecutionMode = ExecutionMode.BACKGROUND, **kwargs) -> ExecutionHandle:
        """
        Submits a task for execution.
        """
        execution_id = str(uuid4())
        
        if mode == ExecutionMode.INTERACTIVE:
            # Run synchronously
            try:
                result = task(*args, **kwargs)
                return LocalExecutionHandle(execution_id, result_value=result)
            except Exception as e:
                # In a real system we might capture the exception in the handle better
                # For now let it propagate or wrap? 
                # Better to wrap in a failed handle? 
                # Sync execution usually expects immediate failure feedback.
                raise e 
        else:
            # Run in background
            future = self._executor.submit(task, *args, **kwargs)
            return LocalExecutionHandle(execution_id, future=future)
            
    def shutdown(self):
        self._executor.shutdown(wait=True)
