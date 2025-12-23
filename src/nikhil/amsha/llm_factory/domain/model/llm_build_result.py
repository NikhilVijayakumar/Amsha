# src/nikhil/amsha/llm_factory/domain/model/llm_build_result.py
from typing import NamedTuple

from amsha.llm_factory.domain.provider_protocol import ILLMProvider


class LLMBuildResult(NamedTuple):

    provider: ILLMProvider 
