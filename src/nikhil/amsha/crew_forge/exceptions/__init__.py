"""
Exception hierarchy for crew_forge module.

This module defines the custom exception types used throughout the crew_forge
module to provide consistent error handling across all Protocol implementations.
"""

from .crew_forge_exception import CrewForgeException
from .crew_configuration_exception import CrewConfigurationException
from .crew_execution_exception import CrewExecutionException
from .crew_manager_exception import CrewManagerException
from .input_preparation_exception import InputPreparationException
from .error_context import ErrorContext, ErrorMessageBuilder, wrap_external_exception

__all__ = [
    'CrewForgeException',
    'CrewConfigurationException',
    'CrewExecutionException',
    'CrewManagerException',
    'InputPreparationException',
    'ErrorContext',
    'ErrorMessageBuilder',
    'wrap_external_exception'
]