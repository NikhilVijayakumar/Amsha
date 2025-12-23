"""
Protocol interfaces for crew_forge module.

This module defines the Protocol interfaces that enable structural typing
and duck typing for crew_forge components, following Clean Architecture
principles and SOLID design patterns.
"""

from .crew_application import CrewApplication
from .crew_orchestrator import CrewOrchestrator
from .crew_manager import CrewManager
from .input_preparation_service import InputPreparationService

__all__ = [
    'CrewApplication',
    'CrewOrchestrator', 
    'CrewManager',
    'InputPreparationService'
]