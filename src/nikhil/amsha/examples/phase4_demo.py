from unittest.mock import MagicMock
import sys
import time

# Mocking Docling Source and any other heavy libs to avoid import hang
mock_docling = MagicMock()
sys.modules["amsha.crew_forge.knowledge.amsha_crew_docling_source"] = mock_docling

from amsha.execution_runtime.domain.execution_mode import ExecutionMode
from amsha.execution_state.domain.enums import ExecutionStatus
from amsha.execution_state.service.state_manager import StateManager
from amsha.crew_forge.orchestrator.db.db_crew_orchestrator import DbCrewOrchestrator
from amsha.crew_forge.orchestrator.db.atomic_crew_db_manager import AtomicCrewDBManager

def main():
    print("🚀 Starting Phase 4 State Integration Validation")
    
    # 1. Setup Dependencies
    mock_manager = MagicMock(spec=AtomicCrewDBManager)
    mock_manager.model_name = "test-model-v1"
    
    # Mock Manager building a Mock Crew with Token Usage
    mock_crew = MagicMock()
    
    # Mock result with token usage
    mock_result = MagicMock()
    mock_result.token_usage.total_tokens = 150
    mock_crew.kickoff.return_value = mock_result
    
    mock_manager.build_atomic_crew.return_value = mock_crew
    
    state_manager = StateManager() # In-memory default
    
    # 2. Instantiate Orchestrator
    orchestrator = DbCrewOrchestrator(manager=mock_manager, state_manager=state_manager)
    
    # 3. Test Background Execution
    print("\n⚡ Running Crew in Background...")
    
    handle = orchestrator.run_crew(
        "state-demo-crew", 
        inputs={"topic": "Integration"}, 
        mode=ExecutionMode.BACKGROUND
    )
    
    exec_id = getattr(handle, 'execution_state_id', None)
    print(f"   Handle Execution ID: {exec_id}")
    
    if not exec_id:
        print("   ❌ Error: Execution ID not found on handle")
        return

    # 4. Verify Initial State
    state_start = state_manager.get_execution(exec_id)
    print(f"   Initial Status: {state_start.status}")
    if state_start.status not in [ExecutionStatus.PENDING, ExecutionStatus.RUNNING]:
         print(f"   ❌ Unexpected initial status: {state_start.status}")

    # 5. Wait for Result
    print("   Waiting for completion...")
    try:
        handle.result(timeout=5.0)
    except Exception as e:
        print(f"   ❌ Execution failed or timed out: {e}")
        
    # 6. Verify Final State and Metrics
    state_final = state_manager.get_execution(exec_id)
    print(f"   Final Status: {state_final.status}")
    
    if state_final.status != ExecutionStatus.COMPLETED:
         print("   ❌ Status did not update to COMPLETED")
    else:
        print("   ✅ Status is COMPLETED")
        
    # Check Metrics
    metadata = state_final.metadata
    print(f"   Metadata: {metadata}")
    
    metrics = metadata.get("metrics", {})
    general = metrics.get("general", {})
    tokens = general.get("total_tokens")
    
    if tokens == 150:
        print(f"   ✅ Metrics persisted correctly: {tokens} tokens")
    else:
        print(f"   ❌ Metrics mismatch. Expected 150, got {tokens}")
        print(f"   Full Metrics: {metrics}")

    print("\n🎉 Phase 4 Validation Complete!")
    orchestrator.runtime.shutdown()

if __name__ == "__main__":
    main()
