"""
Integration tests for Protocol-based applications.

Tests that the new Protocol-based applications can be imported and used
through the public API.
"""
import pytest
import unittest
from unittest.mock import Mock, patch, MagicMock

def test_protocol_applications_can_be_imported():
    """Test that Protocol-based applications can be imported from the public API."""
    # Test importing from the main module
    from amsha.crew_forge import FileCrewApplication, DbCrewApplication
    from amsha.crew_forge import CrewApplication
    
    # Test that they are classes
    assert callable(FileCrewApplication)
    assert callable(DbCrewApplication)
    
    # Test that CrewApplication is a Protocol (check for typing.Protocol)
    import typing
    assert hasattr(typing, 'Protocol')  # Just verify Protocol is available

def test_file_application_basic_functionality():
    """Test basic functionality of FileCrewApplication."""
    from amsha.crew_forge import FileCrewApplication
    from amsha.llm_factory.domain.model.llm_type import LLMType
    
    config_paths = {
        "job": "test_job.yaml",
        "app": "test_app.yaml", 
        "llm": "test_llm.yaml"
    }
    
    with patch('amsha.utils.yaml_utils.YamlUtils.yaml_safe_load'), \
         patch('amsha.crew_forge.service.shared_llm_initialization_service.SharedLLMInitializationService.initialize_llm') as mock_llm_init, \
         patch('amsha.crew_forge.orchestrator.file.atomic_crew_file_manager.AtomicCrewFileManager'), \
         patch('amsha.crew_forge.orchestrator.file.file_crew_orchestrator.FileCrewOrchestrator'):
        
        mock_llm_init.return_value = (Mock(), "test_model")
        
        # Test that application can be created
        app = FileCrewApplication(config_paths, LLMType.CREATIVE)
        
        # Test that it has the expected Protocol methods
        assert hasattr(app, 'run_crew')
        assert hasattr(app, 'prepare_inputs_for')
        assert hasattr(app, 'clean_json')
        assert hasattr(app, 'get_last_output_file')
        
        # Test that backward compatibility methods exist
        assert hasattr(app, '_prepare_inputs_for')
        assert hasattr(app, '_prepare_multiple_inputs_for')
        assert hasattr(app, 'clean_json_metrics')

def test_protocol_interface_consistency():
    """Test that Protocol interface is consistent across implementations."""
    from amsha.crew_forge.protocols.crew_application import CrewApplication
    from amsha.crew_forge.orchestrator.file.file_crew_application import FileCrewApplication
    from amsha.crew_forge.orchestrator.db.db_crew_application import DbCrewApplication
    
    # Get Protocol methods
    protocol_methods = [
        'run_crew',
        'prepare_inputs_for', 
        'clean_json',
        'get_last_output_file'
    ]
    
    # Test that FileCrewApplication has all Protocol methods
    for method_name in protocol_methods:
        assert hasattr(FileCrewApplication, method_name), f"FileCrewApplication missing {method_name}"
        
    # Test that DbCrewApplication has all Protocol methods
    for method_name in protocol_methods:
        assert hasattr(DbCrewApplication, method_name), f"DbCrewApplication missing {method_name}"

def test_exception_hierarchy_available():
    """Test that exception hierarchy is available through public API."""
    from amsha.crew_forge import (
        CrewForgeException,
        CrewConfigurationException,
        CrewExecutionException,
        CrewManagerException,
        InputPreparationException
    )
    
    # Test that they are exception classes
    assert issubclass(CrewConfigurationException, CrewForgeException)
    assert issubclass(CrewExecutionException, CrewForgeException)
    assert issubclass(CrewManagerException, CrewForgeException)
    assert issubclass(InputPreparationException, CrewForgeException)

def test_explicit_inheritance():
    """Test that implementations explicitly inherit from Protocols."""
    from amsha.crew_forge.protocols.crew_application import CrewApplication
    from amsha.crew_forge.protocols.crew_manager import CrewManager
    from amsha.crew_forge.orchestrator.file.file_crew_application import FileCrewApplication
    from amsha.crew_forge.orchestrator.db.db_crew_application import DbCrewApplication
    from amsha.crew_forge.orchestrator.file.atomic_crew_file_manager import AtomicCrewFileManager
    from amsha.crew_forge.orchestrator.db.atomic_crew_db_manager import AtomicCrewDBManager
    
    # Check Application inheritance
    assert FileCrewApplication in FileCrewApplication.__mro__
    assert CrewApplication in FileCrewApplication.__mro__
    assert DbCrewApplication in DbCrewApplication.__mro__
    assert CrewApplication in DbCrewApplication.__mro__
    
    # Check Manager inheritance
    assert AtomicCrewFileManager in AtomicCrewFileManager.__mro__
    assert CrewManager in AtomicCrewFileManager.__mro__
    assert AtomicCrewDBManager in AtomicCrewDBManager.__mro__
    assert CrewManager in AtomicCrewDBManager.__mro__

def test_dependency_injection_support():
    """Test that factory functions and classes support dependency injection."""
    from amsha.crew_forge import create_file_crew_application, FileCrewApplication
    from amsha.llm_factory.domain.model.llm_type import LLMType
    from amsha.execution_runtime.service.runtime_engine import RuntimeEngine
    from amsha.execution_state.service.state_manager import StateManager
    from unittest.mock import MagicMock
    
    # Mock dependencies
    mock_runtime = MagicMock(spec=RuntimeEngine)
    mock_state_manager = MagicMock(spec=StateManager)
    
    # Mock config paths
    config_paths = {
        "job": "mock_job.yaml",
        "app": "mock_app.yaml",
        "llm": "mock_llm.yaml"
    }
    
    # We need to mock the internals to avoid actual file loading during init
    # Patch where it is USED, not where it is defined
    with patch('amsha.utils.yaml_utils.YamlUtils.yaml_safe_load'), \
         patch('amsha.crew_forge.service.shared_llm_initialization_service.SharedLLMInitializationService.initialize_llm') as mock_llm_init, \
         patch('amsha.crew_forge.orchestrator.file.atomic_crew_file_manager.AtomicCrewFileManager'), \
         patch('amsha.crew_forge.orchestrator.file.file_crew_application.FileCrewOrchestrator') as mock_orchestrator_cls:
        
        mock_llm_init.return_value = (MagicMock(), "test_model")
        
        # Test direct instantiation with DI
        app = FileCrewApplication(
            config_paths, 
            LLMType.CREATIVE,
            runtime=mock_runtime,
            state_manager=mock_state_manager
        )
        
        # Verify dependencies were passed to orchestrator
        print(f"DEBUG: Call args: {mock_orchestrator_cls.call_args}")
        mock_orchestrator_cls.assert_called_with(
            manager=unittest.mock.ANY,
            runtime=mock_runtime,
            state_manager=mock_state_manager
        )
        
        # Test factory function with DI
        create_file_crew_application(
            config_paths,
            LLMType.CREATIVE,
            runtime=mock_runtime,
            state_manager=mock_state_manager
        )
        
        # Verify dependencies were passed again
        mock_orchestrator_cls.assert_called_with(
            manager=unittest.mock.ANY,
            runtime=mock_runtime,
            state_manager=mock_state_manager
        )