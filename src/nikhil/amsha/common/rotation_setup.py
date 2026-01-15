"""
Log rotation configuration utility for Amsha applications.

⚠️  THESE UTILITIES ARE OPTIONAL!

Amsha provides sensible default rotation settings out of the box.
You only need these utilities if you want to OVERRIDE the defaults.

Default settings (created automatically if no config exists):
- Enabled: True
- Max size: 50 MB
- Interval: 24 hours
- Retention: 30 days

Use these utilities to customize rotation for your needs:

Example - Using defaults (no setup needed):
    from amsha.common.logger import get_logger
    logger = get_logger("my_app")  # Works immediately with defaults!

Example - Customizing settings (optional):
    from amsha.common.rotation_setup import setup_rotation_for_environment
    setup_rotation_for_environment()  # Override with environment-specific settings
    
    from amsha.common.logger import get_logger
    logger = get_logger("my_app")
"""
from pathlib import Path
from typing import Optional, Dict, Any
import yaml
import os


def setup_rotation_config(
    enabled: bool = True,
    max_size_mb: int = 50,
    rotation_interval_hours: int = 24,
    archive_retention_days: int = 30,
    config_dir: Optional[Path] = None
) -> Path:
    """
    Create log rotation configuration file programmatically.
    
    ⚠️  CALL ONCE at the start of your application, before any logger initialization.
    This prevents interactive prompts from Nibandha.
    
    Once the config file is created, ALL get_logger() calls in your entire
    application will use this configuration. You do NOT need to call this
    for every function or class that uses the logger.
    
    Args:
        enabled: Enable/disable log rotation
        max_size_mb: Max log size in MB before rotation
        rotation_interval_hours: Max hours before rotation
        archive_retention_days: Days to keep archived logs
        config_dir: Optional custom config directory (defaults to .Nibandha/config)
        
    Returns:
        Path to the created config file
        
    Example:
        # At the very start of your application, before any imports that use logger:
        from amsha.common.rotation_setup import setup_rotation_config
        setup_rotation_config(enabled=True, max_size_mb=50)
        
        # Now safe to use logger anywhere in your app
        from amsha.common.logger import get_logger
        from my_app.service1 import Service1  # Uses logger internally
        from my_app.service2 import Service2  # Also uses logger
        
        logger = get_logger("my_app")
        service1 = Service1()  # All use the same rotation config
        service2 = Service2()
    """
    if config_dir is None:
        config_dir = Path(".Nibandha/config")
    
    config_dir.mkdir(parents=True, exist_ok=True)
    config_file = config_dir / "rotation_config.yaml"
    
    config = {
        'enabled': enabled,
        'max_size_mb': max_size_mb,
        'rotation_interval_hours': rotation_interval_hours,
        'archive_retention_days': archive_retention_days,
        'backup_count': 5,
        'log_data_dir': 'logs/data',
        'archive_dir': 'logs/archive',
        'timestamp_format': '%Y-%m-%d'
    }
    
    with open(config_file, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)
    
    return config_file


def setup_rotation_for_environment(
    environment: Optional[str] = None,
    config_dir: Optional[Path] = None,
    custom_configs: Optional[Dict[str, Dict[str, Any]]] = None
) -> Path:
    """
    Create environment-specific log rotation configuration.
    
    ⚠️  THIS IS OPTIONAL! Amsha provides sensible defaults automatically.
    Only use this if you want to OVERRIDE the defaults with custom settings.
    
    Default settings (if you don't call this):
    - Enabled: True, Max size: 50MB, Interval: 24h, Retention: 30 days
    
    Args:
        environment: Environment name (development, staging, production).
                    Defaults to ENVIRONMENT env var or "development"
        config_dir: Optional custom config directory
        custom_configs: Optional dict mapping environment names to config dicts
        
    Returns:
        Path to the created config file
        
    Example:
        # In your main.py or entry point
        if __name__ == "__main__":
            # ✅ Call ONCE at the very start
            from amsha.common.rotation_setup import setup_rotation_for_environment
            setup_rotation_for_environment()  # Uses ENVIRONMENT env var
            
            # Now ALL your classes/functions can use logger safely
            from my_app.crew_manager import CrewManager
            from my_app.service import MyService
            
            # Both will use the same rotation config
            manager = CrewManager()  # Internally uses get_logger()
            service = MyService()    # Also uses get_logger()
        
        # Or specify custom configs
        custom = {
            "test": {"enabled": False},
            "prod": {"enabled": True, "max_size_mb": 200}
        }
        setup_rotation_for_environment("prod", custom_configs=custom)
    """
    if environment is None:
        environment = os.getenv("ENVIRONMENT", "development")
    
    # Default environment-specific configs
    default_configs = {
        "development": {
            "enabled": True,
            "max_size_mb": 10,
            "rotation_interval_hours": 6,
            "archive_retention_days": 7
        },
        "staging": {
            "enabled": True,
            "max_size_mb": 50,
            "rotation_interval_hours": 12,
            "archive_retention_days": 30
        },
        "production": {
            "enabled": True,
            "max_size_mb": 200,
            "rotation_interval_hours": 24,
            "archive_retention_days": 90
        },
        "test": {
            "enabled": False
        }
    }
    
    # Use custom configs if provided, otherwise use defaults
    configs = custom_configs if custom_configs else default_configs
    
    # Get config for environment, fallback to development
    env_config = configs.get(environment, configs.get("development", {}))
    
    # Add default values
    config = {
        'enabled': env_config.get('enabled', True),
        'max_size_mb': env_config.get('max_size_mb', 10),
        'rotation_interval_hours': env_config.get('rotation_interval_hours', 24),
        'archive_retention_days': env_config.get('archive_retention_days', 30),
        'backup_count': env_config.get('backup_count', 5),
        'log_data_dir': env_config.get('log_data_dir', 'logs/data'),
        'archive_dir': env_config.get('archive_dir', 'logs/archive'),
        'timestamp_format': env_config.get('timestamp_format', '%Y-%m-%d')
    }
    
    if config_dir is None:
        config_dir = Path(".Nibandha/config")
    
    config_dir.mkdir(parents=True, exist_ok=True)
    config_file = config_dir / "rotation_config.yaml"
    
    with open(config_file, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)
    
    return config_file


def disable_rotation(config_dir: Optional[Path] = None) -> Path:
    """
    Create a configuration that disables log rotation.
    
    Useful for testing or environments where rotation is not needed.
    
    Args:
        config_dir: Optional custom config directory
        
    Returns:
        Path to the created config file
    """
    return setup_rotation_config(
        enabled=False,
        config_dir=config_dir
    )
