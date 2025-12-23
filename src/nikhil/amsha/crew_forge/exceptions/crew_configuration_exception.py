"""
Exception for crew configuration errors.

This module defines the exception raised when crew configuration
is invalid or cannot be processed.
"""

from .crew_forge_exception import CrewForgeException


class CrewConfigurationException(CrewForgeException):
    """
    Raised when crew configuration is invalid.
    
    This exception is thrown when there are issues with crew configuration
    such as missing required fields, invalid values, or malformed
    configuration structures.
    """
    
    def __init__(self, message: str, crew_name: str = None, config_details: str = None):
        """
        Initialize the CrewConfigurationException.
        
        Args:
            message: The main error message
            crew_name: Optional name of the crew with configuration issues
            config_details: Optional details about the configuration problem
        """
        super().__init__(message, config_details)
        self.crew_name = crew_name
        self.config_details = config_details
    
    def __str__(self) -> str:
        """Return a string representation of the exception."""
        base_message = self.message
        if self.crew_name:
            base_message = f"Crew '{self.crew_name}': {base_message}"
        if self.config_details:
            base_message = f"{base_message} - {self.config_details}"
        return base_message