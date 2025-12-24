"""
Unit tests for SharedLLMInitializationService class.
"""
import unittest
import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch
from amsha.crew_forge.service.shared_llm_initialization_service import SharedLLMInitializationService
from amsha.llm_factory.domain.model.llm_type import LLMType
from amsha.crew_forge.exceptions import CrewConfigurationException


class TestSharedLLMInitializationService(unittest.TestCase):
    """Test cases for SharedLLMInitializationService class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.service = SharedLLMInitializationService()
        self.test_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
            
    def test_initialization(self):
        """Test proper initialization of SharedLLMInitializationService."""
        self.assertIsNotNone(self.service)
        
    @patch('amsha.crew_forge.service.shared_llm_initialization_service.LLMContainer')
    def test_initialize_llm_creative_success(self, mock_container_class):
        """Test successful LLM initialization for creative use case."""
        # Create a dummy config file
        config_path = os.path.join(self.test_dir, "llm_config.yaml")
        with open(config_path, 'w') as f:
            f.write("test: config")
            
        # Setup mocks
        mock_container = mock_container_class.return_value
        mock_builder = mock_container.llm_builder.return_value
        
        mock_llm_instance = MagicMock()
        mock_build_result = MagicMock()
        mock_build_result.provider.get_raw_llm.return_value = mock_llm_instance
        mock_build_result.provider.model_name = "test-model"
        
        mock_builder.build_creative.return_value = mock_build_result
        
        # Call the service
        llm, model_name = self.service.initialize_llm(config_path, LLMType.CREATIVE)
        
        # Verify
        self.assertEqual(llm, mock_llm_instance)
        self.assertEqual(model_name, "test-model")
        mock_container.config.llm.yaml_path.from_value.assert_called_once_with(config_path)
        mock_builder.build_creative.assert_called_once()

    @patch('amsha.crew_forge.service.shared_llm_initialization_service.LLMContainer')
    def test_initialize_llm_evaluation_success(self, mock_container_class):
        """Test successful LLM initialization for evaluation use case."""
        # Create a dummy config file
        config_path = os.path.join(self.test_dir, "llm_config.yaml")
        with open(config_path, 'w') as f:
            f.write("test: config")
            
        # Setup mocks
        mock_container = mock_container_class.return_value
        mock_builder = mock_container.llm_builder.return_value
        
        mock_llm_instance = MagicMock()
        mock_build_result = MagicMock()
        mock_build_result.provider.get_raw_llm.return_value = mock_llm_instance
        mock_build_result.provider.model_name = "eval-model"
        
        mock_builder.build_evaluation.return_value = mock_build_result
        
        # Call the service
        llm, model_name = self.service.initialize_llm(config_path, LLMType.EVALUATION)
        
        # Verify
        self.assertEqual(llm, mock_llm_instance)
        self.assertEqual(model_name, "eval-model")
        mock_builder.build_evaluation.assert_called_once()

    def test_initialize_llm_file_not_found(self):
        """Test error handling when config file is missing."""
        with self.assertRaises(CrewConfigurationException) as context:
            self.service.initialize_llm("nonexistent.yaml", LLMType.CREATIVE)
        
        self.assertIn("configuration file not found", str(context.exception))

    @patch('amsha.crew_forge.service.shared_llm_initialization_service.LLMContainer')
    def test_get_model_name_from_config(self, mock_container_class):
        """Test get_model_name_from_config helper."""
        # Create a dummy config file
        config_path = os.path.join(self.test_dir, "llm_config.yaml")
        with open(config_path, 'w') as f:
            f.write("test: config")
            
        # Setup mocks
        mock_container = mock_container_class.return_value
        mock_builder = mock_container.llm_builder.return_value
        mock_build_result = MagicMock()
        mock_build_result.provider.model_name = "test-model"
        mock_builder.build_creative.return_value = mock_build_result
        
        model_name = self.service.get_model_name_from_config(config_path, LLMType.CREATIVE)
        
        self.assertEqual(model_name, "test-model")

    @patch('amsha.crew_forge.service.shared_llm_initialization_service.LLMContainer')
    @patch('pathlib.Path.exists')
    def test_initialize_llm_failure(self, mock_exists, mock_container_class):
        """Test initialize_llm failure cases."""
        # Case 1: Config file not found
        mock_exists.return_value = False
        with self.assertRaises(CrewConfigurationException):
            self.service.initialize_llm("missing.yaml", LLMType.CREATIVE)
            
        # Case 2: Invalid LLM type
        mock_exists.return_value = True
        with self.assertRaises(CrewConfigurationException):
            self.service.initialize_llm("test.yaml", MagicMock())

        # Case 3: Unexpected exception
        mock_container_class.side_effect = Exception("Unexpected")
        with self.assertRaises(CrewConfigurationException):
            self.service.initialize_llm("test.yaml", LLMType.CREATIVE)

    def test_get_model_name_from_config(self):
        """Test get_model_name_from_config."""
        with patch('amsha.crew_forge.service.shared_llm_initialization_service.SharedLLMInitializationService.initialize_llm') as mock_init:
            mock_init.return_value = (MagicMock(), "test-model")
            res = self.service.get_model_name_from_config("test.yaml", LLMType.CREATIVE)
            self.assertEqual(res, "test-model")


if __name__ == '__main__':
    unittest.main()
