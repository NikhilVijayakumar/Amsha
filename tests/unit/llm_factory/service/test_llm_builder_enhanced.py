"""
Enhanced unit tests for LLMBuilder class.
"""
import unittest
from unittest.mock import MagicMock, patch
from amsha.llm_factory.service.llm_builder import LLMBuilder
from amsha.llm_factory.settings.llm_settings import LLMSettings
from amsha.llm_factory.domain.model.llm_type import LLMType
from amsha.llm_factory.domain.model.llm_use_case_config import LLMUseCaseConfig
from amsha.llm_factory.domain.model.llm_parameters import LLMParameters
from amsha.llm_factory.domain.model.llm_model_config import LLMModelConfig


class TestLLMBuilderEnhanced(unittest.TestCase):
    """Enhanced test cases for LLMBuilder class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create mock settings
        self.mock_settings = MagicMock(spec=LLMSettings)
        
        # Setup model config without base_url
        self.model_config_no_base = MagicMock()
        self.model_config_no_base.model = "gpt-4"
        self.model_config_no_base.base_url = None
        self.model_config_no_base.api_key = "test-key"
        self.model_config_no_base.api_version = None
        
        # Setup model config with base_url
        self.model_config_with_base = MagicMock()
        self.model_config_with_base.model = "custom-model"
        self.model_config_with_base.base_url = "https://custom.api.com"
        self.model_config_with_base.api_key = "custom-key"
        self.model_config_with_base.api_version = "v2"
        
        # Setup parameters
        self.params = MagicMock()
        self.params.temperature = 0.7
        self.params.top_p = 0.9
        self.params.max_completion_tokens = 1500
        self.params.presence_penalty = 0.0
        self.params.frequency_penalty = 0.0
        self.params.stop = None
        
        self.mock_settings.get_parameters.return_value = self.params
        
        self.builder = LLMBuilder(self.mock_settings)
    
    def test_initialization(self):
        """Test proper initialization of LLMBuilder."""
        self.assertEqual(self.builder.settings, self.mock_settings)
    
    @patch('amsha.llm_factory.service.llm_builder.LLM')
    @patch('amsha.llm_factory.service.llm_builder.LLMUtils.extract_model_name')
    def test_build_without_base_url(self, mock_extract, mock_llm_class):
        """Test building LLM without base_url."""
        mock_extract.return_value = "gpt-4"
        self.mock_settings.get_model_config.return_value = self.model_config_no_base
        
        result = self.builder.build(LLMType.CREATIVE)
        
        # Verify LLM was called with correct parameters
        mock_llm_class.assert_called_once()
        call_kwargs = mock_llm_class.call_args[1]
        
        self.assertEqual(call_kwargs['model'], 'gpt-4')
        self.assertEqual(call_kwargs['api_key'], 'test-key')
        self.assertIsNone(call_kwargs['api_version'])
        self.assertEqual(call_kwargs['temperature'], 0.7)
        self.assertTrue(call_kwargs['stream'])
        
        # Verify result
        self.assertIsNotNone(result.provider)
    
    @patch('amsha.llm_factory.service.llm_builder.LLM')
    @patch('amsha.llm_factory.service.llm_builder.LLMUtils.extract_model_name')
    def test_build_with_base_url(self, mock_extract, mock_llm_class):
        """Test building LLM with base_url."""
        mock_extract.return_value = "custom-model"
        self.mock_settings.get_model_config.return_value = self.model_config_with_base
        
        result = self.builder.build(LLMType.EVALUATION)
        
        # Verify LLM was called with base_url
        call_kwargs = mock_llm_class.call_args[1]
        
        self.assertEqual(call_kwargs['base_url'], 'https://custom.api.com')
        self.assertEqual(call_kwargs['model'], 'custom-model')
        self.assertEqual(call_kwargs['api_version'], 'v2')
        
        # Verify stream is not set when base_url is provided
        self.assertNotIn('stream', call_kwargs)
    
    @patch('amsha.llm_factory.service.llm_builder.LLM')
    @patch('amsha.llm_factory.service.llm_builder.LLMUtils')
    def test_build_creative(self, mock_utils, mock_llm_class):
        """Test build_creative convenience method."""
        mock_utils.extract_model_name.return_value = "gpt-4"
        self.mock_settings.get_model_config.return_value = self.model_config_no_base
        
        result = self.builder.build_creative()
        
        # Verify telemetry was disabled
        mock_utils.disable_telemetry.assert_called_once()
        
        # Verify it called build with CREATIVE type
        self.mock_settings.get_model_config.assert_called_with(LLMType.CREATIVE.value, None)
        
        self.assertIsNotNone(result.provider)
    
    @patch('amsha.llm_factory.service.llm_builder.LLM')
    @patch('amsha.llm_factory.service.llm_builder.LLMUtils')
    def test_build_evaluation(self, mock_utils, mock_llm_class):
        """Test build_evaluation convenience method."""
        mock_utils.extract_model_name.return_value = "gpt-3.5-turbo"
        self.mock_settings.get_model_config.return_value = self.model_config_no_base
        
        result = self.builder.build_evaluation()
        
        # Verify telemetry was disabled
        mock_utils.disable_telemetry.assert_called_once()
        
        # Verify it called build with EVALUATION type
        self.mock_settings.get_model_config.assert_called_with(LLMType.EVALUATION.value, None)
        
        self.assertIsNotNone(result.provider)
    
    @patch('amsha.llm_factory.service.llm_builder.LLM')
    @patch('amsha.llm_factory.service.llm_builder.LLMUtils.extract_model_name')
    def test_build_with_specific_model_key(self, mock_extract, mock_llm_class):
        """Test building with specific model key."""
        mock_extract.return_value = "custom-model"
        self.mock_settings.get_model_config.return_value = self.model_config_no_base
        
        result = self.builder.build(LLMType.CREATIVE, model_key="alternative")
        
        # Verify model_key was passed
        self.mock_settings.get_model_config.assert_called_with(
            LLMType.CREATIVE.value, "alternative"
        )
        
        self.assertIsNotNone(result.provider)
    
    @patch('amsha.llm_factory.service.llm_builder.LLM')
    @patch('amsha.llm_factory.service.llm_builder.LLMUtils')
    def test_build_creative_with_model_key(self, mock_utils, mock_llm_class):
        """Test build_creative with specific model key."""
        mock_utils.extract_model_name.return_value = "gpt-4-turbo"
        self.mock_settings.get_model_config.return_value = self.model_config_no_base
        
        result = self.builder.build_creative(model_key="turbo")
        
        self.mock_settings.get_model_config.assert_called_with(
            LLMType.CREATIVE.value, "turbo"
        )
        
        self.assertIsNotNone(result.provider)
    
    @patch('amsha.llm_factory.service.llm_builder.LLM')
    @patch('amsha.llm_factory.service.llm_builder.LLMUtils.extract_model_name')
    def test_build_returns_crewai_adapter(self, mock_extract, mock_llm_class):
        """Test that build returns result with CrewAI adapter."""
        mock_extract.return_value = "gpt-4"
        self.mock_settings.get_model_config.return_value = self.model_config_no_base
        mock_llm_instance = MagicMock()
        mock_llm_class.return_value = mock_llm_instance
        
        result = self.builder.build(LLMType.CREATIVE)
        
        # Verify provider exists and is properly initialized
        self.assertIsNotNone(result.provider)
        from amsha.llm_factory.adapters.crewai_adapter import CrewAIProviderAdapter
        self.assertIsInstance(result.provider, CrewAIProviderAdapter)
    
    @patch('amsha.llm_factory.service.llm_builder.LLM')
    @patch('amsha.llm_factory.service.llm_builder.LLMUtils.extract_model_name')
    def test_build_with_prefix_model_name(self, mock_extract, mock_llm_class):
        """Test building with prefixed model name that gets extracted."""
        mock_extract.return_value = "extracted-model"
        
        config = MagicMock()
        config.model = "lm_studio/extracted-model"
        config.base_url = None
        config.api_key = "key"
        config.api_version = None
        
        self.mock_settings.get_model_config.return_value = config
        
        result = self.builder.build(LLMType.CREATIVE)
        
        # Verify extract_model_name was called
        mock_extract.assert_called_once_with("lm_studio/extracted-model")
        
        self.assertIsNotNone(result.provider)


if __name__ == '__main__':
    unittest.main()
