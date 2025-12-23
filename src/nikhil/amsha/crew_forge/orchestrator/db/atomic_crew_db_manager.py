from typing import Optional, Dict, Any
from crewai import Crew

from amsha.crew_forge.dependency.crew_forge_container import CrewForgeContainer
from amsha.crew_forge.domain.models.crew_config_data import CrewConfigResponse
from amsha.crew_forge.domain.models.crew_data import CrewData
from amsha.crew_forge.service.atomic_db_builder import AtomicDbBuilderService
from amsha.crew_forge.exceptions import (
    CrewManagerException,
    CrewConfigurationException,
    ErrorContext,
    ErrorMessageBuilder,
    wrap_external_exception
)
from amsha.utils.yaml_utils import YamlUtils


from amsha.crew_forge.protocols.crew_manager import CrewManager


class AtomicCrewDBManager(CrewManager):
    """
    Database-based implementation of CrewManager Protocol.
    
    Acts as a factory to build specific, atomic crews based on database-stored
    configurations and a job configuration. This implementation conforms to the
    CrewManager Protocol interface for structural typing compatibility.
    """

    def __init__(self, llm, app_config_path: str, job_config: Dict[str, Any], model_name: str):
        """
        Initialize the database-based crew manager.
        
        Args:
            llm: LLM instance for crew agents
            app_config_path: Path to application configuration file
            job_config: Job configuration dictionary
            model_name: Name of the LLM model being used
            
        Raises:
            CrewConfigurationException: If configuration loading fails
            CrewManagerException: If database initialization fails
        """
        print("🏗️  [DBManager] Initializing database-based crew manager...")
        
        context = ErrorContext("AtomicCrewDBManager", "__init__")
        context.add_context("app_config_path", app_config_path)
        context.add_context("model_name", model_name)
        
        try:
            self.llm = llm
            self.job_config = job_config
            self.crew_container = CrewForgeContainer()
            self._model_name = model_name
            self._output_file: Optional[str] = None

            # Load app config for DI with error handling
            app_config = YamlUtils.yaml_safe_load(app_config_path)
            self.app_config = app_config
            self.crew_container.config.from_dict(app_config)

            # Fetch the single master blueprint using top-level keys from job_config
            self.blueprint_service = self.crew_container.crew_blueprint_service()
            
            crew_name_key = self.job_config.get("crew_name")
            usecase_key = self.job_config.get("usecase")
            
            if not crew_name_key:
                raise CrewConfigurationException(
                    message=ErrorMessageBuilder.configuration_error(
                        "job_config", 
                        "missing required 'crew_name' key"
                    ),
                    config_details="job_config must contain 'crew_name' key"
                )
            
            if not usecase_key:
                raise CrewConfigurationException(
                    message=ErrorMessageBuilder.configuration_error(
                        "job_config", 
                        "missing required 'usecase' key"
                    ),
                    config_details="job_config must contain 'usecase' key"
                )
            
            context.add_context("crew_name_key", crew_name_key)
            context.add_context("usecase_key", usecase_key)
            
            self.master_blueprint: Optional[CrewConfigResponse] = self.blueprint_service.get_config(
                name=crew_name_key,
                usecase=usecase_key
            )

            if not self.master_blueprint:
                raise CrewConfigurationException(
                    message=ErrorMessageBuilder.configuration_error(
                        crew_name_key, 
                        "master blueprint not found in database",
                        f"usecase: {usecase_key}"
                    ),
                    crew_name=crew_name_key,
                    config_details=f"No blueprint found for name='{crew_name_key}', usecase='{usecase_key}'"
                )
            
            print(f"✅ [DBManager] Initialized successfully with model: {model_name}")
            print(f"  -> Master blueprint loaded: {crew_name_key} (usecase: {usecase_key})")
            
        except Exception as e:
            if isinstance(e, (CrewManagerException, CrewConfigurationException)):
                raise
            else:
                raise wrap_external_exception(e, context, CrewManagerException)

    def build_atomic_crew(self, crew_name: str, filename_suffix: Optional[str] = None) -> Crew:
        """
        Build a configured crew ready for execution.
        
        This method creates a complete CrewAI Crew instance from the
        specified database configuration, including all agents, tasks, and
        knowledge sources.
        
        Args:
            crew_name: Name of the crew configuration to build
            filename_suffix: Optional suffix for output filenames
            
        Returns:
            Configured CrewAI Crew instance ready for execution
            
        Raises:
            CrewManagerException: If crew building fails
            CrewConfigurationException: If crew configuration is invalid
        """
        print(f"🔨 [DBManager] Building atomic crew: '{crew_name}'...")
        
        context = ErrorContext("AtomicCrewDBManager", "build_atomic_crew")
        context.add_context("crew_name", crew_name)
        context.add_context("filename_suffix", filename_suffix)
        
        try:
            # Validate crew definition exists
            crew_def = self.job_config["crews"].get(crew_name)
            if not crew_def:
                raise CrewConfigurationException(
                    message=ErrorMessageBuilder.configuration_error(
                        crew_name, 
                        "crew definition not found in job configuration"
                    ),
                    crew_name=crew_name,
                    config_details="crew not found in 'crews' section"
                )

            # Set up crew data for building
            crew_data = CrewData(
                llm=self.llm,
                module_name=self.job_config.get("module_name", ""),
                output_dir_path=self.app_config.get("output_dir_path", f"output/{crew_name}")
            )

            # Create crew builder
            crew_builder: AtomicDbBuilderService = self.crew_container.atomic_db_builder(data=crew_data)

            # Process each step in the crew definition
            for step_index, step in enumerate(crew_def['steps']):
                context.add_context("step_index", step_index)
                
                task_key = step.get('task_key')
                agent_key = step.get('agent_key')

                if not task_key:
                    raise CrewConfigurationException(
                        message=ErrorMessageBuilder.configuration_error(
                            crew_name, 
                            f"task_key missing in step {step_index}"
                        ),
                        crew_name=crew_name,
                        config_details=f"step {step_index} missing 'task_key'"
                    )

                if not agent_key:
                    raise CrewConfigurationException(
                        message=ErrorMessageBuilder.configuration_error(
                            crew_name, 
                            f"agent_key missing in step {step_index}"
                        ),
                        crew_name=crew_name,
                        config_details=f"step {step_index} missing 'agent_key'"
                    )

                # Look up task and agent IDs from master blueprint
                task_id = self.master_blueprint.tasks.get(task_key)
                if not task_id:
                    raise CrewConfigurationException(
                        message=ErrorMessageBuilder.configuration_error(
                            crew_name, 
                            f"task_key '{task_key}' not found in master blueprint"
                        ),
                        crew_name=crew_name,
                        config_details=f"task_key '{task_key}' not in blueprint.tasks"
                    )

                agent_id = self.master_blueprint.agents.get(agent_key)
                if not agent_id:
                    raise CrewConfigurationException(
                        message=ErrorMessageBuilder.configuration_error(
                            crew_name, 
                            f"agent_key '{agent_key}' not found in master blueprint"
                        ),
                        crew_name=crew_name,
                        config_details=f"agent_key '{agent_key}' not in blueprint.agents"
                    )

                # Handle agent knowledge sources
                agent_knowledge_paths = set()
                for path in step.get('knowledge_sources', []):
                    print(f"  -> Adding agent knowledge source: {path}")
                    agent_knowledge_paths.add(path)
                
                agent_text_source = None
                if agent_knowledge_paths:
                    from amsha.crew_forge.knowledge.amsha_crew_docling_source import AmshaCrewDoclingSource
                    agent_text_source = AmshaCrewDoclingSource(
                        file_paths=list(agent_knowledge_paths)
                    )
                
                # Add agent to crew
                crew_builder.add_agent(
                    agent_id=agent_id,
                    knowledge_sources=agent_text_source
                )
                
                # Determine output filename
                if filename_suffix:
                    output_filename = f"{self._model_name}_{task_key}_{filename_suffix}"
                else:
                    output_filename = f"{self._model_name}_{task_key}"
                
                # Add task to crew
                crew_builder.add_task(
                    task_id=task_id,
                    agent=crew_builder.get_last_agent(),
                    output_filename=output_filename
                )

            # Store output file reference
            self._output_file = crew_builder.get_last_file()

            # Handle crew-level knowledge sources
            crew_knowledge_paths = set()
            for path in crew_def.get('knowledge_sources', []):
                print(f"  -> Adding crew knowledge source: {path}")
                crew_knowledge_paths.add(path)
            
            crew_text_source = None
            if crew_knowledge_paths:
                from amsha.crew_forge.knowledge.amsha_crew_docling_source import AmshaCrewDoclingSource
                crew_text_source = AmshaCrewDoclingSource(
                    file_paths=list(crew_knowledge_paths)
                )

            print(f"✅ [DBManager] Finished building '{crew_name}'.")
            return crew_builder.build(knowledge_sources=crew_text_source)
            
        except (CrewManagerException, CrewConfigurationException):
            # Re-raise crew_forge exceptions as-is
            raise
        except Exception as e:
            # Wrap any other unexpected exceptions
            raise wrap_external_exception(e, context, CrewManagerException)

    @property
    def model_name(self) -> str:
        """
        Get the model name used by this manager.
        
        Returns:
            String identifier of the LLM model being used
        """
        return self._model_name
    
    @property
    def output_file(self) -> Optional[str]:
        """
        Get the current output file path.
        
        Returns:
            Path to the current output file, or None if no file is set
        """
        return self._output_file






