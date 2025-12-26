# src/nikhil/amsha/llm_factory/service/llm_builder.py
from amsha.llm_factory.domain.model.llm_type import LLMType
from amsha.llm_factory.domain.model.llm_build_result import LLMBuildResult
from amsha.llm_factory.settings.llm_settings import LLMSettings
from amsha.llm_factory.utils.llm_utils import LLMUtils
from crewai import LLM



from amsha.llm_factory.adapters.crewai_adapter import CrewAIProviderAdapter


class LLMBuilder:
    def __init__(self, settings: LLMSettings):
        self.settings: LLMSettings = settings

    def build(self, llm_type: LLMType, model_key: str = None) -> LLMBuildResult:
        model_config = self.settings.get_model_config(llm_type.value, model_key)
        params = self.settings.get_parameters(llm_type.value)

        clean_model_name = LLMUtils.extract_model_name(model_config.model)
        if model_config.base_url is None:
            llm_instance = LLM(
                api_key=model_config.api_key,
                api_version=model_config.api_version,
                model=model_config.model,
                temperature=params.temperature,
                top_p=params.top_p,
                max_completion_tokens=params.max_completion_tokens,
                presence_penalty=params.presence_penalty,
                frequency_penalty=params.frequency_penalty,
                stop=params.stop,
                stream=True,
                drop_params=True
            )
        else:
            llm_instance = LLM(
                base_url=model_config.base_url,
                api_key=model_config.api_key,
                api_version=model_config.api_version,
                model=model_config.model,
                temperature=params.temperature,
                top_p=params.top_p,
                max_completion_tokens=params.max_completion_tokens,
                presence_penalty=params.presence_penalty,
                frequency_penalty=params.frequency_penalty,
                drop_params=True
            )


        provider = CrewAIProviderAdapter(crewai_llm=llm_instance, model_name=clean_model_name)
        
        # Return result with backward compatible llm and new provider
        return LLMBuildResult(provider=provider)

    def build_creative(self, model_key: str = None) -> LLMBuildResult:
        LLMUtils.disable_telemetry()
        return self.build(LLMType.CREATIVE, model_key)

    def build_evaluation(self, model_key: str = None) -> LLMBuildResult:
        LLMUtils.disable_telemetry()
        return self.build(LLMType.EVALUATION, model_key)


