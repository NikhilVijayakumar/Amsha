import time
from research.providers.base_provider import BaseProvider, ProviderResult
from amsha.crew_forge.orchestrator.file.amsha_crew_file_application import AmshaCrewFileApplication
from amsha.llm_factory.domain.llm_type import LLMType

class AmshaLLMProvider(BaseProvider):
    """
    Tier 2 implementation: Uses Amsha's unified LLMBuilder (which wraps litellm).
    Bypasses CrewAI orchestration entirely to measure raw LLM execution overhead.
    """
    def run(self, prompt: str, model_context: dict, **kwargs) -> ProviderResult:
        # Initialize Amsha application just to get the properly built LLM instance
        # Bypasses complex Pydantic parsing of LLMSettings
        configs = {
            "llm": "research/temp_llm_config.yaml",
            "app": "research/config/app_config.yaml",
            "job": "research/config/job_config.yaml"
        }
        
        start_time = time.time()
        try:
            # Init app without running a crew, just extracting the built CrewAI LLM
            app = AmshaCrewFileApplication(config_paths=configs, llm_type=LLMType.CREATIVE)
            llm_instance = app.orchestrator.manager.llm
            
            # Direct litellm call via CrewAI's LLM wrapper
            response = llm_instance.call(messages=[{"role": "user", "content": prompt}])
            
            elapsed = time.time() - start_time
            
            # Since CrewAI's .call() currently returns just the string and masks token usage 
            # in its simpler API, we record what we can.
            # In a full run, the CrewPerformanceMonitor captures tokens.
            output_text = str(response)
            
            return ProviderResult(
                output=output_text,
                latency_s=round(elapsed, 2),
                tokens_in=0,  # Hidden behind standard .call() abstraction
                tokens_out=0,
                provider_name="amsha_llm",
                tier="amsha_llm"
            )
            
        except Exception as e:
            elapsed = time.time() - start_time
            return ProviderResult(
                output="",
                latency_s=round(elapsed, 2),
                tokens_in=0,
                tokens_out=0,
                provider_name="amsha_llm",
                tier="amsha_llm",
                error=str(e)
            )
