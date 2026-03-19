import time
from .base_provider import BaseProvider, ProviderResult
from google import genai
from google.genai import types

class GeminiProvider(BaseProvider):
    """
    Tier 1 Native SDK implementation for Google Gemini using the new google-genai package.
    """
    def run(self, prompt: str, model_context: dict, **kwargs) -> ProviderResult:
        api_key = model_context.get("api_key")
        model = model_context.get("id", model_context.get("name"))
        
        # Initialize native Google SDK client
        client = genai.Client(api_key=api_key)
        
        start_time = time.time()
        try:
            # Deterministic config
            config = types.GenerateContentConfig(temperature=0.0)
            
            response = client.models.generate_content(
                model=model,
                contents=prompt,
                config=config
            )
            
            elapsed = time.time() - start_time
            
            output_text = response.text or ""
            
            # Extract token usage from the response metadata
            tokens_in = 0
            tokens_out = 0
            if response.usage_metadata:
                tokens_in = response.usage_metadata.prompt_token_count
                tokens_out = response.usage_metadata.candidates_token_count
            
            return ProviderResult(
                output=output_text,
                latency_s=round(elapsed, 2),
                tokens_in=tokens_in,
                tokens_out=tokens_out,
                provider_name="gemini",
                tier="native_sdk"
            )
            
        except Exception as e:
            elapsed = time.time() - start_time
            return ProviderResult(
                output="",
                latency_s=round(elapsed, 2),
                tokens_in=0,
                tokens_out=0,
                provider_name="gemini",
                tier="native_sdk",
                error=str(e)
            )
