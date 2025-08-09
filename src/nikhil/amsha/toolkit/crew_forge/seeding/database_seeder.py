# src/nikhil/amsha/toolkit/crew_forge/seeding/database_seeder.py
import logging
import os
from collections import defaultdict

from nikhil.amsha.toolkit.crew_forge.domain.models.crew_config_data import CrewConfigRequest
from nikhil.amsha.toolkit.crew_forge.repo.interfaces.i_agent_repository import IAgentRepository
from nikhil.amsha.toolkit.crew_forge.repo.interfaces.i_crew_config_repository import ICrewConfigRepository
from nikhil.amsha.toolkit.crew_forge.repo.interfaces.i_task_repository import ITaskRepository
from nikhil.amsha.toolkit.crew_forge.seeding.parser.crew_parser import CrewParser

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class DatabaseSeeder:

    def __init__(self, agent_repo: IAgentRepository, task_repo: ITaskRepository, crew_repo: ICrewConfigRepository):
        self.agent_repo = agent_repo
        self.task_repo = task_repo
        self.crew_repo = crew_repo
        self.crew_parser = CrewParser()

    def synchronize(self, root_path: str):
        if not root_path or not os.path.isdir(root_path):
            logging.error(f"The provided path '{root_path}' is not a valid directory.")
            return

        logging.info(f"🚀 Starting database synchronization from path: {root_path}")
        usecase_map = self._collect_configs_from_path(root_path)

        if not usecase_map:
            logging.warning("No use cases found to process.")
        else:
            self._process_usecases(usecase_map)

        logging.info("🎉 Database synchronization complete.")

    def _collect_configs_from_path(self, root_path: str) -> dict:
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
                    key = os.path.splitext(filename)[0]
                    file_path = os.path.join(dirpath, filename)

                    if os.path.basename(dirpath) == "agents":
                        agent_req = self.crew_parser.parse_agent(file_path)
                        agent_req.usecase = usecase
                        usecase_map[usecase]["agents"].append({"key": key, "data": agent_req})
                    elif os.path.basename(dirpath) == "tasks":
                        task_req = self.crew_parser.parse_task(file_path)
                        task_req.usecase = usecase
                        usecase_map[usecase]["tasks"].append({"key": key, "data": task_req})
        return usecase_map

    def _process_usecases(self, usecase_map: dict):
        for usecase, configs in usecase_map.items():
            logging.info(f"--- Processing Usecase: {usecase} ---")
            agent_id_map = self._synchronize_agents(usecase, configs["agents"])
            task_id_map = self._synchronize_tasks(usecase, configs["tasks"])
            self._synchronize_crew(usecase, agent_id_map, task_id_map)

    def _synchronize_agents(self, usecase: str, agent_configs: list) -> dict:
        id_map = {}
        for config in agent_configs:
            agent_key = config["key"]
            agent_req = config["data"]
            try:
                existing_agent = self.agent_repo.find_by_role_and_usecase(agent_req.role, usecase)
                if not existing_agent:
                    created_agent = self.agent_repo.create_agent(agent_req)
                    # 👇 **CHANGE**: Use the filename-key for the map
                    id_map[agent_key] = str(created_agent.id)
                    logging.info(f"  ✅ CREATED Agent '{agent_req.role}'")
                else:
                    if existing_agent.goal != agent_req.goal or existing_agent.backstory != agent_req.backstory:
                        self.agent_repo.update_agent(existing_agent.id, agent_req)
                        logging.info(f"  🔄 UPDATED Agent '{agent_req.role}'")
                    else:
                        logging.info(f"  ➖ SKIPPED Agent '{agent_req.role}' (unchanged).")
                    # 👇 **CHANGE**: Use the filename-key for the map
                    id_map[agent_key] = str(existing_agent.id)
            except Exception as e:
                logging.error(f"  ❌ FAILED to process agent '{agent_req.role}': {e}")
        return id_map

    def _synchronize_tasks(self, usecase: str, task_configs: list) -> dict:
        id_map = {}
        for config in task_configs:
            task_key = config["key"]
            task_req = config["data"]
            try:
                existing_task = self.task_repo.find_by_name_and_usecase(task_req.name, usecase)
                if not existing_task:
                    created_task = self.task_repo.create_task(task_req)
                    # 👇 **CHANGE**: Use the filename-key for the map
                    id_map[task_key] = str(created_task.id)
                    logging.info(f"  ✅ CREATED Task '{task_req.name}'")
                else:
                    if (
                            existing_task.description != task_req.description or existing_task.expected_output != task_req.expected_output):
                        self.task_repo.update_task(existing_task.id, task_req)
                        logging.info(f"  🔄 UPDATED Task '{task_req.name}'")
                    else:
                        logging.info(f"  ➖ SKIPPED Task '{task_req.name}' (unchanged).")
                    # 👇 **CHANGE**: Use the filename-key for the map
                    id_map[task_key] = str(existing_task.id)
            except Exception as e:
                logging.error(f"  ❌ FAILED to process task '{task_req.name}': {e}")
        return id_map

    def _synchronize_crew(self, usecase: str, agent_id_map: dict, task_id_map: dict):
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
                if existing_crew.agents != crew_req.agents or existing_crew.tasks != crew_req.tasks:
                    self.crew_repo.update_crew_config(existing_crew.id, crew_req)
                    logging.info(f"  🔄 UPDATED Crew '{crew_name}'")
                else:
                    logging.info(f"  ➖ SKIPPED Crew '{crew_name}' (unchanged).")
        except Exception as e:
            logging.error(f"  ❌ FAILED to process crew '{crew_name}': {e}")
