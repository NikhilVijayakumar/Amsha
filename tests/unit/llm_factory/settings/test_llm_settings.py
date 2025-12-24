"""
Unit tests for LLMSettings class.
"""
import unittest
from amsha.llm_factory.settings.llm_settings import LLMSettings
from amsha.llm_factory.domain.model.llm_use_case_config import LLMUseCaseConfig
from amsha.llm_factory.domain.model.llm_parameters import LLMParameters
from amsha.llm_factory.domain.model.llm_model_config import LLMModelConfig


class TestLLMSettings(unittest.TestCase):
    """Test cases for LLMSettings class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create test model configs
        self.creative_model = LLMModelConfig(
            model="gpt-4",
            api_key="test-key-1",
            base_url=None,
            api_version=None
        )
        
        self.eval_model = LLMModelConfig(
            model="gpt-3.5-turbo",
            api_key="test-key-2",
            base_url="https://api.test.com",
            api_version="v1"
        )
        
        # Create test use case configs
        self.creative_config = LLMUseCaseConfig(
            default="default",
            models={"default": self.creative_model, "alternative": self.eval_model}
        )
        
        self.eval_config = LLMUseCaseConfig(
            default="standard",
            models={"standard": self.eval_model}
        )
        
        # Create test parameters
        self.creative_params = LLMParameters(
            temperature=0.9,
            top_p=0.95,
            max_completion_tokens=2000,
            presence_penalty=0.1,
            frequency_penalty=0.1,
            stop=["STOP"]
        )
        
        self.eval_params = LLMParameters(
            temperature=0.3,
            top_p=0.8,
            max_completion_tokens=1000
        )
        
        # Create settings instance
        self.settings = LLMSettings(
            llm={
                "creative": self.creative_config,
                "evaluation": self.eval_config
            },
            llm_parameters={
                "creative": self.creative_params,
                "evaluation": self.eval_params
            }
        )
    
    def test_initialization(self):
        """Test proper initialization of LLMSettings."""
        self.assertIsNotNone(self.settings.llm)
        self.assertIsNotNone(self.settings.llm_parameters)
        self.assertIn("creative", self.settings.llm)
        self.assertIn("evaluation", self.settings.llm)
    
    def test_get_model_config_default(self):
        """Test getting default model config."""
        config = self.settings.get_model_config("creative")
        
        self.assertEqual(config.model, "gpt-4")
        self.assertEqual(config.api_key, "test-key-1")
        self.assertIsNone(config.base_url)
    
    def test_get_model_config_specific_model(self):
        """Test getting specific model by key."""
        config = self.settings.get_model_config("creative", "alternative")
        
        self.assertEqual(config.model, "gpt-3.5-turbo")
        self.assertEqual(config.api_key, "test-key-2")
        self.assertEqual(config.base_url, "https://api.test.com")
    
    def test_get_model_config_invalid_use_case(self):
        """Test error handling for invalid use case."""
        with self.assertRaises(ValueError) as context:
            self.settings.get_model_config("invalid_use_case")
        
        self.assertIn("Use case 'invalid_use_case' not found", str(context.exception))
    
    def test_get_model_config_invalid_model_key(self):
        """Test error handling for invalid model key."""
        with self.assertRaises(ValueError) as context:
            self.settings.get_model_config("creative", "nonexistent")
        
        self.assertIn("Model 'nonexistent' not found", str(context.exception))
    
    def test_get_parameters_existing_use_case(self):
        """Test getting parameters for existing use case."""
        params = self.settings.get_parameters("creative")
        
        self.assertEqual(params.temperature, 0.9)
        self.assertEqual(params.top_p, 0.95)
        self.assertEqual(params.max_completion_tokens, 2000)
        self.assertEqual(params.presence_penalty, 0.1)
        self.assertEqual(params.frequency_penalty, 0.1)
        self.assertEqual(params.stop, ["STOP"])
    
    def test_get_parameters_nonexistent_use_case(self):
        """Test getting parameters for nonexistent use case returns defaults."""
        params = self.settings.get_parameters("nonexistent")
        
        # Should return default LLMParameters
        self.assertIsInstance(params, LLMParameters)
        # Check some default values
        self.assertIsNotNone(params.temperature)
    
    def test_get_parameters_evaluation(self):
        """Test getting evaluation parameters."""
        params = self.settings.get_parameters("evaluation")
        
        self.assertEqual(params.temperature, 0.3)
        self.assertEqual(params.top_p, 0.8)
        self.assertEqual(params.max_completion_tokens, 1000)
    
    def test_multiple_models_per_use_case(self):
        """Test handling multiple models in one use case."""
        # Creative has both 'default' and 'alternative' models
        default_config = self.settings.get_model_config("creative", "default")
        alt_config = self.settings.get_model_config("creative", "alternative")
        
        self.assertEqual(default_config.model, "gpt-4")
        self.assertEqual(alt_config.model, "gpt-3.5-turbo")
        self.assertNotEqual(default_config.api_key, alt_config.api_key)


if __name__ == '__main__':
    unittest.main()
