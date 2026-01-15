"""
Shared LLM initialization utilities for all application implementations.
"""
from pathlib import Path
from typing import Any, Tuple, Optional, TYPE_CHECKING
from amsha.llm_factory.dependency.llm_container import LLMContainer
from amsha.llm_factory.domain.model.llm_type import LLMType

if TYPE_CHECKING:
    from amsha.llm_factory.domain.model.llm_model_config import LLMModelConfig
    from amsha.llm_factory.domain.model.llm_parameters import LLMParameters
    from amsha.llm_factory.domain.model.llm_output_config import LLMOutputConfig

from amsha.crew_forge.exceptions import (
    CrewConfigurationException,
    ErrorContext,
    ErrorMessageBuilder,
    wrap_external_exception
)
from amsha.common.logger import get_logger, MetricsLogger


class SharedLLMInitializationService:
    """Shared LLM initialization logic for all application implementations."""
    
    @staticmethod
    def initialize_llm(llm_config_path: str, llm_type: LLMType,
                       model_config: Optional["LLMModelConfig"] = None,
                       llm_params: Optional["LLMParameters"] = None) -> Tuple[Any, str, Optional["LLMOutputConfig"]]:
        """
        Initialize LLM instance using the LLM factory with consistent patterns.
        
        Args:
            llm_config_path: Path to the LLM configuration file (used as fallback or for container init)
            llm_type: Type of LLM to build (CREATIVE or EVALUATION)
            model_config: Optional specific model configuration to use
            llm_params: Optional specific LLM parameters to use
            
        Returns:
            Tuple of (llm_instance, model_name, output_config)
            
        Raises:
            CrewConfigurationException: If LLM configuration is invalid or file not found
        """
        logger = get_logger("llm_factory.initialization")
        metrics_logger = MetricsLogger(logger)
        
        logger.info("LLM initialization requested", extra={
            "llm_type": llm_type.value,
            "has_model_override": model_config is not None,
            "has_params_override": llm_params is not None
        })
        
        context = ErrorContext("SharedLLMInitializationService", "initialize_llm")
        context.add_context("llm_config_path", llm_config_path)
        context.add_context("llm_type", llm_type.value)
        
        try:
            # Validate config file exists - still required for container initialization 
            # (unless we want to refactor container to not need a path if overrides are provided, 
            # but let's keep it simple for now and rely on the file existence check from before)
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
                logger.debug("Building CREATIVE LLM instance", extra={
                    "llm_type": "CREATIVE"
                })
                build_llm = llm_builder.build_creative(
                    model_config_override=model_config,
                    params_override=llm_params
                )
            elif llm_type == LLMType.EVALUATION:
                logger.debug("Building EVALUATION LLM instance", extra={
                    "llm_type": "EVALUATION"
                })
                build_llm = llm_builder.build_evaluation(
                    model_config_override=model_config,
                    params_override=llm_params
                )
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
            # CrewAI 1.8.0 expects LLM wrapper instances, not the raw provider
            llm_instance = provider.get_raw_llm()
            
            # Get output_config from model_config for custom aliases/folder organization
            output_config = model_config.output_config if model_config else None
            
            # Log successful initialization with configuration details
            llm_config_dict = {
                "llm_type": llm_type.value,  # CREATIVE or EVALUATION
                "model": model_config.model if model_config else "from_config",
                "temperature": llm_params.temperature if llm_params else "from_config",
                "top_p": llm_params.top_p if llm_params else "from_config",
                "max_tokens": llm_params.max_completion_tokens if llm_params else "from_config",
                "has_base_url": bool(model_config.base_url) if model_config else False,
            }
            
            metrics_logger.log_llm_config(model_name, llm_config_dict)
            
            logger.info("LLM initialized successfully", extra={
                "model_name": model_name,
                "llm_type": llm_type.value,
                "has_output_config": output_config is not None
            })
            
            return llm_instance, model_name, output_config
            
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