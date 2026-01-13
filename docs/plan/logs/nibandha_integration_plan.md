# Implementation Plan: Nibandha Logging Integration for Amsha

## Executive Summary

Replace all print statements (86+ identified) in Amsha with structured logging using the Nibandha library to provide centralized, configurable, and production-ready logging.

## Nibandha API Analysis

### Core Components
```python
from nikhil.nibandha import Nibandha, AppConfig

# Initialize for Amsha
config = AppConfig(
    name="Amsha",
    custom_folders=["output/final", "output/intermediate"],
    log_level="INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
)

nb = Nibandha(config).bind()
logger = nb.logger  # Standard Python logger instance
```

### Logging Methods
- `logger.debug(msg)` - Detailed diagnostic information
- `logger.info(msg)` - General informational messages
- `logger.warning(msg)` - Warning messages
- `logger.error(msg)` - Error messages
- `logger.critical(msg)` - Critical failures

### Workspace Structure Created
```
.Nibandha/
└── Amsha/
    ├── logs/
    │   └── Amsha.log  # Rotated log file
    └── output/
        ├── final/
        └── intermediate/
```

## Print Statement Categorization

### Files and Statement Counts
1. **`amsha_crew_file_application.py`** - 15 statements
2. **`base_crew_orchestrator.py`** - 7 statements
3. **`shared_llm_initialization_service.py`** - 4 statements
4. **`crew_builder_service.py`** - 1 statement
5. **`shared_json_file_service.py`** - 7 statements
6. **`json_cleaner_utils.py`** - 6 statements  
7. **`sync_crew_config_manager.py`** - 8 statements
8. **`crew_blueprint_service.py`** - 2 statements
9. **`crew_monitor` package** - 3+ statements
10. **Others** - 33+ statements

### Log Level Mapping

| Current Print Pattern | Nibandha Level | Examples |
|-----------------------|----------------|----------|
| `print("✅ Success...")` | `INFO` | Successful operations |
| `print("⚙️ Setting up...")` | `INFO` | Process initiation |
| `print("🔄 Attempt...")` | `DEBUG` | Retry logic |
| `print("❌ Error...")` | `ERROR` | Failures |
| `print("🛑 Max retries...")` | `CRITICAL` | Fatal errors |
| `print("📦 Preparing...")` | `DEBUG` | Internal processing |
| Emoji-less technical | `DEBUG` | Debug traces |

## Implementation Strategy

### Phase 1: Infrastructure Setup

#### 1.1 Create Nibandha Instance (Singleton)
**NEW FILE**: `src/nikhil/amsha/common/logger.py`

```python
"""
Centralized logger for Amsha using Nibandha.
"""
from nikhil.nibandha import Nibandha, AppConfig
from typing import Optional
import logging

_amsha_logger: Optional[logging.Logger] = None

def get_amsha_logger(log_level: str = "INFO") -> logging.Logger:
    """
    Get or create the Amsha logger instance.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        
    Returns:
        Configured logger instance
    """
    global _amsha_logger
    
    if _amsha_logger is None:
        config = AppConfig(
            name="Amsha",
            custom_folders=[
                "output/final",
                "output/intermediate",
                "execution/state"
            ],
            log_level=log_level
        )
        
        nb = Nibandha(config).bind()
        _amsha_logger = nb.logger
        _amsha_logger.info("Amsha logger initialized via Nibandha")
    
    return _amsha_logger
```

#### 1.2 Update `pyproject.toml`
**Status**: ✅ Already done by user

```toml
dependencies = [
    "Nibandha @ git+https://github.com/NikhilVijayakumar/Nibandha.git@master",
    # ...
]
```

### Phase 2: Systematic Migration

#### Migration Pattern

**Before:**
```python
print(f"✅ [App] Validation Success for '{crew_name}'!")
```

**After:**
```python
from amsha.common.logger import get_amsha_logger

logger = get_amsha_logger()
logger.info(f"Validation success for '{crew_name}'", extra={"crew_name": crew_name})
```

#### Structured Logging Best Practices
```python
# Good - structured data in 'extra'
logger.info("Crew execution started", extra={
    "crew_name": crew_name,
    "execution_id": execution_id,
    "inputs": inputs
})

# Better than embedding f-strings everywhere
```

### Phase 3: File-by-File Migration

#### Priority Order
1. **Core Orchestrator** (`base_crew_orchestrator.py`) - Most critical
2. **LLM Services** (`shared_llm_initialization_service.py`)
3. **Application Layer** (`amsha_crew_file_application.py`)
4. **File Management** (`shared_json_file_service.py`, `json_cleaner_utils.py`)
5. **Supporting Services** (all others)

### Phase 4: Testing & Validation

1. **Verify log files created**: `.Nibandha/Amsha/logs/Amsha.log`
2. **Check console output**: Should still show logs (StreamHandler)
3. **Test log levels**: DEBUG should be hidden in INFO mode
4. **Verify structured data**: Extra fields logged correctly
5. **Performance check**: No significant slowdown

## Nibandha Enhancement Requests

### Change Requests (CR)

**CR-001: Expose `exports` in `__init__.py`**
- **File**: `Nibandha-main/src/nikhil/nibandha/__init__.py`
- **Current**: Empty file
- **Needed**:
```python
from nikhil.nibandha.core import Nibandha, AppConfig

__all__ = ["Nibandha", "AppConfig"]
```
- **Reason**: Makes imports cleaner: `from nikhil.nibandha import Nibandha`

**CR-002: Add Log Rotation Support**
- **Current**: Single log file grows infinitely
- **Needed**: `RotatingFileHandler` or `TimedRotatingFileHandler`
- **Suggested Config**:
```python
class AppConfig(BaseModel):
    max_bytes: int = 10_000_000  # 10MB
    backup_count: int = 5
```

**CR-003: Support for Contextual Loggers**
- **Enhancement**: Allow creating sub-loggers for modules
```python
# Example API
crew_logger = nb.get_logger("crew_forge")
llm_logger = nb.get_logger("llm_factory")
```

**CR-004: JSON Formatter Option**
- **Enhancement**: For machine-parseable logs
```python
class AppConfig(BaseModel):
    json_logging: bool = False  # Enable JSON format
```

### Bugs

*None identified - library appears functional*

## Migration Checklist

### Pre-Migration
- [ ] Install Nibandha dependency
- [ ] Create `amsha/common/logger.py`
- [ ] Add unit tests for logger initialization
- [ ] Document Nibandha integration in `README.md`

### Migration
- [ ] Migrate `base_crew_orchestrator.py`
- [ ] Migrate `shared_llm_initialization_service.py`
- [ ] Migrate `amsha_crew_file_application.py`
- [ ] Migrate `shared_json_file_service.py`
- [ ] Migrate `json_cleaner_utils.py`
- [ ] Migrate remaining files (30+ files)

### Post-Migration
- [ ] Remove all print statements (verify with grep)
- [ ] Test example application
- [ ] Verify log file creation
- [ ] Performance benchmark
- [ ] Update documentation

### Deprecation Logging
- [ ] Ensure deprecation warnings still work with logger
- [ ] Test `warnings.warn` integration

## Example Migration

### Before (base_crew_orchestrator.py)
```python
print(f"[BaseOrchestrator] Request received to run crew: '{crew_name}'")
print(f"[BaseOrchestrator] Created Execution State ID: {state.execution_id}")
```

### After
```python
from amsha.common.logger import get_amsha_logger

logger = get_amsha_logger()

logger.info("Request received to run crew", extra={"crew_name": crew_name})
logger.info("Execution state created", extra={
    "execution_id": state.execution_id,
    "crew_name": crew_name
})
```

## Risk Mitigation

1. **Backward Compatibility**: Keep console output via StreamHandler
2. **Performance**: Logging is async-safe, minimal overhead
3. **Debugging**: DEBUG level available for troubleshooting
4. **Testing**: Incremental migration allows gradual validation

## Success Criteria

- ✅ Zero print statements in production code
- ✅ All logs centralized in `.Nibandha/Amsha/logs/`
- ✅ Structured logging with contextual data
- ✅ Configurable log levels
- ✅ No performance degradation
- ✅ Documentation updated
