"""
Exception for crew execution errors.

This module defines the exception raised when crew execution fails
during runtime.
"""

from .crew_forge_exception import CrewForgeException


class CrewExecutionException(CrewForgeException):
    """
    Raised when crew execution fails.
    
    This exception is thrown when there are failures during crew execution
    such as runtime errors, agent failures, or task execution problems.
    """
    
    def __init__(self, message: str, crew_name: str = None, execution_context: str = None):
        """
        Initialize the CrewExecutionException.
        
        Args:
            message: The main error message
            crew_name: Optional name of the crew that failed
            execution_context: Optional context about the execution failure
        """
        super().__init__(message, execution_context)
        self.crew_name = crew_name
        self.execution_context = execution_context
    
    def __str__(self) -> str:
        """Return a string representation of the exception."""
        base_message = self.message
        if self.crew_name:
            base_message = f"Crew '{self.crew_name}': {base_message}"
        if self.execution_context:
            base_message = f"{base_message} - Context: {self.execution_context}"
        return base_message