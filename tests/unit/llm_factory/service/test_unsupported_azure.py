from unittest.mock import MagicMock, patch

import pytest

from amsha.llm_factory.domain.model.llm_type import LLMType
from amsha.llm_factory.exceptions import UnsupportedProviderError
from amsha.llm_factory.service.llm_builder import LLMBuilder


@pytest.mark.parametrize("model", ["azure/gpt-4", "AZURE/gpt-4", "azure_ai/model"])
def test_azure_is_rejected_before_constructing_provider(model):
    settings = MagicMock()
    settings.get_model_config.return_value.model = model
    with patch("amsha.llm_factory.service.llm_builder.LLM") as client:
        with pytest.raises(UnsupportedProviderError, match="Azure"):
            LLMBuilder(settings).build(LLMType.CREATIVE)
        client.assert_not_called()


def test_non_azure_name_containing_azure_uses_normal_path():
    settings = MagicMock()
    settings.get_model_config.return_value.model = "custom/azure-sky"
    settings.get_model_config.return_value.base_url = None
    settings.get_parameters.return_value.stop = None
    with patch("amsha.llm_factory.service.llm_builder.LLM") as client:
        LLMBuilder(settings).build(LLMType.CREATIVE)
        client.assert_called_once()
        assert client.call_args.kwargs["temperature"] == settings.get_parameters.return_value.temperature
