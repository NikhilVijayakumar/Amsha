import time
from research.providers.base_provider import BaseProvider, ProviderResult
from amsha.crew_forge.orchestrator.file.amsha_crew_file_application import AmshaCrewFileApplication
from amsha.llm_factory.domain.llm_type import LLMType

class AmshaCrewProvider(BaseProvider):
    """
    Tier 3 implementation: Full Agentic Orchestration via CrewAI.
    Uses AmshaCrewFileApplication to process tasks with full monitoring and JSON sanitization.
    """
    def run(self, prompt: str, model_context: dict, **kwargs) -> ProviderResult:
        # Note: Before calling this, the caller must generate temp_llm_config.yaml
        configs = {
            "llm": "research/temp_llm_config.yaml",
            "app": "research/config/app_config.yaml",
            "job": "research/config/job_config.yaml"
        }
        
        start_time = time.time()
        try:
            # Initialize Pipeline
            app = AmshaCrewFileApplication(config_paths=configs, llm_type=LLMType.CREATIVE)
            
            # Execute Pipeline
            result = app.orchestrator.run_crew(
                crew_name="research_crew", 
                inputs={"dataset_content": prompt}
            )
            
            elapsed = time.time() - start_time
            
            # Extract performance metrics from the monitor
            token_usage = 0
            stats = app.orchestrator.get_last_performance_stats()
            if stats:
                metrics = stats.get_metrics()
                token_usage = metrics.get("general", {}).get("total_tokens", 0)
                
            return ProviderResult(
                output=str(result),
                latency_s=round(elapsed, 2),
                tokens_in=0,  # Monitor only provides total right now
                tokens_out=token_usage, # Logging total here for reference
                provider_name="amsha_crew",
                tier="amsha_crew"
            )
            
        except Exception as e:
            elapsed = time.time() - start_time
            return ProviderResult(
                output="",
                latency_s=round(elapsed, 2),
                tokens_in=0,
                tokens_out=0,
                provider_name="amsha_crew",
                tier="amsha_crew",
                error=str(e)
            )
