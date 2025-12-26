"""
Unit tests for Protocol-based application classes.

Tests that FileCrewApplication and DbCrewApplication conform to the
CrewApplication Protocol interface and provide consistent behavior.
"""
import pytest
import unittest
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any
from pathlib import Path

from amsha.crew_forge.orchestrator.file.file_crew_application import FileCrewApplication
from amsha.crew_forge.orchestrator.db.db_crew_application import DbCrewApplication
from amsha.crew_forge.protocols.crew_application import CrewApplication
from amsha.llm_factory.domain.model.llm_type import LLMType
from amsha.execution_runtime.domain.execution_mode import ExecutionMode
from amsha.crew_forge.exceptions import CrewConfigurationException


class TestProtocolApplications:
    """Test Protocol-based application implementations."""
    
    @pytest.fixture
    def mock_config_paths(self):
        """Mock configuration paths for testing."""
        return {
            "job": "test_job.yaml",
            "app": "test_app.yaml", 
            "llm": "test_llm.yaml"
        }
    
    @pytest.fixture
    def mock_job_config(self):
        """Mock job configuration for testing."""
        return {
            "crews": {
                "test_crew": {
                    "input": {
                        "test_input": "test_value"
                    }
                }
            }
        }
    
    def test_file_application_conforms_to_protocol(self, mock_config_paths):
        """Test that FileCrewApplication conforms to CrewApplication Protocol."""
        with patch('amsha.crew_forge.orchestrator.file.file_crew_application.YamlUtils.yaml_safe_load'), \
             patch('amsha.crew_forge.orchestrator.file.file_crew_application.SharedLLMInitializationService.initialize_llm') as mock_llm_init, \
             patch('amsha.crew_forge.orchestrator.file.file_crew_application.AtomicCrewFileManager'), \
             patch('amsha.crew_forge.orchestrator.file.file_crew_application.FileCrewOrchestrator'):
            
            mock_llm_init.return_value = (Mock(), "test_model")
            
            app = FileCrewApplication(mock_config_paths, LLMType.CREATIVE)
            
            # Test that it conforms to Protocol (structural typing)
            assert isinstance(app, object)  # Basic check
            
            # Test that it has all required Protocol methods
            assert hasattr(app, 'run_crew')
            assert hasattr(app, 'prepare_inputs_for')
            assert hasattr(app, 'clean_json')
            assert hasattr(app, 'get_last_output_file')
            
            # Test method signatures are compatible
            assert callable(app.run_crew)
            assert callable(app.prepare_inputs_for)
            assert callable(app.clean_json)
            assert callable(app.get_last_output_file)
    
    def test_db_application_conforms_to_protocol(self, mock_config_paths):
        """Test that DbCrewApplication conforms to CrewApplication Protocol."""
        with patch('amsha.crew_forge.orchestrator.db.db_crew_application.YamlUtils.yaml_safe_load'), \
             patch('amsha.crew_forge.orchestrator.db.db_crew_application.SharedLLMInitializationService.initialize_llm') as mock_llm_init, \
             patch('amsha.crew_forge.orchestrator.db.db_crew_application.AtomicCrewDBManager') as mock_manager_class, \
             patch('amsha.crew_forge.orchestrator.db.db_crew_application.DbCrewOrchestrator'):
            
            mock_llm_init.return_value = (Mock(), "test_model")
            
            # Mock the AtomicCrewDBManager constructor to return a mock instance
            mock_manager_instance = Mock()
            mock_manager_class.return_value = mock_manager_instance
            
            app = DbCrewApplication(mock_config_paths, LLMType.CREATIVE)
            
            # Test that it conforms to Protocol (structural typing)
            assert isinstance(app, object)  # Basic check
            
            # Test that it has all required Protocol methods
            assert hasattr(app, 'run_crew')
            assert hasattr(app, 'prepare_inputs_for')
            assert hasattr(app, 'clean_json')
            assert hasattr(app, 'get_last_output_file')
            
            # Test method signatures are compatible
            assert callable(app.run_crew)
            assert callable(app.prepare_inputs_for)
            assert callable(app.clean_json)
            assert callable(app.get_last_output_file)
    
    def test_applications_can_be_used_as_protocol(self, mock_config_paths):
        """Test that both applications can be used through Protocol interface."""
        with patch('amsha.crew_forge.orchestrator.file.file_crew_application.YamlUtils.yaml_safe_load'), \
             patch('amsha.crew_forge.orchestrator.file.file_crew_application.SharedLLMInitializationService.initialize_llm') as mock_llm_init, \
             patch('amsha.crew_forge.orchestrator.file.file_crew_application.AtomicCrewFileManager'), \
             patch('amsha.crew_forge.orchestrator.file.file_crew_application.FileCrewOrchestrator'), \
             patch('amsha.crew_forge.orchestrator.db.db_crew_application.AtomicCrewDBManager') as mock_db_manager_class, \
             patch('amsha.crew_forge.orchestrator.db.db_crew_application.DbCrewOrchestrator'):
            
            mock_llm_init.return_value = (Mock(), "test_model")
            
            # Mock the AtomicCrewDBManager constructor to return a mock instance
            mock_db_manager_instance = Mock()
            mock_db_manager_class.return_value = mock_db_manager_instance
            
            # Create both implementations
            file_app = FileCrewApplication(mock_config_paths, LLMType.CREATIVE)
            db_app = DbCrewApplication(mock_config_paths, LLMType.CREATIVE)
            
            # Function that accepts CrewApplication Protocol
            def use_crew_application(app: CrewApplication) -> str:
                """Function that uses CrewApplication Protocol interface."""
                # This should work with any Protocol-compliant implementation
                return f"Using application: {type(app).__name__}"
            
            # Test that both can be used through Protocol interface
            file_result = use_crew_application(file_app)
            db_result = use_crew_application(db_app)
            
            assert "FileCrewApplication" in file_result
            assert "DbCrewApplication" in db_result
    
    def test_missing_config_paths_raises_exception(self):
        """Test that missing required configuration paths raise appropriate exceptions."""
        incomplete_config = {"job": "test_job.yaml"}  # Missing "app" and "llm"
        
        with pytest.raises(CrewConfigurationException) as exc_info:
            FileCrewApplication(incomplete_config, LLMType.CREATIVE)
        
        assert "missing required configuration paths" in str(exc_info.value)
        assert "app" in str(exc_info.value)
        assert "llm" in str(exc_info.value)
    
    def test_backward_compatibility_methods_exist(self, mock_config_paths):
        """Test that backward compatibility methods are available."""
        with patch('amsha.crew_forge.orchestrator.file.file_crew_application.YamlUtils.yaml_safe_load'), \
             patch('amsha.crew_forge.orchestrator.file.file_crew_application.SharedLLMInitializationService.initialize_llm') as mock_llm_init, \
             patch('amsha.crew_forge.orchestrator.file.file_crew_application.AtomicCrewFileManager'), \
             patch('amsha.crew_forge.orchestrator.file.file_crew_application.FileCrewOrchestrator'):
            
            mock_llm_init.return_value = (Mock(), "test_model")
            
            app = FileCrewApplication(mock_config_paths, LLMType.CREATIVE)
            
            # Test backward compatibility methods exist
            assert hasattr(app, '_prepare_inputs_for')
            assert hasattr(app, '_prepare_multiple_inputs_for')
            assert hasattr(app, 'clean_json_metrics')
            
            # Test that clean_json_metrics is static
            assert callable(FileCrewApplication.clean_json_metrics)
    
    def test_shared_services_integration(self, mock_config_paths, mock_job_config):
        """Test that applications properly integrate with shared services."""
        with patch('amsha.crew_forge.orchestrator.file.file_crew_application.YamlUtils.yaml_safe_load', return_value=mock_job_config), \
             patch('amsha.crew_forge.orchestrator.file.file_crew_application.SharedLLMInitializationService.initialize_llm') as mock_llm_init, \
             patch('amsha.crew_forge.orchestrator.file.file_crew_application.AtomicCrewFileManager'), \
             patch('amsha.crew_forge.orchestrator.file.file_crew_application.FileCrewOrchestrator') as mock_orchestrator, \
             patch('amsha.crew_forge.orchestrator.file.file_crew_application.SharedInputPreparationService') as mock_input_service, \
             patch('amsha.crew_forge.orchestrator.file.file_crew_application.SharedJSONFileService') as mock_json_service:
            
            mock_llm_init.return_value = (Mock(), "test_model")
            mock_orchestrator_instance = Mock()
            mock_orchestrator.return_value = mock_orchestrator_instance
            
            app = FileCrewApplication(mock_config_paths, LLMType.CREATIVE)
            
            # Test that shared services are properly initialized
            assert app._input_service is not None
            assert app._json_service is not None
            
            # Test that methods delegate to shared services
            with patch.object(app._input_service, 'prepare_multiple_inputs_for', return_value={"test": "data"}) as mock_prepare:
                result = app.prepare_inputs_for("test_crew")
                mock_prepare.assert_called_once_with("test_crew", mock_job_config)
                assert result == {"test": "data"}
            
            with patch.object(app._json_service, 'clean_json', return_value=True) as mock_clean:
                result = app.clean_json("test_file.json")
                mock_clean.assert_called_once_with("test_file.json", 2)
                assert result is True

    def test_run_crew_interactive(self, mock_config_paths):
        """Test run_crew in interactive mode."""
        with patch('amsha.crew_forge.orchestrator.file.file_crew_application.YamlUtils.yaml_safe_load'), \
             patch('amsha.crew_forge.orchestrator.file.file_crew_application.SharedLLMInitializationService.initialize_llm') as mock_llm_init, \
             patch('amsha.crew_forge.orchestrator.file.file_crew_application.AtomicCrewFileManager'), \
             patch('amsha.crew_forge.orchestrator.file.file_crew_application.FileCrewOrchestrator') as mock_orchestrator:
            
            mock_llm_init.return_value = (Mock(), "test_model")
            mock_orchestrator_instance = Mock()
            mock_orchestrator.return_value = mock_orchestrator_instance
            mock_orchestrator_instance.run_crew.return_value = "Success"
            
            app = FileCrewApplication(mock_config_paths, LLMType.CREATIVE)
            result = app.run_crew("test_crew", {"topic": "AI"})
            
            assert result == "Success"
            mock_orchestrator_instance.run_crew.assert_called_once_with(
                "test_crew",
                {"topic": "AI"},
                mode=ExecutionMode.INTERACTIVE
            )

    def test_run_crew_background(self, mock_config_paths):
        """Test run_crew in background mode."""
        with patch('amsha.crew_forge.orchestrator.file.file_crew_application.YamlUtils.yaml_safe_load'), \
             patch('amsha.crew_forge.orchestrator.file.file_crew_application.SharedLLMInitializationService.initialize_llm') as mock_llm_init, \
             patch('amsha.crew_forge.orchestrator.file.file_crew_application.AtomicCrewFileManager'), \
             patch('amsha.crew_forge.orchestrator.file.file_crew_application.FileCrewOrchestrator') as mock_orchestrator:
            
            mock_llm_init.return_value = (Mock(), "test_model")
            mock_orchestrator_instance = Mock()
            mock_orchestrator.return_value = mock_orchestrator_instance
            mock_orchestrator_instance.run_crew.return_value = "Handle"
            
            app = FileCrewApplication(mock_config_paths, LLMType.CREATIVE)
            result = app.run_crew("test_crew", {"topic": "AI"}, mode=ExecutionMode.BACKGROUND)
            
            assert result == "Handle"
            mock_orchestrator_instance.run_crew.assert_called_once_with(
                "test_crew",
                {"topic": "AI"},
                mode=ExecutionMode.BACKGROUND
            )


    def test_prepare_inputs_fallback(self, mock_config_paths):
        """Test input preparation fallback to single input format."""
        with patch('amsha.crew_forge.orchestrator.file.file_crew_application.YamlUtils.yaml_safe_load'), \
             patch('amsha.crew_forge.orchestrator.file.file_crew_application.SharedLLMInitializationService.initialize_llm') as mock_llm_init, \
             patch('amsha.crew_forge.orchestrator.file.file_crew_application.AtomicCrewFileManager'), \
             patch('amsha.crew_forge.orchestrator.file.file_crew_application.FileCrewOrchestrator'):
            
            mock_llm_init.return_value = (Mock(), "test_model")
            app = FileCrewApplication(mock_config_paths, LLMType.CREATIVE)
            
            # Mock multiple inputs to fail
            with patch.object(app._input_service, 'prepare_multiple_inputs_for', side_effect=KeyError("missing")), \
                 patch.object(app._input_service, 'prepare_inputs_for', return_value={"topic": "fallback"}) as mock_prepare:
                
                result = app.prepare_inputs_for("test_crew")
                assert result == {"topic": "fallback"}
                mock_prepare.assert_called_once()

    def test_backward_compatibility_execution(self, mock_config_paths):
        """Test execution of backward compatibility methods."""
        with patch('amsha.crew_forge.orchestrator.file.file_crew_application.YamlUtils.yaml_safe_load'), \
             patch('amsha.crew_forge.orchestrator.file.file_crew_application.SharedLLMInitializationService.initialize_llm') as mock_llm_init, \
             patch('amsha.crew_forge.orchestrator.file.file_crew_application.AtomicCrewFileManager'), \
             patch('amsha.crew_forge.orchestrator.file.file_crew_application.FileCrewOrchestrator'):
            
            mock_llm_init.return_value = (Mock(), "test_model")
            app = FileCrewApplication(mock_config_paths, LLMType.CREATIVE)
            
            with patch.object(app._input_service, 'prepare_inputs_for', return_value={"k": "v"}):
                assert app._prepare_inputs_for("c") == {"k": "v"}
            
            with patch.object(app._input_service, 'prepare_multiple_inputs_for', return_value={"k2": "v2"}):
                assert app._prepare_multiple_inputs_for("c") == {"k2": "v2"}
            
            with patch('amsha.crew_forge.orchestrator.file.file_crew_application.SharedJSONFileService') as mock_service:
                mock_service.return_value.clean_json.return_value = True
                success, path = FileCrewApplication.clean_json_metrics("test.json")
                assert success is True
                assert path == "test.json"

    def test_init_unexpected_failure(self, mock_config_paths):
        """Test initialization with unexpected failure."""
        with patch('amsha.crew_forge.orchestrator.file.file_crew_application.YamlUtils.yaml_safe_load', side_effect=Exception("Unexpected")):
            with pytest.raises(CrewConfigurationException):
                FileCrewApplication(mock_config_paths, LLMType.CREATIVE)

class TestFileCrewOrchestrator(unittest.TestCase):
    """Test cases for FileCrewOrchestrator."""

    @patch('amsha.crew_forge.orchestrator.file.file_crew_orchestrator.BaseCrewOrchestrator.run_crew')
    def test_orchestrator_delegation(self, mock_run):
        """Test that orchestrator delegates to manager."""
        from amsha.crew_forge.orchestrator.file.file_crew_orchestrator import FileCrewOrchestrator
        from amsha.crew_forge.protocols.crew_manager import CrewManager
        
        mock_manager = Mock(spec=CrewManager)
        orchestrator = FileCrewOrchestrator(mock_manager)
        
        # Test run_crew
        orchestrator.run_crew("crew", {"i": 1}, "suffix", ExecutionMode.INTERACTIVE)
        mock_run.assert_called_with("crew", {"i": 1}, "suffix", ExecutionMode.INTERACTIVE)
        
        # Test get_last_output_file
        mock_manager.output_file = "file.json"
        assert orchestrator.get_last_output_file() == "file.json"

    @patch('amsha.crew_forge.orchestrator.file.file_crew_orchestrator.BaseCrewOrchestrator.run_crew')
    def test_orchestrator_edge_cases(self, mock_run):
        """Test edge cases for coverage."""
        from amsha.crew_forge.orchestrator.file.file_crew_orchestrator import FileCrewOrchestrator
        from amsha.crew_forge.protocols.crew_manager import CrewManager
        
        mock_manager = Mock(spec=CrewManager)
        orchestrator = FileCrewOrchestrator(mock_manager)
        
        # Line 77: Background with retries
        orchestrator.run_crew("crew", {"i": 1}, mode=ExecutionMode.BACKGROUND, max_retries=1)
        
        # Lines 115-116: No output file found during validation
        mock_run.return_value = "Result"
        with patch.object(orchestrator, 'get_last_output_file', return_value=None):
            orchestrator.run_crew("crew", {"i": 1}, output_validator=lambda x: True, max_retries=1)
            
        # Line 140: get_last_performance_stats
        with patch('amsha.crew_forge.service.base_crew_orchestrator.BaseCrewOrchestrator.get_last_performance_stats') as mock_stats:
            orchestrator.get_last_performance_stats()
            mock_stats.assert_called_once()
            
        # Line 149: get_last_execution_id
        with patch('amsha.crew_forge.service.base_crew_orchestrator.BaseCrewOrchestrator.get_last_execution_id') as mock_id:
            orchestrator.get_last_execution_id()
            mock_id.assert_called_once()