"""
Error context and messaging utilities for crew_forge exceptions.

This module provides utilities for creating consistent error messages
and managing error context across all crew_forge components.
"""

from typing import Dict, Any, Optional
from datetime import datetime


class ErrorContext:
    """
    Utility class for managing error context and creating consistent error messages.
    
    This class helps standardize error reporting across all crew_forge components
    by providing consistent context information and message formatting.
    """
    
    def __init__(self, component: str, operation: str = None):
        """
        Initialize error context.
        
        Args:
            component: The component where the error occurred (e.g., 'FileManager', 'DbOrchestrator')
            operation: Optional operation that was being performed when error occurred
        """
        self.component = component
        self.operation = operation
        self.timestamp = datetime.now()
        self.context_data: Dict[str, Any] = {}
    
    def add_context(self, key: str, value: Any) -> 'ErrorContext':
        """
        Add context information to the error.
        
        Args:
            key: Context key (e.g., 'crew_name', 'file_path', 'config_key')
            value: Context value
            
        Returns:
            Self for method chaining
        """
        self.context_data[key] = value
        return self
    
    def create_message(self, base_message: str) -> str:
        """
        Create a formatted error message with context.
        
        Args:
            base_message: The base error message
            
        Returns:
            Formatted error message with context information
        """
        message_parts = [base_message]
        
        if self.component:
            message_parts.insert(0, f"[{self.component}]")
        
        if self.operation:
            message_parts.append(f"during {self.operation}")
        
        return " ".join(message_parts)
    
    def get_context_details(self) -> str:
        """
        Get formatted context details for error reporting.
        
        Returns:
            Formatted string containing all context information
        """
        if not self.context_data:
            return ""
        
        details = []
        for key, value in self.context_data.items():
            details.append(f"{key}={value}")
        
        return ", ".join(details)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert error context to dictionary for structured logging.
        
        Returns:
            Dictionary representation of the error context
        """
        return {
            "component": self.component,
            "operation": self.operation,
            "timestamp": self.timestamp.isoformat(),
            "context": self.context_data
        }


class ErrorMessageBuilder:
    """
    Builder class for creating consistent error messages across crew_forge components.
    """
    
    @staticmethod
    def configuration_error(crew_name: str, issue: str, config_path: str = None) -> str:
        """
        Build a configuration error message.
        
        Args:
            crew_name: Name of the crew with configuration issues
            issue: Description of the configuration issue
            config_path: Optional path to the configuration file
            
        Returns:
            Formatted configuration error message
        """
        message = f"Configuration error for crew '{crew_name}': {issue}"
        if config_path:
            message += f" (Config: {config_path})"
        return message
    
    @staticmethod
    def execution_error(crew_name: str, stage: str, error_details: str) -> str:
        """
        Build an execution error message.
        
        Args:
            crew_name: Name of the crew that failed
            stage: Execution stage where failure occurred
            error_details: Details about the execution failure
            
        Returns:
            Formatted execution error message
        """
        return f"Execution failed for crew '{crew_name}' during {stage}: {error_details}"
    
    @staticmethod
    def manager_error(manager_type: str, operation: str, details: str) -> str:
        """
        Build a manager error message.
        
        Args:
            manager_type: Type of manager (e.g., 'FileManager', 'DBManager')
            operation: Operation that failed
            details: Error details
            
        Returns:
            Formatted manager error message
        """
        return f"{manager_type} failed during {operation}: {details}"
    
    @staticmethod
    def input_preparation_error(crew_name: str, input_source: str, issue: str) -> str:
        """
        Build an input preparation error message.
        
        Args:
            crew_name: Name of the crew for input preparation
            input_source: Source of the input (file path, config key, etc.)
            issue: Description of the preparation issue
            
        Returns:
            Formatted input preparation error message
        """
        return f"Input preparation failed for crew '{crew_name}' from source '{input_source}': {issue}"


def wrap_external_exception(
    external_error: Exception, 
    context: ErrorContext, 
    crew_forge_exception_class
):
    """
    Wrap external exceptions in crew_forge exception hierarchy.
    
    This utility function helps convert external exceptions (like FileNotFoundError,
    json.JSONDecodeError, etc.) into appropriate crew_forge exceptions while
    preserving the original error information.
    
    Args:
        external_error: The original external exception
        context: Error context information
        crew_forge_exception_class: The crew_forge exception class to wrap with
        
    Returns:
        Instance of the specified crew_forge exception class
    """
    message = context.create_message(str(external_error))
    details = context.get_context_details()
    
    # Create the crew_forge exception with context
    if hasattr(crew_forge_exception_class, '__init__'):
        # Try to create with context-specific parameters
        try:
            if 'crew_name' in context.context_data:
                return crew_forge_exception_class(
                    message=message,
                    crew_name=context.context_data['crew_name'],
                    **{k: v for k, v in context.context_data.items() if k != 'crew_name'}
                )
            else:
                return crew_forge_exception_class(message=message, details=details)
        except TypeError:
            # Fallback to basic initialization
            return crew_forge_exception_class(message)
    
    return crew_forge_exception_class(message)