# src/nikhil/amsha/llm_factory/settings/llm_settings.py

from typing import Dict, Optional

from pydantic import BaseModel

from amsha.llm_factory.domain.model.llm_use_case_config import LLMUseCaseConfig
from amsha.llm_factory.domain.model.llm_parameters import LLMParameters
from amsha.llm_factory.domain.model.llm_model_config import LLMModelConfig


class LLMSettings(BaseModel):
    llm: Dict[str, LLMUseCaseConfig]  # creative, evaluation, etc.
    llm_parameters: Dict[str, LLMParameters]
    # Global fallback for LMStudioLifecycleConfig.context_length when a model
    # config doesn't set its own — None means "no global default, defer to
    # LM Studio's own per-model default".
    lmstudio_context_length_default: Optional[int] = None

    def get_model_config(self, use_case: str, model_key: Optional[str] = None) -> LLMModelConfig:
        use_case_config = self.llm.get(use_case)
        if not use_case_config:
            raise ValueError(f"Use case '{use_case}' not found.")

        selected_model_key = model_key or use_case_config.default
        model_config = use_case_config.models.get(selected_model_key)

        if not model_config:
            raise ValueError(f"Model '{selected_model_key}' not found in use case '{use_case}'.")

        return model_config

    def get_parameters(self, use_case: str) -> LLMParameters:
        return self.llm_parameters.get(use_case, LLMParameters())

    def get_model_key_for_capability(self, use_case: str, capability: str,
                                      model_key: Optional[str] = None) -> str:
        """Resolve a model_key tagged with the given capability within a use case.

        If model_key is given and already has that capability, it's returned
        as-is. Otherwise the first model in the use case tagged with it wins.
        Raises ValueError if nothing in the use case is tagged for it —
        capability tags are opt-in metadata, not inferred.
        """
        from amsha.llm_factory.domain.model.llm_model_capabilities import LLMModelCapabilities
        if capability not in LLMModelCapabilities.model_fields:
            raise ValueError(f"Unknown capability '{capability}'. Valid: {sorted(LLMModelCapabilities.model_fields)}.")

        use_case_config = self.llm.get(use_case)
        if not use_case_config:
            raise ValueError(f"Use case '{use_case}' not found.")

        if model_key:
            model_config = use_case_config.models.get(model_key)
            if model_config and model_config.capabilities and getattr(model_config.capabilities, capability, False):
                return model_key

        for key, model_config in use_case_config.models.items():
            if model_config.capabilities and getattr(model_config.capabilities, capability, False):
                return key

        raise ValueError(f"No model tagged with capability '{capability}' in use case '{use_case}'.")
