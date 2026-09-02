# src/nikhil/amsha/toolkit/crew_forge/service/atomic_yaml_builder.py
from pathlib import Path
from typing import Optional, Any

from crewai import Crew, Agent, Process

from amsha.crew_forge.domain.models.crew_data import CrewData
from amsha.crew_forge.seeding.parser.crew_parser import CrewParser
from amsha.crew_forge.service.crew_builder_service import CrewBuilderService


class AtomicYamlBuilderService:

    def __init__(self,data: CrewData,parser:CrewParser,agent_yaml_file:str,task_yaml_file:str,
                 skills_root: Optional[str] = None):
        self.parser:CrewParser = parser
        self.agent_yaml_file:str =agent_yaml_file
        self.task_yaml_file:str = task_yaml_file
        self.skills_root: Optional[str] = skills_root
        self.builder:CrewBuilderService = CrewBuilderService(data)

    def add_agent(self,knowledge_sources=None, tools: list = None):
        agent_details = self.parser.parse_agent(self.agent_yaml_file)
        if not agent_details:
            raise ValueError(f"Agent file: '{self.agent_yaml_file}' not found.")
        agent_details.skills = self._resolve_skills(agent_details.skills)
        self.builder.add_agent(agent_details, knowledge_sources, tools)

    def _resolve_skills(self, skills: Optional[list]) -> Optional[list]:
        """Resolve skill names from an agent's YAML to crewai skill search paths.

        Each entry that is not already an existing path is resolved as a
        subdirectory of ``skills_root`` (``<skills_root>/<name>``). A crewai
        skill search path is a directory whose subdirectories each contain a
        ``SKILL.md``.
        """
        if not skills or not self.skills_root:
            return skills
        resolved = []
        for name in skills:
            entry = Path(name)
            if entry.exists():
                resolved.append(str(entry))
                continue
            candidate = Path(self.skills_root) / name
            if not candidate.is_dir():
                raise ValueError(
                    f"Skill '{name}' not found. Expected a directory at '{candidate}' "
                    "containing skill subdirectories, each with a SKILL.md."
                )
            resolved.append(str(candidate))
        return resolved

    def add_task(self, agent: Agent, output_filename: str = None,
                 validation:bool=False,output_json: Any = None):
        task_details = self.parser.parse_task(self.task_yaml_file)
        if not task_details:
            raise ValueError(f"Task file: '{self.task_yaml_file}' not found.")
        self.builder.add_task(task_details, agent, output_filename, validation,output_json)

    def build(self, process: Process = Process.sequential, knowledge_sources=None) -> Crew:
        return self.builder.build(process, knowledge_sources)

    def get_last_agent(self) -> Optional[Agent]:
        return self.builder.get_last_agent()

    def get_last_file(self) -> Optional[str]:
        return self.builder.get_last_file()
