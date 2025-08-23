from pathlib import Path

from nikhil.amsha.toolkit.crew_forge.orchestrator.pipeline_orchestrator import PipelineOrchestrator
from nikhil.amsha.toolkit.llm_factory.dependency.llm_container import LLMContainer

if __name__ == "__main__":
    llm_config = "config/llm_config.yaml"
    app_config = "config/app_config.yaml"
    job_config = "config/job_config.yaml"

    llm_container = LLMContainer()
    llm_container.config.llm.yaml_path.from_value(str(Path(llm_config)))
    llm_builder = llm_container.llm_builder()
    llm = llm_builder.build_creative().llm
    # Instantiate the new orchestrator
    orchestrator = PipelineOrchestrator(
        llm=llm,
        app_config_path=app_config,
        job_config_path=job_config
    )

    # Run the full pipeline
    final_results = orchestrator.run_pipeline()
    print("\n--- Final Pipeline Results ---")
    print(final_results)