from typing import Dict, Optional, Protocol

from amsha.execution_state.domain.execution_state import ExecutionState
from amsha.execution_state.domain.enums import ExecutionStatus

class IStateRepository(Protocol):
    def save(self, state: ExecutionState) -> None:
        ...
        
    def get(self, execution_id: str) -> Optional[ExecutionState]:
        ...

class InMemoryStateRepository(IStateRepository):
    def __init__(self):
        self._storage: Dict[str, ExecutionState] = {}
        
    def save(self, state: ExecutionState) -> None:
        self._storage[state.execution_id] = state
        
    def get(self, execution_id: str) -> Optional[ExecutionState]:
        return self._storage.get(execution_id)

class StateManager:
    """
    Service to manage the lifecycle of execution states.
    Abstracs away persistence specifics.
    """
    def __init__(self, repository: Optional[IStateRepository] = None):
        self.repository = repository or InMemoryStateRepository()
        
    def create_execution(self, inputs: Optional[Dict] = None) -> ExecutionState:
        """
        Creates a new execution state and persists it.
        """
        state = ExecutionState(inputs=inputs or {})
        self.repository.save(state)
        return state
        
    def get_execution(self, execution_id: str) -> Optional[ExecutionState]:
        """
        Retrieves an execution state by ID.
        """
        return self.repository.get(execution_id)
        
    def update_status(self, execution_id: str, status: ExecutionStatus, metadata: Optional[Dict] = None) -> Optional[ExecutionState]:
        """
        Updates the status of an execution and perists the change.
        """
        state = self.repository.get(execution_id)
        if not state:
            return None
            
        state.update_status(status, metadata)
        self.repository.save(state)
        return state
