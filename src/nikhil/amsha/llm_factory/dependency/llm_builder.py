# src/nikhil/amsha/llm_factory/dependency/llm_builder.py


from crewai import LLM

from nikhil.amsha.llm_factory.domain.llm_type import LLMType
from nikhil.amsha.llm_factory.settings.llm_settings import LLMSettings



class LLMBuilder:
    def __init__(self, settings: LLMSettings):
        self.settings: LLMSettings = settings

    def build(self, llm_type: LLMType, model_key: str = None) -> LLM:
        model_config = self.settings.get_model_config(llm_type.value, model_key)
        params = self.settings.get_parameters(llm_type.value)

        return LLM(
            model=model_config.model,
            temperature=params.temperature,
            top_p=params.top_p,
            max_completion_tokens=params.max_completion_tokens,
            presence_penalty=params.presence_penalty,
            frequency_penalty=params.frequency_penalty,
            stop=params.stop
        )

    def build_creative(self, model_key: str = None) -> LLM:
        return self.build(LLMType.CREATIVE, model_key)

    def build_evaluation(self, model_key: str = None) -> LLM:
        return self.build(LLMType.EVALUATION, model_key)