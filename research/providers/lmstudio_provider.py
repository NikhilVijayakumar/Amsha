import time
from .base_provider import BaseProvider, ProviderResult
from openai import OpenAI

class LMStudioProvider(BaseProvider):
    """
    Tier 1 Native SDK implementation for LM Studio using the openai Python package.
    """
    def run(self, prompt: str, model_context: dict, **kwargs) -> ProviderResult:
        # Default API key for LM Studio is "lm-studio"
        api_key = model_context.get("api_key", "lm-studio")
        model = model_context.get("id", model_context.get("name"))
        base_url = model_context.get("endpoint", "http://localhost:1234/v1")
        
        # Initialize native SDK client pointing to localhost
        client = OpenAI(
            base_url=base_url,
            api_key=api_key
        )
        
        start_time = time.time()
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
            )
            
            elapsed = time.time() - start_time
            
            output_text = response.choices[0].message.content or ""
            tokens_in = response.usage.prompt_tokens if response.usage else 0
            tokens_out = response.usage.completion_tokens if response.usage else 0
            
            return ProviderResult(
                output=output_text,
                latency_s=round(elapsed, 2),
                tokens_in=tokens_in,
                tokens_out=tokens_out,
                provider_name="lmstudio",
                tier="native_sdk"
            )
            
        except Exception as e:
            elapsed = time.time() - start_time
            return ProviderResult(
                output="",
                latency_s=round(elapsed, 2),
                tokens_in=0,
                tokens_out=0,
                provider_name="lmstudio",
                tier="native_sdk",
                error=str(e)
            )
