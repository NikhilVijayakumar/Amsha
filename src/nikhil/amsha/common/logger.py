"""
Comprehensive logging for Amsha (stdlib-only).

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
"""
from typing import Optional, Dict, Any, Callable
import logging
import os
import time
import functools
from logging.handlers import RotatingFileHandler

_configured = False
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


def _configure() -> None:
    """
    Configure the root Amsha logger with a rotating file handler and console handler.
    Idempotent - only runs once per process.
    """
    global _configured
    if _configured:
        return

    level = os.getenv("AMSHA_LOG_LEVEL", "INFO")
    root = logging.getLogger("Amsha")
    root.setLevel(level.upper())
    root.propagate = False

    formatter = StructuredFormatter(
        fmt='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    logs_dir = os.getenv("AMSHA_LOG_DIR", "logs")
    os.makedirs(logs_dir, exist_ok=True)

    file_handler = RotatingFileHandler(
        os.path.join(logs_dir, "amsha.log"),
        maxBytes=50 * 1024 * 1024,
        backupCount=30,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    root.addHandler(file_handler)

    # Only add a console handler if one isn't already attached (avoids duplicate
    # console output when the root handler is configured elsewhere).
    if not any(isinstance(h, logging.StreamHandler) for h in root.handlers):
        console = logging.StreamHandler()
        console.setFormatter(formatter)
        root.addHandler(console)

    _configured = True


def get_logger(module_name: Optional[str] = None, log_level: Optional[str] = None) -> logging.Logger:
    """
    Get or create a logger instance for Amsha.
    
    All logs are written to logs/amsha.log and console (path overridable via
    the AMSHA_LOG_DIR environment variable).
    
    Args:
        module_name: Optional module name for hierarchical logging (e.g., "crew_forge")
        log_level: Optional log level override (DEBUG, INFO, WARNING, ERROR, CRITICAL)
                  Defaults to environment variable AMSHA_LOG_LEVEL or INFO
        
    Returns:
        Configured logger instance
        
    Examples:
        >>> logger = get_logger()  # Root Amsha logger
        >>> logger.info("Application started")
        
        >>> crew_logger = get_logger("crew_forge")
        >>> crew_logger.debug("Building crew", extra={"crew_name": "test", "tokens": 1500})
    """
    global _module_loggers
    
    _configure()
    
    logger = logging.getLogger(f"Amsha.{module_name}" if module_name else "Amsha")
    
    if log_level:
        logger.setLevel(log_level.upper())
    
    # Cache module loggers to avoid recreation
    if module_name and module_name not in _module_loggers:
        _module_loggers[module_name] = logger
    
    return logger


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


def reset_logger():
    """
    Reset the logger configuration. Primarily for testing purposes.
    """
    global _configured, _module_loggers
    root = logging.getLogger("Amsha")
    for handler in list(root.handlers):
        root.removeHandler(handler)
    _configured = False
    _module_loggers = {}
