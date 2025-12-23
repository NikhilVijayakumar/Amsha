"""
Base exception for all crew_forge errors.

This module defines the base exception class that all other crew_forge
exceptions inherit from, providing a common base for error handling.
"""


class CrewForgeException(Exception):
    """
    Base exception for all crew_forge errors.
    
    This exception serves as the base class for all crew_forge-specific
    exceptions, enabling consistent error handling and exception hierarchy
    throughout the module.
    
    All crew_forge exceptions should inherit from this base class to
    maintain consistency and enable broad exception catching when needed.
    """
    
    def __init__(self, message: str, details: str = None):
        """
        Initialize the CrewForgeException.
        
        Args:
            message: The main error message
            details: Optional additional details about the error
        """
        super().__init__(message)
        self.message = message
        self.details = details
    
    def __str__(self) -> str:
        """Return a string representation of the exception."""
        if self.details:
            return f"{self.message}: {self.details}"
        return self.message