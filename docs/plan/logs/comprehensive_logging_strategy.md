# Comprehensive Logging Strategy for Amsha

## Vision
Transform Amsha into a fully observable system with structured logging, metrics tracking, performance monitoring, and execution tracing - going far beyond simple print statement replacement.

## Logging Dimensions

### 1. Execution Tracing
**What**: Track the complete lifecycle of crew executions
- Execution start/end with timestamps
- State transitions (PENDING → RUNNING → COMPLETED/FAILED)
- Input/output snapshots
- Dependency chains

**Example**:
```python
logger.info("Crew execution initiated", extra={
    "execution_id": state.execution_id,
    "crew_name": crew_name,
    "inputs": inputs,
    "timestamp": time.time(),
    "mode": mode.value
})
```

### 2. Performance Metrics
**What**: Capture quantitative performance data
- Execution duration
- Token usage (prompt, completion, total)
- CPU/memory utilization
- API call latency
- File I/O operations

**Example**:
```python
logger.info("Crew execution completed", extra={
    "execution_id": execution_id,
    "duration_seconds": duration,
    "total_tokens": metrics["total_tokens"],
    "prompt_tokens": metrics["prompt_tokens"],
    "completion_tokens": metrics["completion_tokens"],
    "cpu_percent": metrics["cpu_usage_end_percent"],
    "memory_mb": metrics["memory_usage_change_mb"]
})
```

### 3. LLM Operations
**What**: Detailed LLM configuration and usage
- Model selection rationale
- Parameter values (temperature, top_p, etc.)
- API endpoint and version
- Rate limiting and retries
- Cost tracking (if applicable)

**Example**:
```python
logger.info("LLM instance created", extra={
    "model": model_config.model,
    "provider": "azure",
    "endpoint": endpoint_url,
    "temperature": params.temperature,
    "max_tokens": params.max_completion_tokens,
    "api_version": model_config.api_version
})
```

### 4. File Operations 
**What**: Track all file I/O with validation results
- File paths (input/output)
- Validation status
- File sizes
- Cleaning operations
- Errors and retries

**Example**:
```python
logger.info("JSON file validated", extra={
    "file_path": output_file_path,
    "file_size_bytes": os.path.getsize(output_file_path),
    "validation_status": "success",
    "crew_name": crew_name,
    "model_name": model_name
})
```

### 5. Error Context
**What**: Rich error information for debugging
- Exception type and message
- Stack trace
- Execution context
- Retry attempts
- Recovery actions

**Example**:
```python
logger.error("Crew execution failed", extra={
    "execution_id": execution_id,
    "crew_name": crew_name,
    "error_type": type(e).__name__,
    "error_message": str(e),
    "attempt": attempt,
    "max_retries": max_retries
}, exc_info=True)  # Includes stack trace
```

### 6. Configuration Changes
**What**: Track configuration overrides and modifications
- LLM config overrides
- Output config (aliases, folders)
- Runtime parameter changes

**Example**:
```python
logger.info("LLM configuration override applied", extra={
    "override_model": llm_config_override["model_config"]["model"],
    "output_alias": llm_config_override.get("model_config", {}).get("output_config", {}).get("alias"),
    "parameters_changed": list(llm_config_override.get("llm_parameters", {}).keys())
})
```

## Enhanced Logger Module

### Updated `logger.py`

```python
"""
Comprehensive logging for Amsha with metrics and tracing support.
"""
from nikhil.nibandha.core import Nibandha, AppConfig
from typing import Optional, Dict, Any
import logging
import time
import functools

# ... existing singleton code ...

def log_execution(logger: logging.Logger, operation_name: str):
    """
    Decorator to automatically log function execution with timing.
    
    Usage:
        @log_execution(logger, "build_crew")
        def build_atomic_crew(self, crew_name):
            # ...
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            logger.debug(f"{operation_name} started", extra={
                "operation": operation_name,
                "function": func.__name__
            })
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                logger.info(f"{operation_name} completed", extra={
                    "operation": operation_name,
                    "duration_seconds": round(duration, 4),
                    "status": "success"
                })
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"{operation_name} failed", extra={
                    "operation": operation_name,
                    "duration_seconds": round(duration, 4),
                    "error_type": type(e).__name__,
                    "status": "failed"
                }, exc_info=True)
                raise
        return wrapper
    return decorator


class MetricsLogger:
    """Helper class for logging structured metrics."""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    def log_execution_metrics(self, crew_name: str, execution_id: str, 
                             metrics: Dict[str, Any], duration: float):
        """Log comprehensive execution metrics."""
        self.logger.info("Execution metrics captured", extra={
            "crew_name": crew_name,
            "execution_id": execution_id,
            "duration_seconds": round(duration, 4),
            "total_tokens": metrics.get("general", {}).get("total_tokens", 0),
            "prompt_tokens": metrics.get("general", {}).get("prompt_tokens", 0),
            "completion_tokens": metrics.get("general", {}).get("completion_tokens", 0),
            "cpu_usage_percent": metrics.get("general", {}).get("cpu_usage_end_percent", 0),
            "memory_change_mb": metrics.get("general", {}).get("memory_usage_change_mb", 0),
            "gpu_metrics": metrics.get("gpu", {})
        })
    
    def log_llm_config(self, model_name: str, config: Dict[str, Any]):
        """Log LLM configuration details."""
        self.logger.info("LLM configuration", extra={
            "model_name": model_name,
            "model": config.get("model"),
            "temperature": config.get("temperature"),
            "top_p": config.get("top_p"),
            "max_tokens": config.get("max_completion_tokens"),
            "stream": config.get("stream", False)
        })
    
    def log_file_operation(self, operation: str, file_path: str, 
                          status: str, **extra_data):
        """Log file I/O operations."""
        self.logger.info(f"File operation: {operation}", extra={
            "operation": operation,
            "file_path": file_path,
            "status": status,
            **extra_data
        })
```

## Implementation Priorities

### Phase 1: Core Instrumentation (High Priority)
1. **BaseCrewOrchestrator** - Execution lifecycle
   - Start/end logging with full context
   - State transition logging
   - Performance metrics integration
   
2. **CrewPerformanceMonitor** - Metrics capture
   - Enhanced metric logging
   - Structured performance data
   
3. **LLM Services** - Configuration and usage
   - Model initialization logging
   - Parameter tracking
   - API call metrics

### Phase 2: File Operations (Medium Priority)
4. **SharedJSONFileService** - File I/O
   - Validation results
   - File sizes and paths
   - Cleaning operations
   
5. **AtomicCrewFileManager** - Output management
   - File creation tracking
   - Output alias usage
   - Directory operations

### Phase 3: Supporting Services (Lower Priority)
6. **Remaining modules** - Complete coverage
   - Input preparation
   - Configuration loading
   - Synchronization operations

## Structured Logging Standards

### Standard Extra Fields
Every log should include relevant context:

```python
{
    # Execution Context
    "execution_id": "uuid",
    "crew_name": "crew_name",
    "model_name": "model_name",
    
    # Timing
    "timestamp": 1234567890.123,
    "duration_seconds": 5.432,
    
    # Metrics
    "total_tokens": 2500,
    "memory_mb": 45.2,
    "cpu_percent": 12.5,
    
    # Status
    "status": "success|failed|running",
    "attempt": 1,
    
    # Errors (if applicable)
    "error_type": "ValueError",
    "error_message": "Invalid input"
}
```

### Log Levels by Category

| Category | Level | Use Case |
|----------|-------|----------|
| Execution lifecycle | INFO | Start, complete, state changes |
| Performance metrics | INFO | Token usage, timing, resources |
| Configuration | INFO | LLM params, overrides |
| File operations | INFO | Validation, saves |
| Debug traces | DEBUG | Internal processing |
| Warnings | WARNING | Retries, fallbacks, deprecations |
| Errors | ERROR | Failures, validation errors |
| Critical failures | CRITICAL | System failures, max retries |

## Migration Strategy

### Not Just Replacement - Enhancement

**Before** (print only):
```python
print(f"✅ [App] Validation Success for '{crew_name}'!")
```

**After** (comprehensive logging):
```python
logger.info("Crew validation successful", extra={
    "crew_name": crew_name,
    "execution_id": execution_id,
    "output_file": output_file,
    "file_size_bytes": os.path.getsize(output_file),
    "validation_duration": validation_end - validation_start,
    "attempt": attempt,
    "model_name": model_name
})
```

### Adding New Instrumentation

Identify logging opportunities beyond print statements:
- Before/after expensive operations
- At state transition points
- When making external API calls
- During error recovery
- When using fallback logic

## Testing & Validation

### Verification Checklist
- [ ] `.Nibandha/Amsha/logs/Amsha.log` created
- [ ] All execution IDs traceable through logs
- [ ] Performance metrics logged for each execution
- [ ] Error logs include full context
- [ ] Structured data parseable (valid JSON in extra)
- [ ] No sensitive data (API keys) in logs
- [ ] Log volume reasonable (not too verbose)

### Performance Impact
- Measure baseline execution time
- Compare with logging enabled
- Target: <5% overhead
- Use DEBUG level for high-volume logs

## Success Metrics

1. **Observability**: Can reconstruct any execution from logs
2. **Debuggability**: Errors include full context for resolution
3. **Performance**: Metrics available for optimization
4. **Traceability**: Each request traceable end-to-end
5. **Analytics**: Aggregate metrics for system health
