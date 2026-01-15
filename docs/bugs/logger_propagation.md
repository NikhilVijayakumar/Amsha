# Logger Propagation Issue

## Issue
The Amsha logger does not disable propagation after Nibandha initialization, causing all Amsha logs to propagate to the root logger. When used in applications where multiple libraries use Nibandha (e.g., Akashavani uses Amsha, Pravaha, and Akashavani's own logger), this causes all Amsha logs to leak into the root logger's file.

## Impact
- **Log Files**: Amsha logs appear in both `.Nibandha/Amsha/logs/data/` AND the root logger's file (e.g., `.Nibandha/Pravaha/logs/data/`)
- **Empty Files**: Amsha log files may appear empty or minimal because logs are being captured by root logger handlers instead
- **Log Separation**: Cannot properly separate logs by component

## Root Cause
In `amsha/common/logger.py`, after Nibandha initialization (line 94-95):
```python
_amsha_nibandha = Nibandha(config).bind()
_amsha_nibandha.logger.info("Amsha logger initialized via Nibandha")
```

The logger's `propagate` attribute is not set to `False`, so it defaults to `True`.

## Recommended Fix
Add `propagate = False` after Nibandha initialization:

```python
_amsha_nibandha = Nibandha(config).bind()

# Disable propagation to prevent logs from going to root logger
_amsha_nibandha.logger.propagate = False

_amsha_nibandha.logger.info("Amsha logger initialized via Nibandha")
```

## Workaround for Client Applications
Client applications can work around this by manually setting propagation after Amsha initializes:

```python
from amsha.common.logger import get_logger
import logging

# This triggers Amsha initialization
logger = get_logger()

# Fix propagation after initialization
logging.getLogger("Amsha").propagate = False
```

However, this must be done AFTER the first call to `get_logger()`.

## Related Issues
- Similar issue exists in Pravaha (see `docs/pravaha/bugs/logger_propagation.md`)
- Timestamp format issue (see `amsha_logger_timestamp.md`)

## Priority
**High** - Affects all multi-component applications using Amsha
