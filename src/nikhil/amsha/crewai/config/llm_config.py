import os
import warnings

from crewai import LLM
from crewai.telemetry import Telemetry

from nikhil.amsha.utils.yaml_utils import YamlUtils


class LLMConfig:
    def __init__(self, yaml_path: str):
        warnings.warn(
            "The 'LLMConfig' class is deprecated and will be removed in a future version. "
            "Please use the new 'AmshaLLMFactory' by loading settings and injecting them "
            "into the 'LLMBuilder' for a more robust and testable approach.",
            DeprecationWarning,
            stacklevel=2
        )
        self.utils = YamlUtils()
        self.config = self.utils.load_llm_config(yaml_path)
        self.model_name = ""

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
                    setattr(Telemetry, attr, LLMConfig.noop)
            print("CrewAI telemetry disabled successfully.")
        except ImportError:
            print("Telemetry module not found. Skipping telemetry disabling.")

    def _create_instance(self, use_case: str, model_key: str = None):
        model_config, params = self.utils.get_llm_settings(use_case, model_key)
        self.model_name =  self.extract_model_name(model_config['model'])


        return LLM(
            model=model_config['model'],
            temperature=params.get('temperature', 0.0),
            top_p=params.get('top_p', 1.0),
            max_completion_tokens=params.get('max_completion_tokens', 4096),
            presence_penalty=params.get('presence_penalty', 0.0),
            frequency_penalty=params.get('frequency_penalty', 0.0),
            stop=params.get('stop', [])
        )

    @staticmethod
    def extract_model_name(model_string):
        prefixes = ["lm_studio/", "gemini/", "open_ai/"]  # Add any other prefixes here
        for prefix in prefixes:
            if model_string.startswith(prefix):
                return model_string[len(prefix):]  # Remove the prefix
        return model_string

    def create_creative_instance(self, model_key: str = None):
        return self._create_instance("creative", model_key)

    def create_evaluation_instance(self, model_key: str = None):
        self.disable_telemetry()
        return self._create_instance("evaluation", model_key)