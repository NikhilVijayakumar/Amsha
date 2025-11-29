# src/nikhil/vak/domain/llm_factory/utils/llm_utils.py

import os

from crewai.telemetry import Telemetry


class LLMUtils:

    @staticmethod
    def noop(*args, **kwargs):
        print("Telemetry method called and noop'd\n")
        pass

    @staticmethod
    def disable_telemetry():
        os.environ["OTEL_SDK_DISABLED"] = "true"
        try:
            for attr in dir(Telemetry):
                if callable(getattr(Telemetry, attr)) and not attr.startswith("__"):
                    setattr(Telemetry, attr, LLMUtils.noop)
            print("CrewAI telemetry disabled successfully.")
        except ImportError:
            print("Telemetry module not found. Skipping telemetry disabling.")

    @staticmethod
    def extract_model_name(model_string):
        prefixes = ["lm_studio/", "gemini/", "open_ai/","azure"]  # Add any other prefixes here
        for prefix in prefixes:
            if model_string.startswith(prefix):
                return model_string[len(prefix):]  # Remove the prefix
        return model_string
