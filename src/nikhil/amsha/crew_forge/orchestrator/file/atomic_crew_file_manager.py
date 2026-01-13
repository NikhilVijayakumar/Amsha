from typing import Optional, Dict, Any
from crewai import Crew

from amsha.crew_forge.dependency.crew_forge_container import CrewForgeContainer
from amsha.crew_forge.domain.models.crew_data import CrewData
from amsha.crew_forge.service.atomic_yaml_builder import AtomicYamlBuilderService
from amsha.crew_forge.exceptions import (
    CrewManagerException,
    CrewConfigurationException,
    ErrorContext,
    ErrorMessageBuilder,
    wrap_external_exception
)
from amsha.utils.yaml_utils import YamlUtils


from amsha.crew_forge.protocols.crew_manager import CrewManager


class AtomicCrewFileManager(CrewManager):
    """
    File-based implementation of CrewManager Protocol.
    
    Acts as a factory to build specific, atomic crews based on YAML configuration files
    and a job configuration. This implementation conforms to the CrewManager Protocol
    interface for structural typing compatibility.
    """

    def __init__(self, llm, app_config_path: str, job_config: Dict[str, Any], model_name: str,
                 output_config: Optional[Any] = None):
        """
        Initialize the file-based crew manager.
        
        Args:
            llm: LLM instance for crew agents
            app_config_path: Path to application configuration file
            job_config: Job configuration dictionary
            model_name: Name of the LLM model being used
            output_config: Optional output configuration for custom aliasing and folder organization
            
        Raises:
            CrewConfigurationException: If configuration loading fails
        """
        print("🏗️  [FileManager] Initializing file-based crew manager...")
        
        context = ErrorContext("AtomicCrewFileManager", "__init__")
        context.add_context("app_config_path", app_config_path)
        context.add_context("model_name", model_name)
        
        try:
            self.llm = llm
            self.job_config = job_config
            self.crew_container = CrewForgeContainer()
            self._model_name = model_name
            self._output_config = output_config
            self._output_file: Optional[str] = None

            # Load app config for DI with error handling
            app_config = YamlUtils.yaml_safe_load(app_config_path)
            self.app_config = app_config
            self.crew_container.config.from_dict(app_config)
            
            print(f"✅ [FileManager] Initialized successfully with model: {model_name}")
            
        except Exception as e:
            if isinstance(e, (CrewManagerException, CrewConfigurationException)):
                raise
            else:
                raise wrap_external_exception(e, context, CrewManagerException)



    def build_atomic_crew(self, crew_name: str, filename_suffix: Optional[str] = None,
                          output_json: Any = None) -> Crew:
        """
        Build a configured crew ready for execution.
        
        This method creates a complete CrewAI Crew instance from the
        specified YAML configuration files, including all agents, tasks, and
        knowledge sources.
        
        Args:
            crew_name: Name of the crew configuration to build
            filename_suffix: Optional suffix for output filenames
            output_json: Any
            
        Returns:
            Configured CrewAI Crew instance ready for execution
            
        Raises:
            CrewManagerException: If crew building fails
            CrewConfigurationException: If crew configuration is invalid
        """
        print(f"🔨 [FileManager] Building atomic crew: '{crew_name}'...")
        
        context = ErrorContext("AtomicCrewFileManager", "build_atomic_crew")
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

            crew_builder: Optional[AtomicYamlBuilderService] = None
            
            # Process each step in the crew definition
            for step_index, step in enumerate(crew_def['steps']):
                context.add_context("step_index", step_index)
                
                task_file = step.get('task_file')
                agent_file = step.get('agent_file')

                if not task_file:
                    raise CrewConfigurationException(
                        message=ErrorMessageBuilder.configuration_error(
                            crew_name, 
                            f"task_file missing in step {step_index}"
                        ),
                        crew_name=crew_name,
                        config_details=f"step {step_index} missing 'task_file'"
                    )

                if not agent_file:
                    raise CrewConfigurationException(
                        message=ErrorMessageBuilder.configuration_error(
                            crew_name, 
                            f"agent_file missing in step {step_index}"
                        ),
                        crew_name=crew_name,
                        config_details=f"step {step_index} missing 'agent_file'"
                    )

                # Create crew builder for this step
                crew_builder = self.crew_container.atomic_yaml_builder(
                    data=crew_data,
                    task_yaml_file=task_file,
                    agent_yaml_file=agent_file
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
                crew_builder.add_agent(knowledge_sources=agent_text_source)
                
                # Determine output filename - use alias from output_config if available
                base_name = self._model_name
                if self._output_config and hasattr(self._output_config, 'alias') and self._output_config.alias:
                    base_name = self._output_config.alias
                
                if filename_suffix:
                    output_filename = f"{base_name}_{filename_suffix}"
                else:
                    output_filename = base_name
                
                # Add task to crew
                crew_builder.add_task(
                    agent=crew_builder.get_last_agent(),
                    output_filename=output_filename,
                    output_json=output_json
                )

            # Store output file reference
            if crew_builder:
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

            print(f"✅ [FileManager] Finished building '{crew_name}'.")
            
            if not crew_builder:
                raise CrewManagerException(
                    message=ErrorMessageBuilder.manager_error(
                        "FileManager", 
                        "build_atomic_crew", 
                        "no steps processed, crew builder not initialized"
                    ),
                    manager_type="FileManager",
                    operation="build_atomic_crew"
                )
            
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






