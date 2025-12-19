from unittest.mock import MagicMock
from amsha.llm_factory.service.llm_builder import LLMBuilder
from amsha.llm_factory.settings.llm_settings import LLMSettings
from amsha.llm_factory.domain.llm_type import LLMType
from amsha.llm_factory.infrastructure.crewai_provider import CrewAILLMProvider

def debug():
    try:
        mock_settings = MagicMock(spec=LLMSettings)
        builder = LLMBuilder(mock_settings)
        
        # Mock settings return values
        mock_settings.get_model_config.return_value.model = "gpt-4"
        mock_settings.get_model_config.return_value.base_url = None
        mock_settings.get_model_config.return_value.api_key = "fake-key"
        mock_settings.get_model_config.return_value.api_version = None
        
        # Mock parameters
        params = MagicMock()
        params.temperature = 0.7
        params.top_p = 0.9
        params.max_completion_tokens = 100
        params.presence_penalty = 0.0
        params.frequency_penalty = 0.0
        params.stop = None
        mock_settings.get_parameters.return_value = params

        print("Building LLM...")
        result = builder.build(LLMType.CREATIVE)
        
        print(f"Model Name: {result.model_name}")
        print(f"LLM Object: {result.llm}")
        print(f"Provider: {result.provider}")
        
        if result.provider is None:
            raise ValueError("Provider is None")
            
        if not isinstance(result.provider, CrewAILLMProvider):
             raise ValueError(f"Provider is wrong type: {type(result.provider)}")

        if result.provider.get_raw_llm() != result.llm:
             raise ValueError("Provider does not allow access to raw LLM")
             
        print("Test Passed!")
        
    except Exception as e:
        print(f"Test Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug()
