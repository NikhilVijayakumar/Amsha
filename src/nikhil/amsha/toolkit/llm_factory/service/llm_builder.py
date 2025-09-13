# src/nikhil/amsha/toolkit/llm_factory/dependency/llm_builder.py

from crewai import LLM

from nikhil.amsha.toolkit.llm_factory.domain.llm_type import LLMType
from nikhil.amsha.toolkit.llm_factory.domain.models import LLMBuildResult
from nikhil.amsha.toolkit.llm_factory.settings.llm_settings import LLMSettings
from nikhil.amsha.toolkit.llm_factory.utils.llm_utils import LLMUtils


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
                api_version =model_config.api_version,
                model=model_config.model,
                temperature=params.temperature,
                top_p=params.top_p,
                max_completion_tokens=params.max_completion_tokens,
                presence_penalty=params.presence_penalty,
                frequency_penalty=params.frequency_penalty,
                stop=params.stop
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
                stop=params.stop
            )

        # Return both the LLM and its name in a structured way
        return LLMBuildResult(llm=llm_instance, model_name=clean_model_name)

    def build_creative(self, model_key: str = None) -> LLMBuildResult:
        LLMUtils.disable_telemetry()
        return self.build(LLMType.CREATIVE, model_key)

    def build_evaluation(self, model_key: str = None) -> LLMBuildResult:
        LLMUtils.disable_telemetry()
        return self.build(LLMType.EVALUATION, model_key)
