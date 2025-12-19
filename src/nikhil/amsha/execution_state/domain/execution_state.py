from datetime import datetime
from typing import Dict, Any, List, Optional
from uuid import uuid4
from pydantic import BaseModel, Field

from amsha.execution_state.domain.enums import ExecutionStatus

class StateSnapshot(BaseModel):
    """
    Immutable record of state at a specific point in time.
    """
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    status: ExecutionStatus
    metadata: Dict[str, Any]

class ExecutionState(BaseModel):
    """
    Container for all state related to a specific execution.
    """
    execution_id: str = Field(default_factory=lambda: str(uuid4()))
    status: ExecutionStatus = Field(default=ExecutionStatus.PENDING)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    modified_at: datetime = Field(default_factory=datetime.utcnow)
    
    inputs: Dict[str, Any] = Field(default_factory=dict)
    outputs: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # Audit history of state changes
    history: List[StateSnapshot] = Field(default_factory=list)
    
    def update_status(self, new_status: ExecutionStatus, metadata: Optional[Dict[str, Any]] = None):
        """
        Transitions the execution to a new status and records a snapshot.
        """
        self.status = new_status
        self.modified_at = datetime.utcnow()
        
        if metadata:
            self.metadata.update(metadata)
            
        snapshot = StateSnapshot(
            status=new_status,
            metadata=metadata or {}
        )
        self.history.append(snapshot)
        
    def set_output(self, key: str, value: Any):
        """
        Updates the output dictionary.
        """
        self.outputs[key] = value
        self.modified_at = datetime.utcnow()
        
    def add_metadata(self, key: str, value: Any):
        """
        Adds or updates metadata.
        """
        self.metadata[key] = value
        self.modified_at = datetime.utcnow()
