# src/nikhil/amsha/llm_factory/service/llm_builder.py

from crewai import LLM
import litellm
import types

from amsha.llm_factory.domain.llm_type import LLMType
from amsha.llm_factory.domain.state import LLMBuildResult
from amsha.llm_factory.settings.llm_settings import LLMSettings
from amsha.llm_factory.utils.llm_utils import LLMUtils


class LLMBuilder:
    def __init__(self, settings: LLMSettings):
        self.settings: LLMSettings = settings

    def build(self, llm_type: LLMType, model_key: str = None) -> LLMBuildResult:
        model_config = self.settings.get_model_config(llm_type.value, model_key)
        params = self.settings.get_parameters(llm_type.value)

        clean_model_name = LLMUtils.extract_model_name(model_config.model)
        
        kwargs = {
            "api_key": model_config.api_key,
            "api_version": model_config.api_version,
            "model": model_config.model,
            "stream": True
        }
        
        if model_config.base_url is not None:
            kwargs["base_url"] = model_config.base_url
            
        # Selectively pass parameters, as Azure OpenAI reasoning models might reject them entirely
        if "azure" not in model_config.model.lower():
            kwargs["max_completion_tokens"] = params.max_completion_tokens
            kwargs["temperature"] = params.temperature
            kwargs["top_p"] = params.top_p
            kwargs["presence_penalty"] = params.presence_penalty
            kwargs["frequency_penalty"] = params.frequency_penalty
            if params.stop:
                kwargs["stop"] = params.stop
            
        llm_instance = LLM(**kwargs)

        # Monkeypatch litellm.completion because CrewAI passes 'stop' dynamically
        if "azure" in model_config.model.lower():
            original_completion = getattr(litellm, "completion", None)
            if original_completion and not hasattr(original_completion, "_patched_for_azure"):
                def patched_completion(*args, **ckwargs):
                    if "stop" in ckwargs:
                        ckwargs.pop("stop", None)
                    return original_completion(*args, **ckwargs)
                patched_completion._patched_for_azure = True
                litellm.completion = patched_completion

            # Also patch the kwargs of the llm_instance itself just in case
            llm_instance.stop = None

        return LLMBuildResult(llm=llm_instance, model_name=clean_model_name)

    def build_creative(self, model_key: str = None) -> LLMBuildResult:
        LLMUtils.disable_telemetry()
        return self.build(LLMType.CREATIVE, model_key)

    def build_evaluation(self, model_key: str = None) -> LLMBuildResult:
        LLMUtils.disable_telemetry()
        return self.build(LLMType.EVALUATION, model_key)
