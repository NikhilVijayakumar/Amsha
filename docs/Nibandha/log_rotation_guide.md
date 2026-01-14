# Nibandha Log Rotation Guide

## Overview

Nibandha v1.0.1 introduces comprehensive log rotation capabilities for the Amsha library. Log rotation prevents unbounded log file growth by:

- **Automatic rotation** based on file size OR time elapsed
- **Timestamped log files** for easy identification
- **Auto-archival** of old logs to a separate directory
- **Configurable cleanup** to manage disk space

> [!IMPORTANT]
> **Amsha is a library** - log cleanup is the **client's responsibility**. The library provides cleanup utilities, but client applications decide when to call them.

## Why Log Rotation?

Without rotation, log files grow indefinitely, which can:
- **Exhaust disk space** on long-running applications
- **Slow down log analysis** (large files are hard to grep/search)
- **Impact performance** (large file I/O operations)

With rotation enabled:
- ✅ **Bounded disk usage** - old logs are archived and deleted
- ✅ **Easier debugging** - smaller, timestamped files
- ✅ **Better performance** - active log stays small

## Default Configuration (Works Out of the Box)

**No setup required!** Amsha provides sensible defaults automatically:

```python
# Just use the logger - defaults are created automatically!
from amsha.common.logger import get_logger

logger = get_logger("my_app")
logger.info("It just works!")  # No setup needed!
```

**Default settings:**
- Rotation: Enabled
- Max log size: 50 MB
- Rotation interval: 24 hours
- Archive retention: 30 days

## Custom Configuration (Optional)

Want to override the defaults? Use the `rotation_setup` utility:

```python
# At the very start of your application (e.g., in main)
from amsha.common.rotation_setup import setup_rotation_for_environment

# Automatically configures based on ENVIRONMENT env var
# (development, staging, production)
setup_rotation_for_environment()

# Now safe to use logger - no interactive prompts!
from amsha.common.logger import get_logger
logger = get_logger("my_app")
```

This prevents interactive prompts from Nibandha by creating the config file programmatically.

## FAQ

### Do I need to call setup functions?

**No!** Amsha provides sensible defaults automatically. Just use the logger:

```python
from amsha.common.logger import get_logger
logger = get_logger("my_app")  # Works immediately - no setup needed!
```

The setup functions (`setup_rotation_for_environment()`, etc.) are **OPTIONAL** - only use them if you want to override the defaults.

### Do I need to call setup for every class/function that uses the logger?

**No!** You call `setup_rotation_for_environment()` **ONCE** at the very start of your application (e.g., in `if __name__ == "__main__"`). 

Once the config file is created at `.Nibandha/config/rotation_config.yaml`, **ALL** `get_logger()` calls anywhere in your entire application will use it.

```python
# main.py - Your entry point
if __name__ == "__main__":
    # ✅ Call ONCE at the start
    from amsha.common.rotation_setup import setup_rotation_for_environment
    setup_rotation_for_environment()
    
    # Now ALL these classes can safely use logger
    from my_app.crew_manager import CrewManager     # Uses get_logger() internally
    from my_app.data_service import DataService     # Also uses get_logger()
    from my_app.processor import Processor          # Also uses get_logger()
    
    # All will use the same rotation config - no need to setup again!
    manager = CrewManager()
    service = DataService()
    processor = Processor()
```

### What if the config file already exists?

If the config file already exists (from a previous run or deployment), it will be **overwritten** with the new settings. If you want to preserve existing settings, check if the file exists first:

```python
from pathlib import Path
from amsha.common.rotation_setup import setup_rotation_for_environment

config_file = Path(".Nibandha/config/rotation_config.yaml")
if not config_file.exists():
    setup_rotation_for_environment()
```

### When should I create the config?

**Option 1: Application startup** (Recommended for most apps)
```python
if __name__ == "__main__":
    setup_rotation_for_environment()
    # ... rest of your app
```

**Option 2: Deployment/setup script** (For servers/production)
```bash
# deploy.sh
python -c "from amsha.common.rotation_setup import setup_rotation_for_environment; setup_rotation_for_environment()"
# Then run your app
python main.py
```

**Option 3: Docker entrypoint** (For containerized apps)
```dockerfile
ENTRYPOINT ["sh", "-c", "python -c 'from amsha.common.rotation_setup import setup_rotation_for_environment; setup_rotation_for_environment()' && python main.py"]
```

## Configuration

> [!IMPORTANT]
> **Config-File-First Approach**: Amsha is a backend library that may be integrated into various client applications (APIs, services, batch jobs, etc.). Clients **must provide a configuration file** - there is no interactive setup. This gives clients full control over how and when rotation is configured.

### Configuration Files

Nibandha looks for rotation configuration in:
- `.Nibandha/config/rotation_config.yaml` (recommended)
- `.Nibandha/config/rotation_config.yml`
- `.Nibandha/config/rotation_config.json`

**If no configuration file is found, rotation will be handled by Nibandha's defaults.** Clients should create the config file before initializing the logger.

### Creating Configuration

Clients should create the configuration file as part of their deployment/setup process:

#### YAML Format (Recommended)

```yaml
enabled: true
max_size_mb: 50                # Rotate when log exceeds 50MB
rotation_interval_hours: 12    # OR rotate every 12 hours
archive_retention_days: 90     # Delete archives older than 90 days
log_data_dir: logs/data        # Active log directory
archive_dir: logs/archive      # Archived logs directory
timestamp_format: "%Y-%m-%d_%H-%M-%S"  # Log filename format
```

#### JSON Format

```json
{
  "enabled": true,
  "max_size_mb": 50,
  "rotation_interval_hours": 12,
  "archive_retention_days": 90,
  "log_data_dir": "logs/data",
  "archive_dir": "logs/archive",
  "timestamp_format": "%Y-%m-%d_%H-%M-%S"
}
```

### Configuration Options

| Option | Default | Description |
|--------|---------|-------------|
| `enabled` | `false` | Enable/disable log rotation |
| `max_size_mb` | `10` | Max log file size in MB before rotation |
| `rotation_interval_hours` | `24` | Max hours before rotation (whichever comes first) |
| `archive_retention_days` | `30` | Days to keep archived logs |
| `log_data_dir` | `logs/data` | Directory for active log files |
| `archive_dir` | `logs/archive` | Directory for archived logs |
| `timestamp_format` | `%Y-%m-%d_%H-%M-%S` | Strftime format for log filenames |

### Disabling Rotation

To disable rotation, either:
1. Set `enabled: false` in the config file
2. Don't create a config file (rotation disabled by default)

When disabled, Amsha uses single-file logging at `.Nibandha/Amsha/logs/Amsha.log`.

## Directory Structure

### With Rotation Enabled

```
.Nibandha/
├── config/
│   └── rotation_config.yaml          # Cached configuration
└── Amsha/
    ├── logs/
    │   ├── data/                      # Active logs
    │   │   └── 2026-01-14_05-30-00.log
    │   └── archive/                   # Archived logs
    │       ├── 2026-01-13_10-00-00.log
    │       ├── 2026-01-13_22-15-30.log
    │       └── 2026-01-14_02-45-12.log
    ├── output/
    └── execution/
```

### With Rotation Disabled

```
.Nibandha/
├── config/
│   └── rotation_config.yaml          # enabled: false
└── Amsha/
    ├── logs/
    │   └── Amsha.log                  # Single log file
    ├── output/
    └── execution/
```

## Usage in Amsha

### Importing Utilities

```python
from amsha.common.logger import (
    get_logger,
    should_rotate,
    rotate_logs,
    cleanup_old_archives,
    get_rotation_config
)
```

### Inspecting Configuration

```python
# Get current rotation configuration
config = get_rotation_config()

if config and config.enabled:
    print(f"Rotation enabled")
    print(f"Max size: {config.max_size_mb}MB")
    print(f"Interval: {config.rotation_interval_hours}h")
    print(f"Retention: {config.archive_retention_days} days")
else:
    print("Rotation disabled")
```

### Automatic Rotation

Rotation happens automatically based on **size OR time** triggers:

```python
logger = get_logger("crew_forge")

# Log normally - Nibandha handles rotation automatically
for task in tasks:
    logger.info(f"Processing {task.name}")
    # ... do work ...
```

When the log file exceeds `max_size_mb` OR `rotation_interval_hours`, Nibandha will:
1. Close the current log file
2. Move it to the archive directory
3. Create a new timestamped log file
4. Continue logging seamlessly

### Manual Rotation

For client applications that need explicit control:

```python
logger = get_logger("my_app")

# Check if rotation is needed
if should_rotate():
    logger.info("Rotation threshold reached, rotating logs...")
    rotate_logs()
    logger.info("Log rotation complete")
```

### Client-Driven Cleanup

> [!WARNING]
> **Cleanup is not automatic!** Client applications must call `cleanup_old_archives()` at appropriate times.

## Client Integration Patterns

### Pattern 1: Startup Cleanup

Clean up old logs when your application starts:

```python
def main():
    """Application entry point."""
    logger = get_logger("my_app")
    
    # Cleanup old archives on startup
    deleted = cleanup_old_archives()
    if deleted > 0:
        logger.info(f"Startup cleanup: removed {deleted} old log archives")
    
    # Continue with application logic
    run_application()
```

**When to use**: Most applications should do this. Ensures old logs don't accumulate indefinitely.

### Pattern 2: Scheduled Maintenance

For long-running applications, schedule periodic cleanup:

```python
import schedule

def cleanup_task():
    """Periodic cleanup task."""
    logger = get_logger("worker")
    deleted = cleanup_old_archives()
    logger.info(f"Scheduled cleanup: removed {deleted} archives")

# Run cleanup daily at 3 AM
schedule.every().day.at("03:00").do(cleanup_task)

def main():
    logger = get_logger("worker")
    
    while True:
        schedule.run_pending()
        # ... do work ...
```

**When to use**: Long-running services, daemons, or worker processes.

### Pattern 3: Manual Trigger

Expose cleanup as an admin command:

```python
import click

@click.group()
def cli():
    pass

@cli.command()
def cleanup_logs():
    """Manually clean up old log archives."""
    logger = get_logger("admin")
    deleted = cleanup_old_archives()
    click.echo(f"Removed {deleted} old log archives")

@cli.command()
def check_logs():
    """Check current log configuration."""
    config = get_rotation_config()
    if config and config.enabled:
        click.echo(f"Rotation: ON")
        click.echo(f"Max size: {config.max_size_mb}MB")
        click.echo(f"Retention: {config.archive_retention_days} days")
    else:
        click.echo("Rotation: OFF")

if __name__ == "__main__":
    cli()
```

**When to use**: Applications with admin CLIs or management interfaces.

### Pattern 4: Rotation Check in Loop

For heavy logging workloads, check rotation periodically:

```python
def process_large_dataset(items):
    """Process items with heavy logging."""
    logger = get_logger("processor")
    
    for i, item in enumerate(items):
        # Do work with extensive logging
        logger.info(f"Processing {item.id}")
        logger.debug(f"Item details: {item}")
        # ... complex processing ...
        
        # Check rotation every 100 items
        if i % 100 == 0 and should_rotate():
            logger.info(f"Rotating logs at item {i}")
            rotate_logs()
```

**When to use**: Batch processing, data pipelines, or any code with heavy logging.

## Examples

### Example 1: Basic Application with Config Setup

```python
from pathlib import Path
import yaml
from amsha.common.logger import get_logger, cleanup_old_archives

def setup_logging_config():
    """Setup log rotation config on first deployment."""
    config_dir = Path(".Nibandha/config")
    config_file = config_dir / "rotation_config.yaml"
    
    # Only create if doesn't exist
    if not config_file.exists():
        config_dir.mkdir(parents=True, exist_ok=True)
        
        config = {
            'enabled': True,
            'max_size_mb': 50,
            'rotation_interval_hours': 24,
            'archive_retention_days': 30
        }
        
        with open(config_file, 'w') as f:
            yaml.dump(config, f)
        
        print(f"Created log rotation config at {config_file}")

def main():
    # Setup config (typically in deployment script or first-run)
    setup_logging_config()
    
    # Initialize logger (reads config automatically)
    logger = get_logger("my_app")
    
    # Clean up old archives on startup
    cleanup_old_archives()
    
    # Use logger normally
    logger.info("Application started")
    # ... application logic ...
    logger.info("Application completed")

if __name__ == "__main__":
    main()
```

### Example 2: Long-Running Worker

```python
from amsha.common.logger import get_logger, should_rotate, rotate_logs, cleanup_old_archives
import time

def worker_loop():
    logger = get_logger("worker")
    cleanup_old_archives()  # Startup cleanup
    
    iteration = 0
    while True:
        # Do work
        logger.info(f"Worker iteration {iteration}")
        
        # Check rotation every 1000 iterations
        if iteration % 1000 == 0 and should_rotate():
            rotate_logs()
        
        iteration += 1
        time.sleep(1)

if __name__ == "__main__":
    worker_loop()
```

### Example 3: CLI with Admin Commands

```python
import click
from amsha.common.logger import (
    get_logger,
    cleanup_old_archives,
    get_rotation_config,
    rotate_logs
)

@click.group()
def cli():
    """My Application CLI"""
    pass

@cli.command()
def run():
    """Run the main application."""
    logger = get_logger("app")
    cleanup_old_archives()  # Cleanup on start
    
    logger.info("Running application...")
    # ... application logic ...

@cli.command()
def logs_cleanup():
    """Clean up old log archives."""
    deleted = cleanup_old_archives()
    click.echo(f"✅ Removed {deleted} old log archives")

@cli.command()
def logs_rotate():
    """Manually rotate logs."""
    rotate_logs()
    click.echo("✅ Logs rotated")

@cli.command()
def logs_status():
    """Show log rotation status."""
    config = get_rotation_config()
    
    if config and config.enabled:
        click.echo("📋 Log Rotation Status")
        click.echo(f"  Status: ENABLED")
        click.echo(f"  Max size: {config.max_size_mb}MB")
        click.echo(f"  Interval: {config.rotation_interval_hours}h")
        click.echo(f"  Retention: {config.archive_retention_days} days")
    else:
        click.echo("⚠️  Log rotation is DISABLED")

if __name__ == "__main__":
    cli()
```

## Troubleshooting

### Issue: Logs not rotating despite large size

**Cause**: Rotation might be disabled or config file missing.

**Solution**: Check configuration:
```python
config = get_rotation_config()
if config:
    print(f"Enabled: {config.enabled}")
else:
    print("No config file found - rotation disabled")
```

Create config file at `.Nibandha/config/rotation_config.yaml` if needed.

### Issue: Old archives not being deleted

**Cause**: Cleanup is client-driven, not automatic.

**Solution**: Ensure your client code calls `cleanup_old_archives()` at startup or on a schedule.

### Issue: Can't find log files

**Solution**: Check directory structure based on rotation status:
- **Enabled**: `.Nibandha/Amsha/logs/data/YYYY-MM-DD_HH-MM-SS.log`
- **Disabled**: `.Nibandha/Amsha/logs/Amsha.log`

## Best Practices

1. **Provide config file in deployment** - Don't rely on runtime configuration. Create the config file as part of your deployment/setup process.

2. **Environment-specific configs** - Use different configs for dev/staging/prod:
   ```python
   import os
   import yaml
   from pathlib import Path
   
   def setup_rotation_for_environment():
       env = os.getenv("ENVIRONMENT", "development")
       
       configs = {
           "development": {"enabled": True, "max_size_mb": 10, "archive_retention_days": 7},
           "staging": {"enabled": True, "max_size_mb": 50, "archive_retention_days": 30},
           "production": {"enabled": True, "max_size_mb": 200, "archive_retention_days": 90}
       }
       
       config_dir = Path(".Nibandha/config")
       config_dir.mkdir(parents=True, exist_ok=True)
       
       with open(config_dir / "rotation_config.yaml", 'w') as f:
           yaml.dump(configs[env], f)
   ```

3. **Enable rotation for production** - Always enable rotation for production deployments to prevent disk space issues.

4. **Choose appropriate size limits** - Consider your logging volume:
   - Light logging: 10-50MB
   - Moderate logging: 50-200MB
   - Heavy logging: 200-500MB

5. **Set reasonable retention periods**:
   - Development: 7-14 days
   - Production: 30-90 days
   - Compliance requirements: Adjust as needed

6. **Call cleanup on startup** - Most applications should clean up old logs when they start.

7. **Monitor disk usage** - Even with rotation, monitor disk space to ensure cleanup is working.

8. **Test rotation** - Verify rotation works in your environment before deploying to production.

9. **Version control your config template** - Keep a template config file in version control, populate it during deployment.

## API Reference

### `get_rotation_config() -> Optional[LogRotationConfig]`

Get the current log rotation configuration.

**Returns**: `LogRotationConfig` object if configured, `None` otherwise.

---

### `should_rotate() -> bool`

Check if log rotation is needed based on size or time triggers.

**Returns**: `True` if rotation is needed, `False` otherwise.

---

### `rotate_logs() -> None`

Manually trigger log rotation and archive the current log file.

Creates a new timestamped log file and moves the current one to the archive directory.

---

### `cleanup_old_archives() -> int`

Delete archived log files older than the configured retention period.

**Returns**: Number of archive files deleted.

**Note**: This is a utility for client applications. Clients decide when to call it.

---

## Related Documentation

- [Nibandha CR-002: Log Rotation](file:///e:/Python/Amsha/Nibandha-main/docs/CR/CR-002-Log-Rotation.md) - Original change request
- [Nibandha Reference Tests](file:///e:/Python/Amsha/Nibandha-main/tests/test_log_rotation.py) - Comprehensive test suite
- [Amsha Logger Module](file:///e:/Python/Amsha/src/nikhil/amsha/common/logger.py) - Logger implementation
