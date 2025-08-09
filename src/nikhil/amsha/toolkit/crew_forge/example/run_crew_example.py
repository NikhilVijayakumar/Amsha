from typing import Optional

import yaml
from pathlib import Path

from nikhil.amsha.toolkit.crew_forge.dependency.container import Container as CrewContainer
from nikhil.amsha.toolkit.crew_forge.domain.models.crew_config_data import CrewConfigResponse
from nikhil.amsha.toolkit.llm_factory.dependency.container import Container as LLMContainer

print("--- Running Integrated Crew Creation Example ---")


crew_container = CrewContainer()
llm_container = LLMContainer()

with open("./config/app_config.yaml", "r") as f:
    app_config = yaml.safe_load(f)
crew_container.config.from_dict(app_config)
print("[Main] Crew Forge container configured.")

# Configure the LLM Factory container
llm_config_path = Path("config/llm_config.yaml")
llm_container.config.llm.yaml_path.from_value(str(llm_config_path))
print("[Main] LLM Factory container configured.")


print("\n[Main] Requesting the LLMBuilder from its container...")
llm_builder = llm_container.llm_builder()

print("[Main] Building the 'creative' LLM...")

actual_llm_data = llm_builder.build_creative()
actual_llm = actual_llm_data.llm  # Extract the llm object from the pydantic model.
print(f"[Main] Successfully built LLM: {actual_llm.model}")


crew_runtime_data = {
    "llm": actual_llm,
    "module_name": "copy",
    "output_dir_path": "output/intermediate"
}


print("\n[Main] Requesting the CrewBuilderService with the real LLM...")
crew_builder = crew_container.crew_builder_service(**crew_runtime_data)

blueprint_service = crew_container.crew_blueprint_service()
config_data:Optional[CrewConfigResponse] = blueprint_service.get_config(name="Copy Crew", usecase="copy")



if not config_data:
    print("[Main] Error: Crew configuration blueprint not found. Exiting.")
    exit()

print(f"[Main] Blueprint for crew '{config_data.name}' loaded successfully.")
agents = config_data.agents
tasks = config_data.tasks
agent_id = agents.get("copywriter_agent")
task_id = tasks.get("ad_copy_task")

print(f"agent_id ={agent_id}\n task_id ={task_id}\n ")

try:
    crew_builder.add_agent(agent_id=agent_id)
    agent =crew_builder.get_last_agent()
    crew_builder.add_task(
        task_id=task_id,
        agent=agent,
        output_filename="ad_copy_results"
    )

    ad_crew = crew_builder.build()

    print("\n[Main] Kicking off the crew...")
    result = ad_crew.kickoff()

    print("\n--- Crew Finished ---")
    print("Result:", result)

except Exception as e:
    print(f"\nAn error occurred: {e}")

finally:
    crew_container.unwire()
    llm_container.unwire()

print("\n--- Integrated Example Finished ---")