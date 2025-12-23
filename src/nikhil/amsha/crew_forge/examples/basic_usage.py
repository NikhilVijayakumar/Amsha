"""
Basic usage examples for CrewForge Protocol-based architecture.

This file demonstrates how to use the new Protocol-based CrewForge API
for common use cases.
"""

from typing import Dict, Any
from amsha.crew_forge import (
    create_file_crew_application,
    create_db_crew_application,
    create_crew_application,
    FileCrewApplication,
    DbCrewApplication
)
from amsha.llm_factory.domain.model.llm_type import LLMType
from amsha.execution_runtime.domain.execution_mode import ExecutionMode


def example_file_based_application():
    """Example of using file-based crew application."""
    print("🔧 Example: File-based Crew Application")
    
    config_paths = {
        "job": "config/job_config.yaml",
        "app": "config/app_config.yaml",
        "llm": "config/llm_config.yaml"
    }
    
    # Method 1: Using factory function (recommended)
    app = create_file_crew_application(config_paths, LLMType.CREATIVE)
    
    # Method 2: Direct instantiation
    # app = FileCrewApplication(config_paths, LLMType.CREATIVE)
    
    # Prepare inputs from configuration
    inputs = app.prepare_inputs_for("example_crew")
    print(f"📦 Prepared inputs: {inputs}")
    
    # Run crew in interactive mode
    result = app.run_crew("example_crew", inputs, mode=ExecutionMode.INTERACTIVE)
    print(f"✅ Crew execution result: {result}")
    
    # Clean output JSON if needed
    output_file = app.get_last_output_file()
    if output_file:
        success = app.clean_json(output_file)
        print(f"🧹 JSON cleaning {'successful' if success else 'failed'}")


def example_database_based_application():
    """Example of using database-based crew application."""
    print("🔧 Example: Database-based Crew Application")
    
    config_paths = {
        "job": "config/job_config.yaml",
        "app": "config/app_config.yaml",
        "llm": "config/llm_config.yaml"
    }
    
    # Method 1: Using factory function (recommended)
    app = create_db_crew_application(config_paths, LLMType.EVALUATION)
    
    # Method 2: Direct instantiation
    # app = DbCrewApplication(config_paths, LLMType.EVALUATION)
    
    # Prepare inputs from configuration
    inputs = app.prepare_inputs_for("analysis_crew")
    print(f"📦 Prepared inputs: {inputs}")
    
    # Run crew in background mode
    handle = app.run_crew("analysis_crew", inputs, mode=ExecutionMode.BACKGROUND)
    print(f"🚀 Background execution started: {handle}")
    
    # Wait for completion and get result
    result = handle.result()
    print(f"✅ Crew execution result: {result}")


def example_generic_factory():
    """Example of using generic factory function."""
    print("🔧 Example: Generic Factory Function")
    
    config_paths = {
        "job": "config/job_config.yaml",
        "app": "config/app_config.yaml",
        "llm": "config/llm_config.yaml"
    }
    
    # Backend can be determined at runtime
    backend = "file"  # Could come from environment variable, config, etc.
    
    app = create_crew_application(backend, config_paths, LLMType.CREATIVE)
    
    # The returned app conforms to CrewApplication Protocol
    # regardless of the backend implementation
    inputs = app.prepare_inputs_for("dynamic_crew")
    result = app.run_crew("dynamic_crew", inputs)
    
    print(f"✅ Dynamic backend ({backend}) execution result: {result}")


def example_error_handling():
    """Example of proper error handling with the new architecture."""
    print("🔧 Example: Error Handling")
    
    from amsha.crew_forge import (
        CrewConfigurationException,
        CrewExecutionException,
        InputPreparationException
    )
    
    config_paths = {
        "job": "config/invalid_job_config.yaml",  # Intentionally invalid
        "app": "config/app_config.yaml",
        "llm": "config/llm_config.yaml"
    }
    
    try:
        app = create_file_crew_application(config_paths, LLMType.CREATIVE)
        inputs = app.prepare_inputs_for("test_crew")
        result = app.run_crew("test_crew", inputs)
        
    except CrewConfigurationException as e:
        print(f"❌ Configuration error: {e}")
        print("💡 Check your configuration files and paths")
        
    except InputPreparationException as e:
        print(f"❌ Input preparation error: {e}")
        print("💡 Check your input definitions in job config")
        
    except CrewExecutionException as e:
        print(f"❌ Execution error: {e}")
        print("💡 Check your crew configuration and LLM setup")
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        print("💡 This might be a bug - please report it")


def example_backward_compatibility():
    """Example showing backward compatibility with legacy classes."""
    print("🔧 Example: Backward Compatibility")
    
    from amsha.crew_forge import (
        AmshaCrewFileApplication,
        AmshaCrewDBApplication,
        create_amsha_file_application,
        create_amsha_db_application
    )
    
    config_paths = {
        "job": "config/job_config.yaml",
        "app": "config/app_config.yaml",
        "llm": "config/llm_config.yaml"
    }
    
    # Legacy class usage (still works)
    legacy_app = AmshaCrewFileApplication(config_paths, LLMType.CREATIVE)
    
    # Legacy factory functions
    legacy_file_app = create_amsha_file_application(config_paths, LLMType.CREATIVE)
    legacy_db_app = create_amsha_db_application(config_paths, LLMType.EVALUATION)
    
    print("✅ Legacy applications created successfully")
    print("💡 Consider migrating to new Protocol-based implementations")


if __name__ == "__main__":
    """
    Run examples (commented out to avoid actual execution).
    
    Uncomment the examples you want to run, but make sure you have
    valid configuration files in the expected locations.
    """
    
    print("CrewForge Protocol-based Architecture Examples")
    print("=" * 50)
    
    # Uncomment to run examples:
    # example_file_based_application()
    # example_database_based_application()
    # example_generic_factory()
    # example_error_handling()
    # example_backward_compatibility()
    
    print("\n💡 Uncomment the examples in __main__ to run them")
    print("📚 Make sure you have valid configuration files before running")