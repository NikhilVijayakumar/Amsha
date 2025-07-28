# nikhil/amsha/crewai/seeding.py
import os
import logging
from collections import defaultdict

from .repo.agent_repo import AgentRepository
from .repo.task_repo import TaskRepository
from .repo.crew_config_repo import CrewConfigRepository
from .model.crew_config_data import CrewConfigRequest
from ..utils.yaml_utils import YamlUtils

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class DatabaseSeeder:
    """
    Synchronizes Agent, Task, and Crew configurations from YAML files
    in a structured directory into a MongoDB database.
    """

    def __init__(self, agent_repo: AgentRepository, task_repo: TaskRepository, crew_repo: CrewConfigRepository):
        self.agent_repo = agent_repo
        self.task_repo = task_repo
        self.crew_repo = crew_repo
        self.yaml_utils = YamlUtils()

    def synchronize(self, root_path: str):
        """Main entry point for the synchronization process."""
        if not root_path or not os.path.isdir(root_path):
            logging.error(f"The provided path '{root_path}' is not a valid directory.")
            return

        logging.info(f"🚀 Starting database synchronization from path: {root_path}")

        # Phase 1: Collect all configurations from the directory structure.
        usecase_map = self._collect_configs_from_path(root_path)

        # Phase 2: Process each use case.
        if not usecase_map:
            logging.warning("No use cases found to process.")
        else:
            self._process_usecases(usecase_map)

        logging.info("🎉 Database synchronization complete.")

    def _collect_configs_from_path(self, root_path: str) -> dict:
        """Walks the path and collects all agent/task YAML definitions."""
        usecase_map = defaultdict(lambda: {"agents": [], "tasks": []})
        for dirpath, _, filenames in os.walk(root_path):
            norm_dirpath = os.path.normpath(dirpath)
            norm_rootpath = os.path.normpath(root_path)

            if norm_dirpath == norm_rootpath:
                continue

            relative_path = os.path.relpath(norm_dirpath, norm_rootpath)
            usecase = relative_path.split(os.sep)[0]

            for filename in filenames:
                if filename.endswith((".yaml", ".yml")):
                    file_path = os.path.join(dirpath, filename)
                    if os.path.basename(dirpath) == "agents":
                        agent_req = self.yaml_utils.parse_agent(file_path)
                        agent_req.usecase = usecase
                        usecase_map[usecase]["agents"].append(agent_req)
                    elif os.path.basename(dirpath) == "tasks":
                        task_req = self.yaml_utils.parse_task(file_path)
                        task_req.usecase = usecase
                        usecase_map[usecase]["tasks"].append(task_req)
        return usecase_map

    def _process_usecases(self, usecase_map: dict):
        """Synchronizes agents, tasks, and the parent crew for each use case."""
        for usecase, configs in usecase_map.items():
            logging.info(f"--- Processing Usecase: {usecase} ---")

            # Synchronize all agents and collect their IDs
            agent_id_map = self._synchronize_agents(usecase, configs["agents"])

            # Synchronize all tasks and collect their IDs
            task_id_map = self._synchronize_tasks(usecase, configs["tasks"])

            # Synchronize the crew configuration for this use case
            self._synchronize_crew(usecase, agent_id_map, task_id_map)

    def _synchronize_agents(self, usecase: str, agent_requests: list) -> dict:
        """Processes a list of agents for a usecase and returns a name-to-ID map."""
        id_map = {}
        for agent_req in agent_requests:
            try:
                existing_agent = self.agent_repo.find_by_role_and_usecase(agent_req.role, usecase)
                if not existing_agent:
                    created_agent = self.agent_repo.create_agent(agent_req)
                    id_map[created_agent.role] = created_agent.id
                    logging.info(f"  ✅ CREATED Agent '{created_agent.role}'")
                else:
                    if (existing_agent.goal != agent_req.goal or existing_agent.backstory != agent_req.backstory):
                        self.agent_repo.update_agent(existing_agent.id, agent_req)
                        logging.info(f"  🔄 UPDATED Agent '{existing_agent.role}'")
                    else:
                        logging.info(f"  ➖ SKIPPED Agent '{existing_agent.role}' (unchanged).")
                    id_map[existing_agent.role] = existing_agent.id
            except Exception as e:
                logging.error(f"  ❌ FAILED to process agent '{agent_req.role}': {e}")
        return id_map

    def _synchronize_tasks(self, usecase: str, task_requests: list) -> dict:
        """Processes a list of tasks for a usecase and returns a name-to-ID map."""
        id_map = {}
        for task_req in task_requests:
            try:
                existing_task = self.task_repo.find_by_name_and_usecase(task_req.name, usecase)
                if not existing_task:
                    created_task = self.task_repo.create_task(task_req)
                    id_map[created_task.name] = created_task.id
                    logging.info(f"  ✅ CREATED Task '{created_task.name}'")
                else:
                    if (
                            existing_task.description != task_req.description or existing_task.expected_output != task_req.expected_output):
                        self.task_repo.update_task(existing_task.id, task_req)
                        logging.info(f"  🔄 UPDATED Task '{existing_task.name}'")
                    else:
                        logging.info(f"  ➖ SKIPPED Task '{existing_task.name}' (unchanged).")
                    id_map[existing_task.name] = existing_task.id
            except Exception as e:
                logging.error(f"  ❌ FAILED to process task '{task_req.name}': {e}")
        return id_map

    def _synchronize_crew(self, usecase: str, agent_id_map: dict, task_id_map: dict):
        """Creates or updates the crew configuration for a usecase."""
        crew_name = f"{usecase.replace('_', ' ').title()} Crew"
        crew_req = CrewConfigRequest(
            name=crew_name,
            agents=agent_id_map,
            tasks=task_id_map,
            usecase=usecase
        )
        try:
            existing_crew = self.crew_repo.get_crew_by_name_and_usecase(crew_name, usecase)
            if not existing_crew:
                self.crew_repo.create_crew_config(crew_req)
                logging.info(f"  ✅ CREATED Crew '{crew_name}'")
            else:
                if (existing_crew.agents != crew_req.agents or existing_crew.tasks != crew_req.tasks):
                    self.crew_repo.update_crew_config(existing_crew.id, crew_req)
                    logging.info(f"  🔄 UPDATED Crew '{crew_name}'")
                else:
                    logging.info(f"  ➖ SKIPPED Crew '{crew_name}' (unchanged).")
        except Exception as e:
            logging.error(f"  ❌ FAILED to process crew '{crew_name}': {e}")