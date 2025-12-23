"""
Protocol extension examples for CrewForge.

This file demonstrates how to create custom implementations that conform
to CrewForge Protocol interfaces, enabling flexible extension patterns.
"""

from typing import Dict, Any, Union, Optional
from amsha.crew_forge import CrewApplication, CrewOrchestrator, CrewManager
from amsha.execution_runtime.domain.execution_mode import ExecutionMode
from amsha.execution_runtime.domain.execution_handle import ExecutionHandle
from amsha.crew_monitor.service.crew_performance_monitor import CrewPerformanceMonitor
from crewai import Crew


class MockCrewApplication:
    """
    Mock implementation of CrewApplication Protocol for testing.
    
    This class demonstrates how to create a test double that conforms
    to the CrewApplication Protocol interface without inheriting from
    any base class.
    """
    
    def __init__(self):
        self.execution_history = []
        self.last_output_file = None
        
    def run_crew(
        self, 
        crew_name: str, 
        inputs: Dict[str, Any], 
        mode: ExecutionMode = ExecutionMode.INTERACTIVE
    ) -> Union[Any, ExecutionHandle]:
        """Mock crew execution that records calls."""
        execution_record = {
            "crew_name": crew_name,
            "inputs": inputs,
            "mode": mode.value,
            "timestamp": "2024-01-01T00:00:00Z"
        }
        self.execution_history.append(execution_record)
        
        # Return mock result
        return {
            "status": "completed",
            "crew": crew_name,
            "result": f"Mock execution of {crew_name}",
            "inputs_processed": len(inputs)
        }
    
    def prepare_inputs_for(self, crew_name: str) -> Dict[str, Any]:
        """Mock input preparation."""
        return {
            "mock_input": f"prepared_for_{crew_name}",
            "timestamp": "2024-01-01T00:00:00Z",
            "source": "mock_preparation"
        }
    
    def clean_json(self, output_filename: str, max_retries: int = 2) -> bool:
        """Mock JSON cleaning that always succeeds."""
        print(f"Mock cleaning JSON file: {output_filename}")
        return True
    
    def get_last_output_file(self) -> Optional[str]:
        """Return mock output file path."""
        return self.last_output_file or "mock_output.json"


class LoggingCrewApplication:
    """
    Logging wrapper that conforms to CrewApplication Protocol.
    
    This demonstrates the decorator pattern with Protocol interfaces,
    where you can wrap any CrewApplication implementation with
    additional functionality.
    """
    
    def __init__(self, wrapped_app: CrewApplication):
        self.wrapped_app = wrapped_app
        self.execution_log = []
    
    def run_crew(
        self, 
        crew_name: str, 
        inputs: Dict[str, Any], 
        mode: ExecutionMode = ExecutionMode.INTERACTIVE
    ) -> Union[Any, ExecutionHandle]:
        """Log crew execution and delegate to wrapped application."""
        print(f"🚀 [LOG] Starting crew execution: {crew_name}")
        print(f"📊 [LOG] Input keys: {list(inputs.keys())}")
        print(f"⚙️ [LOG] Execution mode: {mode.value}")
        
        try:
            result = self.wrapped_app.run_crew(crew_name, inputs, mode)
            print(f"✅ [LOG] Crew execution completed successfully")
            
            self.execution_log.append({
                "crew_name": crew_name,
                "status": "success",
                "input_count": len(inputs),
                "mode": mode.value
            })
            
            return result
            
        except Exception as e:
            print(f"❌ [LOG] Crew execution failed: {e}")
            
            self.execution_log.append({
                "crew_name": crew_name,
                "status": "failed",
                "error": str(e),
                "input_count": len(inputs),
                "mode": mode.value
            })
            
            raise
    
    def prepare_inputs_for(self, crew_name: str) -> Dict[str, Any]:
        """Log input preparation and delegate."""
        print(f"📦 [LOG] Preparing inputs for crew: {crew_name}")
        inputs = self.wrapped_app.prepare_inputs_for(crew_name)
        print(f"📊 [LOG] Prepared {len(inputs)} input parameters")
        return inputs
    
    def clean_json(self, output_filename: str, max_retries: int = 2) -> bool:
        """Log JSON cleaning and delegate."""
        print(f"🧹 [LOG] Cleaning JSON file: {output_filename}")
        result = self.wrapped_app.clean_json(output_filename, max_retries)
        print(f"✅ [LOG] JSON cleaning {'succeeded' if result else 'failed'}")
        return result
    
    def get_last_output_file(self) -> Optional[str]:
        """Delegate to wrapped application."""
        return self.wrapped_app.get_last_output_file()


class CustomCrewManager:
    """
    Custom implementation of CrewManager Protocol.
    
    This demonstrates how to create a custom crew manager that
    conforms to the Protocol interface without inheriting from
    any base class.
    """
    
    def __init__(self, model_name: str = "custom-model"):
        self._model_name = model_name
        self._output_file = None
        self.crew_configs = {
            "test_crew": {
                "agents": ["analyst", "writer"],
                "tasks": ["analyze", "write_report"],
                "description": "Test crew configuration"
            }
        }
    
    def build_atomic_crew(
        self, 
        crew_name: str, 
        filename_suffix: Optional[str] = None
    ) -> Crew:
        """Build a mock crew for demonstration."""
        print(f"🔨 [CustomManager] Building crew: {crew_name}")
        
        if crew_name not in self.crew_configs:
            raise ValueError(f"Unknown crew configuration: {crew_name}")
        
        config = self.crew_configs[crew_name]
        print(f"📋 [CustomManager] Crew config: {config}")
        
        # In a real implementation, you would create actual CrewAI agents and tasks
        # For this example, we'll create a minimal mock crew
        from unittest.mock import Mock
        
        mock_crew = Mock(spec=Crew)
        mock_crew.kickoff = Mock(return_value=f"Mock result from {crew_name}")
        
        # Set output file with suffix if provided
        base_name = f"{crew_name}_output"
        if filename_suffix:
            self._output_file = f"{base_name}_{filename_suffix}.json"
        else:
            self._output_file = f"{base_name}.json"
        
        return mock_crew
    
    @property
    def model_name(self) -> str:
        """Return the model name."""
        return self._model_name
    
    @property
    def output_file(self) -> Optional[str]:
        """Return the current output file path."""
        return self._output_file


def example_mock_application():
    """Example using mock application for testing."""
    print("🔧 Example: Mock Application")
    
    mock_app = MockCrewApplication()
    
    # Use the mock app like any other CrewApplication
    inputs = mock_app.prepare_inputs_for("test_crew")
    result = mock_app.run_crew("test_crew", inputs)
    
    print(f"📊 Execution history: {mock_app.execution_history}")
    print(f"✅ Result: {result}")


def example_logging_wrapper():
    """Example using logging wrapper around real application."""
    print("🔧 Example: Logging Wrapper")
    
    # Create a mock base application
    base_app = MockCrewApplication()
    
    # Wrap it with logging functionality
    logging_app = LoggingCrewApplication(base_app)
    
    # Use the wrapped app - all calls will be logged
    inputs = logging_app.prepare_inputs_for("logged_crew")
    result = logging_app.run_crew("logged_crew", inputs)
    
    print(f"📊 Execution log: {logging_app.execution_log}")


def example_custom_manager():
    """Example using custom crew manager."""
    print("🔧 Example: Custom Crew Manager")
    
    manager = CustomCrewManager("gpt-4")
    
    # Build a crew using the custom manager
    crew = manager.build_atomic_crew("test_crew", "v1")
    
    print(f"🏷️ Manager model: {manager.model_name}")
    print(f"📄 Output file: {manager.output_file}")
    
    # Execute the crew (mock execution)
    result = crew.kickoff(inputs={"test": "data"})
    print(f"✅ Crew result: {result}")


def example_protocol_polymorphism():
    """Example demonstrating Protocol-based polymorphism."""
    print("🔧 Example: Protocol Polymorphism")
    
    def process_with_any_app(app: CrewApplication, crew_name: str) -> Dict[str, Any]:
        """
        Function that works with any CrewApplication Protocol implementation.
        
        This demonstrates how Protocol interfaces enable polymorphism
        without inheritance - any object that has the required methods
        will work with this function.
        """
        print(f"🔄 Processing crew '{crew_name}' with app type: {type(app).__name__}")
        
        # Prepare inputs
        inputs = app.prepare_inputs_for(crew_name)
        
        # Run the crew
        result = app.run_crew(crew_name, inputs)
        
        # Clean output if available
        output_file = app.get_last_output_file()
        if output_file:
            app.clean_json(output_file)
        
        return {
            "crew_name": crew_name,
            "app_type": type(app).__name__,
            "result": result,
            "output_file": output_file
        }
    
    # This function works with ANY CrewApplication Protocol implementation
    apps = [
        MockCrewApplication(),
        LoggingCrewApplication(MockCrewApplication())
    ]
    
    for app in apps:
        result = process_with_any_app(app, "polymorphic_crew")
        print(f"✅ Result from {result['app_type']}: {result['result']}")


if __name__ == "__main__":
    """
    Run Protocol extension examples.
    """
    
    print("CrewForge Protocol Extension Examples")
    print("=" * 50)
    
    example_mock_application()
    print()
    
    example_logging_wrapper()
    print()
    
    example_custom_manager()
    print()
    
    example_protocol_polymorphism()
    print()
    
    print("✅ All Protocol extension examples completed!")
    print("💡 These patterns enable flexible, testable, and extensible code")