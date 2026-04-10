# Nibandha Log Rotation - Quick Start for Clients

**TL;DR**: Defaults work out of the box! Just use `get_logger()` - no setup needed.

This guide shows how to OPTIONALLY customize rotation if you want to override defaults.

## For Client Developers

### 0. Use Defaults (Simplest - Recommended)

No setup required! Just use the logger:

```python
from amsha.common.logger import get_logger

logger = get_logger("my_app")
logger.info("Application started")  # Works immediately with sensible defaults!
# Default: 50MB max, 24h interval, 30 days retention
```

### 1. Override with Quick Setup (Optional)

Use the `rotation_setup` utility if you want to override defaults:

```python
# At the very beginning of your main script
from amsha.common.rotation_setup import setup_rotation_for_environment

# This prevents interactive prompts from Nibandha
setup_rotation_for_environment()  # Uses ENVIRONMENT env var

# Now safe to initialize logger
from amsha.common.logger import get_logger
logger = get_logger("my_app")
```

### 2. Custom Configuration

For more control, create the config file manually:

```python
from pathlib import Path
import yaml

def setup_log_rotation():
    """Setup log rotation configuration."""
    config_dir = Path(".Nibandha/config")
    config_dir.mkdir(parents=True, exist_ok=True)
    
    config = {
        'enabled': True,
        'max_size_mb': 50,
        'rotation_interval_hours': 24,
        'archive_retention_days': 30
    }
    
    config_file = config_dir / "rotation_config.yaml"
    with open(config_file, 'w') as f:
        yaml.dump(config, f)
```

### 3. Environment-Specific Configs (Advanced)

Use the utility for automatic environment-based configuration:

```python
from amsha.common.rotation_setup import setup_rotation_for_environment

# Automatically selects config based on ENVIRONMENT env var
# Supports: development, staging, production
setup_rotation_for_environment()

# Or provide custom configs
custom_configs = {
    "test": {"enabled": False},
    "prod": {"enabled": True, "max_size_mb": 200, "archive_retention_days": 90}
}
setup_rotation_for_environment("prod", custom_configs=custom_configs)
```

### 4. Initialize Logger

```python
from amsha.common.logger import get_logger, cleanup_old_archives

# Setup config BEFORE initializing logger
setup_log_rotation()

# Now use logger
logger = get_logger("my_app")

# Clean up old logs on startup
deleted = cleanup_old_archives()
logger.info(f"Cleaned up {deleted} old log archives")
```

## Configuration Options

| Option | Default | Description |
|--------|---------|-------------|
| `enabled` | `false` | Enable/disable rotation |
| `max_size_mb` | `10` | Max log size before rotation |
| `rotation_interval_hours` | `24` | Max time before rotation |
| `archive_retention_days` | `30` | Days to keep archives |

## Key Points

1. **Defaults Work Out of the Box** - No setup needed, just use `get_logger()`
2. **Setup is Optional** - Only needed to override defaults  
3. **Client-Driven Cleanup** - Call `cleanup_old_archives()` when appropriate
4. **Environment-Specific** - Use `setup_rotation_for_environment()` for different configs

## See Also

- [Complete Guide](log_rotation_guide.md) - Comprehensive documentation
- [Config Template](rotation_config.template.yaml) - Template with all options
