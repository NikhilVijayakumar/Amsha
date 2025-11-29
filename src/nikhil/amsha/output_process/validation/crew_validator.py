import os
import json
import logging
from collections import defaultdict
from datetime import datetime

from amsha.crew_forge.seeding.parser.crew_parser import CrewParser

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class CrewConfigValidator:

    def __init__(self):
        # In a real scenario, you would use your actual parser.
        # self.crew_parser = CrewParser()
        self.crew_parser = CrewParser()  # Using a mock for this runnable example

    def validate(self, root_path: str, output_dir_path: str = None) -> dict:

        report = {"summary": {}, "details": {}}
        if not root_path or not os.path.isdir(root_path):
            logging.error(f"The provided path '{root_path}' is not a valid directory.")
            report["summary"]["error"] = f"Invalid root path: {root_path}"
            return report

        logging.info(f"🚀 Starting configuration validation for path: {root_path}")
        usecase_files = self._collect_files_to_validate(root_path)

        if not usecase_files:
            logging.warning("No use cases or config files found to validate.")
            return report

        report["details"] = self._process_and_validate_files(usecase_files)
        report["summary"] = self._generate_summary(report["details"])

        logging.info("🎉 Validation complete.")

        # --- NEW: Save the report to a file if an output path is provided ---
        if output_dir_path:
            self._save_report_to_file(report, output_dir_path)

        return report

    def _save_report_to_file(self, report: dict, output_dir_path: str):
        try:
            # Ensure the output directory exists
            os.makedirs(output_dir_path, exist_ok=True)

            # Create a timestamped filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = f"validation_report_{timestamp}.json"
            file_path = os.path.join(output_dir_path, file_name)

            # Write the JSON report
            with open(file_path, 'w') as f:
                json.dump(report, f, indent=2)

            logging.info(f"✅ Successfully saved validation report to: {file_path}")

        except Exception as e:
            logging.error(f"❌ FAILED to save validation report to directory '{output_dir_path}': {e}")

    def _collect_files_to_validate(self, root_path: str) -> dict:
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
                        usecase_map[usecase]["agents"].append(file_path)
                    elif os.path.basename(dirpath) == "tasks":
                        usecase_map[usecase]["tasks"].append(file_path)
        return usecase_map

    def _process_and_validate_files(self, usecase_files: dict) -> dict:
        details = {}
        for usecase, files in usecase_files.items():
            details[usecase] = {"agents": [], "tasks": []}
            for agent_file in files["agents"]:
                try:
                    self.crew_parser.parse_agent(agent_file)
                    details[usecase]["agents"].append({"file_path": agent_file, "status": "VALID"})
                except Exception as e:
                    details[usecase]["agents"].append(
                        {"file_path": agent_file, "status": "INVALID", "reason": f"{type(e).__name__}: {e}"})
            for task_file in files["tasks"]:
                try:
                    self.crew_parser.parse_task(task_file)
                    details[usecase]["tasks"].append({"file_path": task_file, "status": "VALID"})
                except Exception as e:
                    details[usecase]["tasks"].append(
                        {"file_path": task_file, "status": "INVALID", "reason": f"{type(e).__name__}: {e}"})
        return details

    @staticmethod
    def _generate_summary(report_details: dict) -> dict:
        total_files, valid_files, invalid_files = 0, 0, 0
        all_agents_valid, all_tasks_valid = True, True

        for data in report_details.values():
            for agent_result in data.get("agents", []):
                total_files += 1
                if agent_result["status"] == "INVALID":
                    invalid_files += 1
                    all_agents_valid = False
            for task_result in data.get("tasks", []):
                total_files += 1
                if task_result["status"] == "INVALID":
                    invalid_files += 1
                    all_tasks_valid = False

        valid_files = total_files - invalid_files

        return {
            "all_agents_valid": all_agents_valid,
            "all_tasks_valid": all_tasks_valid,
            "total_files_checked": total_files,
            "valid_files": valid_files,
            "invalid_files": invalid_files
        }