"""
Exception for input preparation errors.

This module defines the exception raised when input preparation fails.
"""
from amsha.crew_forge.exceptions import CrewForgeException


class InputPreparationException(CrewForgeException):
    """
    Raised when input preparation fails.
    
    This exception is thrown when there are failures during input preparation
    such as file loading errors, format conversion issues, or invalid
    input configurations.
    """
    
    def __init__(self, message: str, crew_name: str = None, input_source: str = None):
        """
        Initialize the InputPreparationException.
        
        Args:
            message: The main error message
            crew_name: Optional name of the crew for which input preparation failed
            input_source: Optional source of the input that failed (e.g., file path, config key)
        """
        super().__init__(message)
        self.crew_name = crew_name
        self.input_source = input_source
    
    def __str__(self) -> str:
        """Return a string representation of the exception."""
        base_message = self.message
        if self.crew_name:
            base_message = f"Crew '{self.crew_name}': {base_message}"
        if self.input_source:
            base_message = f"{base_message} (Source: {self.input_source})"
        return base_message