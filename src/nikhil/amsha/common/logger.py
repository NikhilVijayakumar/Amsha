"""
Comprehensive logging for Amsha using Nibandha.

This module provides structured logging with metrics tracking, execution tracing,
and performance monitoring - going beyond simple print replacement.

Basic Usage:
    from amsha.common.logger import get_logger, log_execution, MetricsLogger
    
    logger = get_logger("crew_forge")
    logger.info("Operation successful", extra={"crew_name": "test", "tokens": 1500})
    
    @log_execution(logger, "build_crew")
    def build_crew(name):
        # Automatically logs start, duration, and completion
        pass

Log Rotation (New in Nibandha v1.0.1):
    Rotation requires a config file at .Nibandha/config/rotation_config.yaml
    Client applications must create this file before initializing the logger.
    
    from amsha.common.logger import should_rotate, rotate_logs, cleanup_old_archives
    
    # Check if rotation is needed (size or time triggers)
    if should_rotate():
        rotate_logs()
    
    # Client applications should call cleanup when appropriate
    # (e.g., on startup, scheduled maintenance, or manual trigger)
    deleted_count = cleanup_old_archives()
    
    # Inspect current rotation configuration
    config = get_rotation_config()
    if config and config.enabled:
        print(f"Rotation enabled: max {config.max_size_mb}MB, {config.rotation_interval_hours}h")
"""
from nibandha.core import Nibandha, AppConfig, LogRotationConfig
from typing import Optional, Dict, Any, Callable
import logging
import os
import time
import functools

_amsha_nibandha: Optional[Nibandha] = None
_module_loggers: dict = {}


# ============================================================================
# Structured Logging Formatter
# ============================================================================

class StructuredFormatter(logging.Formatter):
    """
    Custom formatter that includes extra fields in log output.
    
    Formats log records to show structured metadata in a readable way:
    timestamp | logger_name | level | message | key1=value1 key2=value2
    """
    
    # Standard logging record attributes to exclude from extra fields
    EXCLUDED_ATTRS = {
        'name', 'msg', 'args', 'created', 'filename', 'funcName', 'levelname',
        'levelno', 'lineno', 'module', 'msecs', 'message', 'pathname', 'process',
        'processName', 'relativeCreated', 'thread', 'threadName', 'exc_info',
        'exc_text', 'stack_info', 'asctime', 'taskName'
    }
    
    def format(self, record: logging.LogRecord) -> str:
        # Format base message with standard format
        base_message = super().format(record)
        
        # Extract extra fields
        extra_fields = {}
        for key, value in record.__dict__.items():
            if key not in self.EXCLUDED_ATTRS:
                extra_fields[key] = value
        
        # If there are extra fields, append them to the message
        if extra_fields:
            # Format extra fields as key=value pairs
            extra_str = " | ".join(f"{k}={v}" for k, v in sorted(extra_fields.items()))
            return f"{base_message} | {extra_str}"
        
        return base_message


def _configure_structured_logging(logger: logging.Logger) -> None:
    """
    Configure the logger to use structured formatter for all handlers.
    
    Args:
        logger: Logger instance to configure
    """
    structured_formatter = StructuredFormatter(
        fmt='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Apply to all handlers
    for handler in logger.handlers:
        handler.setFormatter(structured_formatter)



def get_logger(module_name: Optional[str] = None, log_level: Optional[str] = None) -> logging.Logger:
    """
    Get or create a logger instance for Amsha.
    
    This function initializes Nibandha on first call and returns loggers for specific
    modules. All logs are written to .Nibandha/Amsha/logs/Amsha.log and console.
    
    **Automatic Default Config**: If no rotation config exists, a sensible default
    is created automatically. Clients can override this using rotation_setup utilities.
    
    Args:
        module_name: Optional module name for hierarchical logging (e.g., "crew_forge")
        log_level: Optional log level override (DEBUG, INFO, WARNING, ERROR, CRITICAL)
                  Defaults to environment variable AMSHA_LOG_LEVEL or INFO
        
    Returns:
        Configured logger instance
        
    Examples:
        >>> logger = get_logger()  # Root Amsha logger (auto-creates default config)
        >>> logger.info("Application started")
        
        >>> crew_logger = get_logger("crew_forge")
        >>> crew_logger.debug("Building crew", extra={"crew_name": "test", "tokens": 1500})
    """
    global _amsha_nibandha, _module_loggers
    
    # Initialize Nibandha on first call
    if _amsha_nibandha is None:
        # Create default rotation config if none exists
        # This prevents interactive prompts from Nibandha
        _ensure_default_rotation_config()
        
        # Get log level from environment or parameter or default
        level = log_level or os.getenv("AMSHA_LOG_LEVEL", "INFO")
        
        # Check if structured logging is enabled
        use_structured = os.getenv("AMSHA_STRUCTURED_LOGS", "false").lower() == "true"
        
        config = AppConfig(
            name="Amsha",
            custom_folders=[
                "output/final",
                "output/intermediate",
                "execution/state"
            ],
            log_level=level
        )
        
        _amsha_nibandha = Nibandha(config).bind()
        
        # Apply structured formatter if enabled
        if use_structured:
            _configure_structured_logging(_amsha_nibandha.logger)
        
        _amsha_nibandha.logger.info("Amsha logger initialized via Nibandha")
    
    # Return module-specific logger or root logger
    if module_name:
        logger_name = f"Amsha.{module_name}"
        
        # Cache module loggers to avoid recreation
        if logger_name not in _module_loggers:
            _module_loggers[logger_name] = logging.getLogger(logger_name)
            
        return _module_loggers[logger_name]
    
    return _amsha_nibandha.logger


def log_execution(logger: logging.Logger, operation_name: str) -> Callable:
    """
    Decorator to automatically log function execution with timing and error handling.
    
    Args:
        logger: Logger instance to use
        operation_name: Human-readable operation name
        
    Returns:
        Decorated function
        
    Usage:
        @log_execution(logger, "build_crew")
        def build_atomic_crew(self, crew_name):
            # Automatically logs start, duration, success/failure
            return crew
    """
    def decorator(func: Callable) -> Callable:
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
                    "error_message": str(e),
                    "status": "failed"
                }, exc_info=True)
                raise
        return wrapper
    return decorator


class MetricsLogger:
    """Helper class for logging structured metrics and performance data."""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    def log_execution_metrics(self, crew_name: str, execution_id: str, 
                             metrics: Dict[str, Any], duration: float):
        """
        Log comprehensive execution metrics.
        
        Args:
            crew_name: Name of the crew
            execution_id: Unique execution identifier
            metrics: Dict containing general and gpu metrics
            duration: Execution duration in seconds
        """
        general = metrics.get("general", {})
        self.logger.info("Execution metrics captured", extra={
            "crew_name": crew_name,
            "execution_id": execution_id,
            "duration_seconds": round(duration, 4),
            "total_tokens": general.get("total_tokens", 0),
            "prompt_tokens": general.get("prompt_tokens", 0),
            "completion_tokens": general.get("completion_tokens", 0),
            "cpu_usage_percent": general.get("cpu_usage_end_percent", 0),
            "memory_change_mb": general.get("memory_usage_change_mb", 0),
            "has_gpu_metrics": bool(metrics.get("gpu", {}))
        })
    
    def log_llm_config(self, model_name: str, config: Dict[str, Any]):
        """
        Log LLM configuration details.
        
        Args:
            model_name: Clean model name
            config: Dict containing LLM configuration
        """
        self.logger.info("LLM configuration applied", extra={
            "model_name": model_name,
            "model": config.get("model"),
            "temperature": config.get("temperature"),
            "top_p": config.get("top_p"),
            "max_tokens": config.get("max_completion_tokens"),
            "stream": config.get("stream", False),
            "has_base_url": bool(config.get("base_url") or config.get("endpoint"))
        })
    
    def log_file_operation(self, operation: str, file_path: str, 
                          status: str, **extra_data):
        """
        Log file I/O operations with context.
        
        Args:
            operation: Operation type (e.g., "validation", "save", "clean")
            file_path: Path to the file
            status: Operation status (success, failed)
            **extra_data: Additional context
        """
        self.logger.info(f"File operation: {operation}", extra={
            "operation": operation,
            "file_path": file_path,
            "status": status,
            **extra_data
        })


# ============================================================================
# Internal Helpers
# ============================================================================

def _ensure_default_rotation_config() -> None:
    """
    Internal helper to create a default rotation config if none exists.
    
    This prevents interactive prompts from Nibandha while providing
    sensible defaults. Clients can override by using rotation_setup utilities.
    """
    from pathlib import Path
    import yaml
    
    config_dir = Path(".Nibandha/config")
    config_file = config_dir / "rotation_config.yaml"
    
    # Only create if doesn't exist
    if not config_file.exists():
        config_dir.mkdir(parents=True, exist_ok=True)
        
        # Sensible defaults for development/testing
        default_config = {
            'enabled': True,
            'max_size_mb': 50,
            'rotation_interval_hours': 24,
            'archive_retention_days': 30,
            'log_data_dir': 'logs/data',
            'archive_dir': 'logs/archive',
            'timestamp_format': '%Y-%m-%d'  # Daily rotation - logs append to same file throughout the day
        }
        
        with open(config_file, 'w') as f:
            yaml.dump(default_config, f, default_flow_style=False)


# ============================================================================
# Log Rotation Utilities (Nibandha v1.0.1)
# ============================================================================

def should_rotate() -> bool:
    """
    Check if log rotation is needed based on size or time triggers.
    
    Returns:
        True if rotation is needed, False otherwise
        
    Note:
        Returns False if rotation is not enabled or Nibandha is not initialized.
    """
    global _amsha_nibandha
    
    if _amsha_nibandha is None:
        return False
    
    return _amsha_nibandha.should_rotate()


def rotate_logs() -> None:
    """
    Manually trigger log rotation and archive the current log file.
    
    This creates a new timestamped log file and moves the current one to the archive directory.
    Rotation must be enabled in the configuration.
    
    Raises:
        Warning if rotation is not enabled or Nibandha is not initialized.
    """
    global _amsha_nibandha
    
    if _amsha_nibandha is None:
        logging.warning("Cannot rotate logs: Nibandha not initialized")
        return
    
    _amsha_nibandha.rotate_logs()


def cleanup_old_archives() -> int:
    """
    Delete archived log files older than the configured retention period.
    
    Returns:
        Number of archive files deleted
        
    Note:
        This is a utility function for client applications. Clients should call this
        at appropriate times:
        - On application startup (cleanup old logs from previous runs)
        - Scheduled maintenance (e.g., daily/weekly cron job)
        - Manual trigger (e.g., admin command or button)
        
        Amsha is a library and does not automatically call cleanup.
    """
    global _amsha_nibandha
    
    if _amsha_nibandha is None:
        return 0
    
    return _amsha_nibandha.cleanup_old_archives()


def get_rotation_config() -> Optional[LogRotationConfig]:
    """
    Get the current log rotation configuration for inspection.
    
    Returns:
        LogRotationConfig object if rotation is configured, None otherwise
        
    Usage:
        config = get_rotation_config()
        if config and config.enabled:
            print(f"Max size: {config.max_size_mb}MB")
            print(f"Interval: {config.rotation_interval_hours}h")
            print(f"Retention: {config.archive_retention_days} days")
    """
    global _amsha_nibandha
    
    if _amsha_nibandha is None:
        return None
    
    return _amsha_nibandha.rotation_config


def reset_logger():
    """
    Reset the logger instance. Primarily for testing purposes.
    """
    global _amsha_nibandha, _module_loggers
    _amsha_nibandha = None
    _module_loggers = {}
