import json
from pathlib import Path
from typing import Dict, Any, Optional, List

from ... import CrewApplication
from ...orchestrator.file.atomic_crew_file_manager import AtomicCrewFileManager
from ...orchestrator.file.file_crew_orchestrator import FileCrewOrchestrator
from ....execution_runtime.domain import ExecutionMode
from ....execution_state.domain import ExecutionStatus
from ....execution_state.service import StateManager
from ....llm_factory.dependency.llm_container import LLMContainer
from ....llm_factory.domain.model.llm_type import LLMType
from ....output_process.optimization.json_cleaner_utils import JsonCleanerUtils
from ....utils.yaml_utils import YamlUtils


class AmshaCrewFileApplication(CrewApplication):
    """
    A reusable base class that handles all the boilerplate setup for running a crew.

    """

    def __init__(self, config_paths: Dict[str, str],llm_type:LLMType,inputs: Optional[List[Dict[str, Any]]] = None):
        """
        Initializes the application with necessary configuration paths.

        Args:
            config_paths: A dictionary containing paths to config files.
        """
        self.llm_type = llm_type
        self.config_paths = config_paths
        self.job_config = YamlUtils.yaml_safe_load(config_paths["job"])
        self.model_name:Optional[str] = None
        llm = self._initialize_llm()
        self.external_inputs = inputs
        

        self.state_manager = StateManager()
        
        manager = AtomicCrewFileManager(
            llm=llm,
            model_name = self.model_name,
            app_config_path=config_paths["app"],
            job_config=self.job_config
        )
        self.orchestrator = FileCrewOrchestrator(
            manager=manager,
            state_manager=self.state_manager
        )


    def _initialize_llm(self) -> Any:
        """Sets up the DI container for the LLM and builds the instance."""
        print("⚙️  Setting up LLM...")
        llm_container = LLMContainer()
        llm_container.config.llm.yaml_path.from_value(
            str(Path(self.config_paths["llm"]))
        )
        llm_builder = llm_container.llm_builder()
        if self.llm_type == LLMType.CREATIVE:
            build_llm = llm_builder.build_creative()
        else:
            build_llm = llm_builder.build_evaluation()
        provider = build_llm.provider
        self.model_name = provider.model_name
        return provider.get_raw_llm()

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
            print(f"  -> 🚀 Handling External Override for: {key_name}")
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

        print(f"📦 [App] Preparing inputs for '{crew_name}'...")

        # Loop through each input definition in the list
        for input_item in inputs_def:
            key_name = input_item["key_name"]

            # STEP 1: Try External Handler (The new separate method)
            external_data = self._handle_external_overrides(key_name)

            if external_data is not None:
                final_inputs[key_name] = external_data
            else:
                # STEP 2: Fallback to existing YAML logic via the common processor
                print(f"  -> Loading '{key_name}' from YAML config.")
                final_inputs[key_name] = self._process_input_item(input_item)

        print(f"  -> Final prepared inputs: {list(final_inputs.keys())}")
        return final_inputs


    def _prepare_inputs_for(self, crew_name: str) -> dict:
        """
        Prepares the inputs dictionary for a specific crew by resolving values
        from the job config.
        """
        crew_def = self.job_config["crews"][crew_name]
        inputs_def = crew_def.get("input", {})  # Get the inputs dictionary
        final_inputs = {}

        print(f"📦 [App] Preparing inputs for '{crew_name}'...")

        # Loop through each placeholder and its defined value
        for placeholder, value_def in inputs_def.items():

            # Case 1: The value is a dictionary defining a file source
            if isinstance(value_def, dict) and value_def.get("source") == "file":
                file_path = Path(value_def["path"])
                file_format = value_def.get("format", "text")
                print(f"  -> Loading '{placeholder}' from file: {file_path}")

                if file_format == "json":
                    with open(file_path, 'r', encoding='utf-8') as f:
                        final_inputs = json.load(f)
                else:  # Plain text
                    with open(file_path, 'r', encoding='utf-8') as f:
                        final_inputs = f.read()

            # Case 2: The value is provided directly (e.g., a string)
            else:
                print(f"  -> Loading '{placeholder}' directly from config.")
                final_inputs = value_def


        return final_inputs




    def execute_crew_with_retry(
        self, 
        crew_name: str, 
        inputs: Dict[str, Any], 
        max_retries: int = 0,
        filename_suffix: Optional[str] = None,
            output_folder: Optional[str] = None
    ) -> Any:
        """
        Executes a crew with retry logic managed by the application.
        
        Args:
            crew_name: Name of the crew to run.
            inputs: Input dictionary for the crew.
            max_retries: Maximum number of retries allowed.
            filename_suffix: Optional suffix for output files.
            output_folder: optional output folder to group different generated output
            
        Returns:
            The result of the successful execution, or the last result if all retries fail.
        """


        attempt = 0
        success = False
        last_result = None
        
        # Total attempts = initial run (1) + retries
        while attempt <= max_retries:
            attempt += 1
            print(f"🔄 [App] Execution Attempt {attempt}/{max_retries + 1} for crew '{crew_name}'")
            
            current_suffix = filename_suffix
            if attempt > 1:
                base_suffix = filename_suffix or crew_name
                current_suffix = f"{base_suffix}_retry_{attempt}"
            
            # Run the crew
            last_result = self.orchestrator.run_crew(
                crew_name=crew_name,
                inputs=inputs,
                filename_suffix=current_suffix,
                mode=ExecutionMode.INTERACTIVE
            )
            
            # Get output file for validation
            output_file = self.orchestrator.get_last_output_file()
            
            # Validate
            if self.validate_execution(last_result, output_file,output_folder):
                print(f"✅ [App] Validation Success for '{crew_name}'!")
                success = True
                break
            
            print(f"❌ [App] Validation Failed for '{crew_name}'.")
            
            # Update State on failure
            execution_id = self.orchestrator.get_last_execution_id()
            if execution_id:
                print(f"   -> Updating state for execution {execution_id} to FAILED")
                self.state_manager.update_status(
                    execution_id, 
                    ExecutionStatus.FAILED, 
                    metadata={"reason": "Validation failed", "attempt": attempt}
                )
            
            if attempt > max_retries:
                print(f"🛑 [App] Max retries reached for '{crew_name}'. Giving up.")
        
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
            print(f"{class_name}:{output_file}")
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





