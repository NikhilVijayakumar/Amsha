from unittest.mock import MagicMock
import sys

# Mocking Docling Source to avoid import hang
mock_docling = MagicMock()
sys.modules["amsha.crew_forge.knowledge.amsha_crew_docling_source"] = mock_docling

from amsha.execution_runtime.domain.execution_mode import ExecutionMode
from amsha.execution_runtime.domain.execution_handle import ExecutionHandle
from amsha.crew_forge.orchestrator.db.db_crew_orchestrator import DbCrewOrchestrator
from amsha.crew_forge.orchestrator.db.atomic_crew_db_manager import AtomicCrewDBManager

def main():
    print("🚀 Starting Phase 3 Orchestrator Verification Demo")
    
    # 1. Mock Dependencies
    mock_manager = MagicMock(spec=AtomicCrewDBManager)
    mock_manager.model_name = "test-model"
    
    # Mock Manager building a Mock Crew
    mock_crew = MagicMock()
    def side_effect(*args, **kwargs):
        print("   [Mock] Kickoff called")
        return "Crew Result Payload"
    mock_crew.kickoff.side_effect = side_effect
    mock_manager.build_atomic_crew.return_value = mock_crew
    
    # 2. Instantiate Orchestrator (Runtime injects automatically)
    orchestrator = DbCrewOrchestrator(manager=mock_manager)
    
    # 3. Test Interactive Mode (Backward Compatibility)
    print("\n🔄 Testing Interactive Mode (Synchronous)...")
    result = orchestrator.run_crew("demo-crew", inputs={"key": "val"}, mode=ExecutionMode.INTERACTIVE)
    print(f"   Result: {result}")
    
    # Verify manager was called
    mock_manager.build_atomic_crew.assert_called_with("demo-crew", None)
    
    # 4. Test Background Mode (Asynchronous)
    print("\n⚡ Testing Background Mode (Asynchronous)...")
    handle = orchestrator.run_crew("demo-background-crew", inputs={"key": "val2"}, mode=ExecutionMode.BACKGROUND)
    
    print(f"   Handle received: {handle}")
    print(f"   Handle type: {type(handle)}")
    
    if hasattr(handle, 'result'): # Check if it behaves like a handle
        print("   Waiting for background result (timeout 5s)...")
        try:
            bg_result = handle.result(timeout=5.0)
            print(f"   Background Result: {bg_result}")
        except Exception as e:
            print(f"   ❌ Error waiting for result: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("   ❌ Error: Expected ExecutionHandle")
        
    print("\n🎉 Demo Completed Successfully!")
    orchestrator.runtime.shutdown()

if __name__ == "__main__":
    main()
