import time
import os
from .base_provider import BaseProvider, ProviderResult
from openai import AzureOpenAI

class AzureOpenAIProvider(BaseProvider):
    """
    Tier 1 Native SDK implementation for Azure OpenAI.
    """
    def run(self, prompt: str, model_context: dict, **kwargs) -> ProviderResult:
        api_key = model_context.get("api_key")
        model = model_context.get("id", model_context.get("name"))
        endpoint = model_context.get("endpoint")
        api_version = model_context.get("api_version", "2024-02-15-preview")
        
        # Initialize Azure native client
        client = AzureOpenAI(
            azure_endpoint=endpoint,
            api_key=api_key,
            api_version=api_version
        )
        
        start_time = time.time()
        try:
            create_kwargs = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}]
            }
            # Only add temperature if it's not a mini/reasoning model which rejects it
            if "mini" not in model.lower() and "o1" not in model.lower() and "o3" not in model.lower():
                create_kwargs["temperature"] = 0.0
                
            response = client.chat.completions.create(**create_kwargs)
            
            elapsed = time.time() - start_time
            
            output_text = response.choices[0].message.content or ""
            tokens_in = response.usage.prompt_tokens if response.usage else 0
            tokens_out = response.usage.completion_tokens if response.usage else 0
            
            return ProviderResult(
                output=output_text,
                latency_s=round(elapsed, 2),
                tokens_in=tokens_in,
                tokens_out=tokens_out,
                provider_name="azure",
                tier="native_sdk"
            )
            
        except Exception as e:
            elapsed = time.time() - start_time
            return ProviderResult(
                output="",
                latency_s=round(elapsed, 2),
                tokens_in=0,
                tokens_out=0,
                provider_name="azure",
                tier="native_sdk",
                error=str(e)
            )
