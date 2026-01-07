"""
Exception for crew manager errors.

This module defines the exception raised when crew manager operations fail.
"""
from amsha.crew_forge.exceptions import CrewForgeException


class CrewManagerException(CrewForgeException):
    """
    Raised when crew manager operations fail.
    
    This exception is thrown when there are failures in crew manager
    operations such as crew building, configuration loading, or
    dependency resolution.
    """
    
    def __init__(self, message: str, manager_type: str = None, operation: str = None):
        """
        Initialize the CrewManagerException.
        
        Args:
            message: The main error message
            manager_type: Optional type of manager that failed (e.g., 'FileManager', 'DBManager')
            operation: Optional operation that failed (e.g., 'build_crew', 'load_config')
        """
        super().__init__(message)
        self.manager_type = manager_type
        self.operation = operation
    
    def __str__(self) -> str:
        """Return a string representation of the exception."""
        base_message = self.message
        if self.manager_type:
            base_message = f"{self.manager_type}: {base_message}"
        if self.operation:
            base_message = f"{base_message} (Operation: {self.operation})"
        return base_message