import unittest
from unittest.mock import MagicMock
from amsha.llm_factory.service.llm_builder import LLMBuilder
from amsha.llm_factory.settings.llm_settings import LLMSettings
from amsha.llm_factory.domain.llm_type import LLMType
from amsha.llm_factory.infrastructure.crewai_provider import CrewAILLMProvider

class TestLLMRefactoring(unittest.TestCase):
    def setUp(self):
        self.mock_settings = MagicMock(spec=LLMSettings)
        self.builder = LLMBuilder(self.mock_settings)
        
        # Mock settings return values
        self.mock_settings.get_model_config.return_value.model = "gpt-4"
        self.mock_settings.get_model_config.return_value.base_url = None
        self.mock_settings.get_model_config.return_value.api_key = "fake-key"
        self.mock_settings.get_model_config.return_value.api_version = None
        
        # Mock parameters with correct types
        params = MagicMock()
        params.temperature = 0.7
        params.top_p = 0.9
        params.max_completion_tokens = 100
        params.presence_penalty = 0.0
        params.frequency_penalty = 0.0
        params.stop = None
        self.mock_settings.get_parameters.return_value = params

    def test_build_returns_provider(self):
        result = self.builder.build(LLMType.CREATIVE)
        
        # Check backward compatibility
        self.assertIsNotNone(result.llm)
        self.assertEqual(result.model_name, "gpt-4")
        
        # Check new provider presence
        self.assertIsNotNone(result.provider)
        self.assertIsInstance(result.provider, CrewAILLMProvider)
        
        # Check provider wraps correct LLM
        self.assertEqual(result.provider.get_raw_llm(), result.llm)
        self.assertEqual(result.provider.model_name, "gpt-4")

if __name__ == '__main__':
    unittest.main()
