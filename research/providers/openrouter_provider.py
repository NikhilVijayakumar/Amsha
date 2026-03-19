import time
from .base_provider import BaseProvider, ProviderResult
from openai import OpenAI

class OpenRouterProvider(BaseProvider):
    """
    Tier 1 Native SDK implementation for OpenRouter using the openai Python package.
    """
    def run(self, prompt: str, model_context: dict, **kwargs) -> ProviderResult:
        api_key = model_context.get("api_key")
        model = model_context.get("id", model_context.get("name"))
        
        # Initialize native SDK client exactly as OpenRouter docs suggest
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
        
        start_time = time.time()
        try:
            # We explicitly ask for usage stats in the stream response per OpenRouter docs
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
                stream=True,
                stream_options={"include_usage": True}
            )
            
            output_text = ""
            tokens_in = 0
            tokens_out = 0
            
            for chunk in response:
                if len(chunk.choices) > 0 and chunk.choices[0].delta.content:
                    output_text += chunk.choices[0].delta.content
                    
                # Usage info comes in the final chunk
                if chunk.usage:
                    tokens_in = chunk.usage.prompt_tokens
                    tokens_out = chunk.usage.completion_tokens
                    
            elapsed = time.time() - start_time
            
            return ProviderResult(
                output=output_text,
                latency_s=round(elapsed, 2),
                tokens_in=tokens_in,
                tokens_out=tokens_out,
                provider_name="openrouter",
                tier="native_sdk"
            )
            
        except Exception as e:
            elapsed = time.time() - start_time
            return ProviderResult(
                output="",
                latency_s=round(elapsed, 2),
                tokens_in=0,
                tokens_out=0,
                provider_name="openrouter",
                tier="native_sdk",
                error=str(e)
            )
