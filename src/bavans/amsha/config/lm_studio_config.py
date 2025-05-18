import os
from enum import Enum
from crewai import LLM
from crewai.telemetry import Telemetry

class LMStudioConfig:

    class ModelNames(Enum):
        PHI = "lm_studio/phi-4"
        GEMMA = "lm_studio/gemma-3-12b-it"
        LLAMA = "lm_studio/meta-llama-3.1-8b-instruct"
        LLAVA = "lm_studio/llava-v1.6-vicuna-13b"
        MN_LYRA_12B = "lm_studio/mn-12b-lyra-v1"
        QWEN = "lm_studio/qwen2.5-14b-instruct"
        MISTRAL_NEMO_GUTENBERG = "lm_studio/mistral-nemo-gutenberg-doppel-12b-v2"
        DARKEST_MUSE_V1 = "lm_studio/darkest-muse-v1"
        QUILL_V1 = "lm_studio/quill-v1"

    @staticmethod
    def set_environment():
        api_base = os.getenv('LM_STUDIO_API_BASE')
        api_key = os.getenv('LM_STUDIO_API_KEY')

        if not api_base or not api_key:
            raise ValueError("Missing LM Studio API environment variables.")

        os.environ['LM_STUDIO_API_BASE'] = api_base
        os.environ['LM_STUDIO_API_KEY'] = api_key

    @staticmethod
    def noop(*args, **kwargs):
        print("Telemetry method called and noop'd\n")
        pass

    @staticmethod
    def disable_telemetry():
        """Disables CrewAI telemetry and OpenTelemetry."""
        os.environ["OTEL_SDK_DISABLED"] = "true"

        try:
            for attr in dir(Telemetry):
                if callable(getattr(Telemetry, attr)) and not attr.startswith("__"):
                    setattr(Telemetry, attr, LMStudioConfig.noop)
            print("CrewAI telemetry disabled successfully.")
        except ImportError:
            print("Telemetry module not found. Skipping telemetry disabling.")

    @staticmethod
    def create_llm_creative_instance(model_name: ModelNames, ):
        LMStudioConfig.set_environment()
        return LLM(
            model=model_name.value,
            temperature=0.8,  # Encourages creativity while maintaining coherence
            top_p=0.9,  # Ensures diversity without excessive randomness
            max_completion_tokens=8192,  # Allows longer outputs for narratives
            presence_penalty=0.6,  # Reduces repetition, encourages exploration of new topics
            frequency_penalty=0.4,  # Limits overuse of common phrases
            stop=["###"]  # Helps in segmenting outputs, can be adjusted as needed
        )

    @staticmethod
    def create_llm_instance(model_name: ModelNames):
        LMStudioConfig.disable_telemetry()
        LMStudioConfig.set_environment()
        return LLM(
            model=model_name.value,
            temperature=0.0,  # Low randomness ensures logical and structured evaluation
            top_p=0.5,  # Reduces sampling diversity to maintain consistency
            presence_penalty=0.0,  # No need to push for novelty
            frequency_penalty=0.0,  # Avoids unnecessary bias in repetition control
            stop=["###"]  # Helps segment outputs for better parsing
        )





