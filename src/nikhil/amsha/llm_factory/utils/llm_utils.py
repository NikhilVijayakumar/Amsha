# src/nikhil/amsha/llm_factory/utils/llm_utils.py

import os
from amsha.common.logger import get_logger

from crewai.telemetry import Telemetry

_logger = get_logger("llm_factory.utils")


class LLMUtils:

    @staticmethod
    def noop(*args, **kwargs):
        _logger.debug("Telemetry noop method called")
        pass

    @staticmethod
    def disable_telemetry():
        os.environ["OTEL_SDK_DISABLED"] = "true"
        try:
            for attr in dir(Telemetry):
                if callable(getattr(Telemetry, attr)) and not attr.startswith("__"):
                    setattr(Telemetry, attr, LLMUtils.noop)
            _logger.info("CrewAI telemetry disabled successfully")
        except ImportError:
            _logger.debug("Telemetry module not found, skipping")

    @staticmethod
    def extract_model_name(model_string):
        prefixes = ["lm_studio/", "gemini/", "open_ai/", "azure/"]  # Add any other prefixes here
        for prefix in prefixes:
            if model_string.startswith(prefix):
                return model_string[len(prefix):]  # Remove the prefix
        return model_string
