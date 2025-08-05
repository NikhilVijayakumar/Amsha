# src/nikhil/amsha/llm_factory/dependency/llm_di.py
from nikhil.amsha.llm_factory.dependency.llm_builder import LLMBuilder
from nikhil.amsha.llm_factory.settings.llm_settings import LLMSettings
from nikhil.amsha.utils.yaml_utils import YamlUtils



def get_llm_settings_from_yaml(yaml_path :str) -> LLMSettings:
    raw_data = YamlUtils.yaml_safe_load(yaml_path)
    return LLMSettings(**raw_data)


def get_llm_builder(yaml_path :str) -> LLMBuilder:
    settings = get_llm_settings_from_yaml(yaml_path)
    return LLMBuilder(settings)