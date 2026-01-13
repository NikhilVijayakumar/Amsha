"""
Deprecated compatibility utilities for CrewAI upgrades.

This module contains backward compatibility helpers that are marked for deprecation.
These utilities will be removed in future versions as we fully align with CrewAI's native APIs.
"""
import warnings
from functools import wraps
from typing import Dict, Any, Callable


def deprecated(reason: str, removal_version: str = "3.0.0") -> Callable:
    """
    Decorator to mark functions as deprecated.
    
    Args:
        reason: Explanation of why the function is deprecated and what to use instead
        removal_version: Version when this will be removed (default: 3.0.0)
        
    Returns:
        Decorated function that emits DeprecationWarning when called
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            warnings.warn(
                f"{func.__name__} is deprecated and will be removed in version {removal_version}. "
                f"Reason: {reason}",
                DeprecationWarning,
                stacklevel=2
            )
            return func(*args, **kwargs)
        return wrapper
    return decorator


@deprecated(
    reason="drop_params is a workaround for parameter compatibility. "
           "Future versions should use CrewAI's native parameter validation.",
    removal_version="3.0.0"
)
def apply_drop_params_workaround(llm_kwargs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Apply drop_params=True to LLM kwargs as compatibility workaround.
    
    This allows CrewAI to ignore unrecognized parameters instead of raising errors.
    In future versions, we should only pass parameters that CrewAI natively supports.
    
    Args:
        llm_kwargs: Dictionary of LLM initialization parameters
        
    Returns:
        Updated kwargs dict with drop_params=True added
        
    Note:
        This is a temporary workaround for CrewAI 1.8.0 parameter compatibility.
        Will be removed in version 3.0.0.
    """
    llm_kwargs['drop_params'] = True
    return llm_kwargs
