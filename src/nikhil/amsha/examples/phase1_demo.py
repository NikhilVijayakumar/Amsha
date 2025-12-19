import time
from amsha.execution_state.service.state_manager import StateManager
from amsha.execution_state.domain.enums import ExecutionStatus
from amsha.execution_runtime.service.runtime_engine import RuntimeEngine
from amsha.execution_runtime.domain.execution_mode import ExecutionMode

def long_running_task(name: str):
    print(f"Task {name} started")
    time.sleep(1)
    print(f"Task {name} finished")
    return f"Hello {name}"

def main():
    print("🚀 Starting Phase 1 Verification Demo")
    
    # 1. Setup Services
    state_manager = StateManager()
    runtime = RuntimeEngine()
    
    # 2. Create Execution State
    print("\n💾 Creating Execution State...")
    state = state_manager.create_execution(inputs={"name": "Amsha User"})
    print(f"   Created Execution ID: {state.execution_id}")
    print(f"   Status: {state.status.value}")
    
    # 3. Update State
    print("\n🔄 Updating State...")
    state_manager.update_status(state.execution_id, ExecutionStatus.RUNNING, metadata={"node": "demo-script"})
    print(f"   Status updated to: {state_manager.get_execution(state.execution_id).status.value}")
    
    # 4. Submit to Runtime (Background)
    print("\n⚡ Submitting Task to Runtime (Background)...")
    handle = runtime.submit(long_running_task, "Amsha User", mode=ExecutionMode.BACKGROUND)
    print(f"   Task submitted. Handle ID: {handle.execution_id}")
    print(f"   Immediate Status: {handle.status().value}")
    
    # Wait for result
    print("   Waiting for result...")
    result = handle.result()
    print(f"   Result received: {result}")
    print(f"   Final Status: {handle.status().value}")
    
    # 5. Link Runtime Result to State
    print("\n🔗 Linking Result to State...")
    state.set_output("greeting", result)
    state_manager.update_status(state.execution_id, ExecutionStatus.COMPLETED)
    
    # 6. Verify Final State
    final_state = state_manager.get_execution(state.execution_id)
    print("\n✅ Final State Verification:")
    print(f"   ID: {final_state.execution_id}")
    print(f"   Status: {final_state.status.value}")
    print(f"   Outputs: {final_state.outputs}")
    print(f"   History Length: {len(final_state.history)}")
    
    runtime.shutdown()
    print("\n🎉 Demo Completed Successfully!")

if __name__ == "__main__":
    main()
