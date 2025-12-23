"""
Shared LLM initialization utilities for all application implementations.
"""
from pathlib import Path
from typing import Any, Tuple
from amsha.llm_factory.dependency.llm_container import LLMContainer
from amsha.llm_factory.domain.model.llm_type import LLMType
from amsha.crew_forge.exceptions import (
    CrewConfigurationException,
    ErrorContext,
    ErrorMessageBuilder,
    wrap_external_exception
)


class SharedLLMInitializationService:
    """Shared LLM initialization logic for all application implementations."""
    
    @staticmethod
    def initialize_llm(llm_config_path: str, llm_type: LLMType) -> Tuple[Any, str]:
        """
        Initialize LLM instance using the LLM factory with consistent patterns.
        
        Args:
            llm_config_path: Path to the LLM configuration file
            llm_type: Type of LLM to build (CREATIVE or EVALUATION)
            
        Returns:
            Tuple of (llm_instance, model_name)
            
        Raises:
            CrewConfigurationException: If LLM configuration is invalid or file not found
        """
        print("⚙️  [SharedLLMInit] Setting up LLM...")
        
        context = ErrorContext("SharedLLMInitializationService", "initialize_llm")
        context.add_context("llm_config_path", llm_config_path)
        context.add_context("llm_type", llm_type.value)
        
        try:
            # Validate config file exists
            config_path = Path(llm_config_path)
            if not config_path.exists():
                raise CrewConfigurationException(
                    message=ErrorMessageBuilder.configuration_error(
                        "LLM", 
                        "configuration file not found", 
                        llm_config_path
                    ),
                    config_details=f"LLM config file does not exist: {llm_config_path}"
                )
            
            # Set up the DI container for the LLM
            llm_container = LLMContainer()
            llm_container.config.llm.yaml_path.from_value(str(config_path))
            
            # Build the LLM based on type
            llm_builder = llm_container.llm_builder()
            
            if llm_type == LLMType.CREATIVE:
                print("  -> Building CREATIVE LLM...")
                build_llm = llm_builder.build_creative()
            elif llm_type == LLMType.EVALUATION:
                print("  -> Building EVALUATION LLM...")
                build_llm = llm_builder.build_evaluation()
            else:
                raise CrewConfigurationException(
                    message=ErrorMessageBuilder.configuration_error(
                        "LLM", 
                        f"invalid LLM type: {llm_type}. Must be CREATIVE or EVALUATION"
                    ),
                    config_details=f"Received LLM type: {llm_type}"
                )
            
            provider = build_llm.provider
            model_name = provider.model_name
            llm_instance = provider.get_raw_llm()
            
            print(f"  -> LLM initialized successfully: {model_name}")
            return llm_instance, model_name
            
        except CrewConfigurationException:
            # Re-raise crew_forge exceptions as-is
            raise
        except Exception as e:
            # Wrap any other unexpected exceptions
            raise wrap_external_exception(e, context, CrewConfigurationException)
    
    @staticmethod
    def get_model_name_from_config(llm_config_path: str, llm_type: LLMType) -> str:
        """
        Get model name without fully initializing the LLM (for lightweight operations).
        
        Args:
            llm_config_path: Path to the LLM configuration file
            llm_type: Type of LLM to check (CREATIVE or EVALUATION)
            
        Returns:
            Model name string
            
        Raises:
            CrewConfigurationException: If LLM configuration is invalid or file not found
        """
        # For now, we'll use the full initialization since the LLM factory
        # doesn't provide a lightweight way to get just the model name
        # This could be optimized in the future if needed
        _, model_name = SharedLLMInitializationService.initialize_llm(llm_config_path, llm_type)
        return model_name