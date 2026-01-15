import json
from pathlib import Path
from typing import Dict, Any, Optional, List


from amsha.crew_forge.orchestrator.file.atomic_crew_file_manager import AtomicCrewFileManager
from amsha.crew_forge.orchestrator.file.file_crew_orchestrator import FileCrewOrchestrator
from amsha.crew_forge.protocols.crew_application import CrewApplication
from amsha.crew_forge.service.shared_llm_initialization_service import SharedLLMInitializationService
from amsha.execution_runtime.domain import ExecutionMode
from amsha.execution_state.domain import ExecutionStatus
from amsha.execution_state.service import StateManager
from amsha.llm_factory.domain.model.llm_type import LLMType
from amsha.llm_factory.domain.model.llm_model_config import LLMModelConfig
from amsha.llm_factory.domain.model.llm_parameters import LLMParameters
from amsha.output_process.optimization.json_cleaner_utils import JsonCleanerUtils
from amsha.utils.yaml_utils import YamlUtils
from amsha.common.logger import get_logger


class AmshaCrewFileApplication(CrewApplication):
    """
    A reusable base class that handles all the boilerplate setup for running a crew.

    """

    def __init__(self, config_paths: Dict[str, str], llm_type: LLMType, inputs: Optional[List[Dict[str, Any]]] = None, llm_config_override: Optional[Dict] = None):
        """
        Initializes the application with necessary configuration paths.

        Args:
            config_paths: A dictionary containing paths to config files.
            llm_type: Type of LLM to initialize (CREATIVE or EVALUATION)
            inputs: Optional external inputs
            llm_config_override: Optional dictionary containing LLM configuration overrides
        """
        self.logger = get_logger("crew_forge.application")
        self.llm_type = llm_type
        self.config_paths = config_paths
        self.job_config = YamlUtils.yaml_safe_load(config_paths["job"])
        
        # Prepare overrides if provided
        model_config = None
        llm_params = None
        
        if llm_config_override:
            self.logger.info("Using LLM configuration overrides", extra={
                "has_model_config": 'model_config' in llm_config_override,
                "has_llm_parameters": 'llm_parameters' in llm_config_override
            })
            if 'model_config' in llm_config_override:
                model_config = LLMModelConfig(**llm_config_override['model_config'])
            if 'llm_parameters' in llm_config_override:
                llm_params = LLMParameters(**llm_config_override['llm_parameters'])

        # Initialize LLM using shared service
        llm, model_name, output_config = SharedLLMInitializationService.initialize_llm(
            config_paths["llm"], 
            llm_type,
            model_config=model_config,
            llm_params=llm_params
        )
        self.model_name = model_name
        self.output_config = output_config
        
        self.external_inputs = inputs
        

        self.state_manager = StateManager()
        
        manager = AtomicCrewFileManager(
            llm=llm,
            model_name=self.model_name,
            output_config=output_config,
            app_config_path=config_paths["app"],
            job_config=self.job_config
        )
        self.orchestrator = FileCrewOrchestrator(
            manager=manager,
            state_manager=self.state_manager
        )

    def _process_input_item(self, input_item: Dict[str, Any]) -> Any:
        """Standalone logic to transform an input definition into actual data."""
        key_name = input_item.get("key_name")
        source = input_item.get("source")

        if source == "file":
            file_path = Path(input_item["path"])
            file_format = input_item.get("format", "text")

            if file_format == "json":
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:  # Plain text
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()

        elif source == "direct":
            return input_item.get("value")

        return None

    def _handle_external_overrides(self, key_name: str) -> Optional[Any]:
        """
        Checks if the client provided an override for a specific key.
        Returns the processed data if found, otherwise None.
        """
        if not self.external_inputs:
            return None

        # Find the specific override in the list provided by the client
        override_item = next(
            (item for item in self.external_inputs if item.get("key_name") == key_name),
            None
        )

        if override_item:
            self.logger.debug("Handling external input override", extra={
                "key_name": key_name
            })
            return self._process_input_item(override_item)

        return None


    def _prepare_multiple_inputs_for(self, crew_name: str) -> dict:
        """
        Prepares the inputs dictionary for a specific crew by resolving values
        from a list of sources in the job config.
        """
        crew_def = self.job_config["crews"][crew_name]
        # Expect a list of inputs, defaulting to an empty list
        inputs_def = crew_def.get("input", [])
        final_inputs = {}

        self.logger.info("Preparing crew inputs", extra={
            "crew_name": crew_name,
            "num_inputs": len(inputs_def),
            "has_external_overrides": bool(self.external_inputs)
        })

        # Loop through each input definition in the list
        for input_item in inputs_def:
            key_name = input_item["key_name"]

            # STEP 1: Try External Handler (The new separate method)
            external_data = self._handle_external_overrides(key_name)

            if external_data is not None:
                final_inputs[key_name] = external_data
                self.logger.debug("Using external input", extra={
                    "key_name": key_name,
                    "source": input_item.get("source"),
                    "is_file": input_item.get("source") == "file",
                    "file_path": input_item.get("path") if input_item.get("source") == "file" else None
                })
            else:
                # STEP 2: Fallback to existing YAML logic via the common processor
                self.logger.debug("Loading input from YAML config", extra={
                    "key_name": key_name,
                    "source": input_item.get("source"),
                    "file_path": input_item.get("path") if input_item.get("source") == "file" else None
                })
                final_inputs[key_name] = self._process_input_item(input_item)

        self.logger.debug("Inputs prepared", extra={
            "crew_name": crew_name,
            "input_keys": list(final_inputs.keys())
        })
        return final_inputs


    def _prepare_inputs_for(self, crew_name: str) -> dict:
        """
        Prepares the inputs dictionary for a specific crew by resolving values
        from the job config.
        """
        crew_def = self.job_config["crews"][crew_name]
        inputs_def = crew_def.get("input", {})  # Get the inputs dictionary
        final_inputs = {}

        self.logger.info("Preparing crew inputs", extra={
            "crew_name": crew_name,
            "num_placeholders": len(inputs_def)
        })

        # Loop through each placeholder and its defined value
        for placeholder, value_def in inputs_def.items():

            # Case 1: The value is a dictionary defining a file source
            if isinstance(value_def, dict) and value_def.get("source") == "file":
                file_path = Path(value_def["path"])
                file_format = value_def.get("format", "text")
                self.logger.debug("Loading input from file", extra={
                    "placeholder": placeholder,
                    "file_path": str(file_path)
                })

                if file_format == "json":
                    with open(file_path, 'r', encoding='utf-8') as f:
                        final_inputs = json.load(f)
                else:  # Plain text
                    with open(file_path, 'r', encoding='utf-8') as f:
                        final_inputs = f.read()

            # Case 2: The value is provided directly (e.g., a string)
            else:
                self.logger.debug("Loading input from config", extra={
                    "placeholder": placeholder
                })
                final_inputs = value_def


        return final_inputs




    def execute_crew_with_retry(
        self, 
        crew_name: str, 
        inputs: Dict[str, Any], 
        max_retries: int = 0,
        filename_suffix: Optional[str] = None,
            output_folder: Optional[str] = None,
            output_json: Any = None
    ) -> Any:
        """
        Executes a crew with retry logic managed by the application.
        
        Args:
            crew_name: Name of the crew to run.
            inputs: Input dictionary for the crew.
            max_retries: Maximum number of retries allowed.
            filename_suffix: Optional suffix for output files.
            output_folder: optional output folder to group different generated output
            output_json: Pydantic Json
            
        Returns:
            The result of the successful execution, or the last result if all retries fail.
        """


        attempt = 0
        success = False
        last_result = None
        
        # Total attempts = initial run (1) + retries
        while attempt <= max_retries:
            attempt += 1
            self.logger.info("Crew execution attempt", extra={
                "crew_name": crew_name,
                "attempt": attempt,
                "max_attempts": max_retries + 1
            })
            
            current_suffix = filename_suffix
            if attempt > 1:
                base_suffix = filename_suffix or crew_name
                current_suffix = f"{base_suffix}_retry_{attempt}"
            
            # Run the crew
            last_result = self.orchestrator.run_crew(
                crew_name=crew_name,
                inputs=inputs,
                filename_suffix=current_suffix,
                output_json=output_json,
                mode=ExecutionMode.INTERACTIVE
            )
            
            # Get output file for validation
            output_file = self.orchestrator.get_last_output_file()
            
            # Validate
            if self.validate_execution(last_result, output_file,output_folder):
                self.logger.info("Crew validation successful", extra={
                    "crew_name": crew_name,
                    "attempt": attempt,
                    "output_file": output_file,
                    "model_name": self.model_name,
                    "llm_type": self.llm_type.value
                })
                success = True
                break
            
            self.logger.warning("Crew validation failed", extra={
                "crew_name": crew_name,
                "attempt": attempt
            })
            
            # Update State on failure
            execution_id = self.orchestrator.get_last_execution_id()
            if execution_id:
                self.logger.debug("Updating execution state to FAILED", extra={
                    "execution_id": execution_id,
                    "attempt": attempt
                })
                self.state_manager.update_status(
                    execution_id, 
                    ExecutionStatus.FAILED, 
                    metadata={"reason": "Validation failed", "attempt": attempt}
                )
            
            if attempt > max_retries:
                self.logger.error("Max retries reached, execution failed", extra={
                    "crew_name": crew_name,
                    "attempts": attempt
                })
        
        return last_result

    def validate_execution(self, result: Any, output_file: Optional[str],output_folder: Optional[str] = None) -> bool:
        """
        Hook for subclasses to implement custom validation logic.
        
        Args:
            result: The result object returned by the crew execution.
            output_file: The path to the output file generated, if any.
            output_folder: optional output folder to group different generated output
            
        Returns:
            True if execution is considered successful, False otherwise.
        """
        class_name = self.__class__.__name__
        valid = False
        if output_file:
            self.logger.info("Output file generated", extra={
                "class_name": class_name,
                "output_file": output_file,
                "model_name": self.model_name,
                "model_alias": self.output_config.alias if self.output_config else None
            })
            valid=self.clean_json(output_filename=output_file, output_folder=output_folder)
        return valid


    def clean_json(self, output_filename: str, max_llm_retries: int = 2,output_folder: Optional[str] = None) -> bool:
        """
        Cleans and validates a JSON file, using an LLM for fixes with a retry limit.

        Args:
            output_filename: The path to the JSON file to be cleaned.
            max_llm_retries: The maximum number of times to call the LLM to fix the file.
            output_folder: optional output folder to group different generated output

        Returns:
            The true or false.
        """
        print(f"AmshaCrewForgeApplication:{output_filename}")
        current_file = Path(output_filename)
        cleaner = JsonCleanerUtils(input_file_path=output_filename,output_folder=output_folder)
        if cleaner.process_file():
            print(f"✅ JSON validated successfully. Clean file at: {cleaner.output_file_path}")
            return True
        return False





