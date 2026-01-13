"""
Shared JSON processing and file management utilities for all application implementations.
"""
from pathlib import Path
from typing import Optional, Tuple
from amsha.output_process.optimization.json_cleaner_utils import JsonCleanerUtils
from amsha.common.logger import get_logger, MetricsLogger
from amsha.crew_forge.exceptions import (
    CrewForgeException,
    ErrorContext,
    ErrorMessageBuilder,
    wrap_external_exception
)

# Module-level logger for static methods
_logger = get_logger("crew_forge.json_service")


class SharedJSONFileService:
    """Shared JSON processing and file management utilities."""
    
    @staticmethod
    def clean_json(output_filename: str, max_retries: int = 2,output_folder=None) -> bool:
        """
        Clean and validate a JSON file using consistent patterns across implementations.
        
        Args:
            output_filename: Path to the JSON file to be cleaned
            max_retries: Maximum number of retry attempts (currently unused by JsonCleanerUtils)
            
        Returns:
            True if JSON was successfully cleaned and validated, False otherwise
            
        Raises:
            CrewForgeException: If file operations fail
        """
        _logger.info("Cleaning JSON file", extra={
            "output_filename": output_filename
        })
        
        context = ErrorContext("SharedJSONFileService", "clean_json")
        context.add_context("output_filename", output_filename)
        
        try:
            # Validate file exists
            output_path = Path(output_filename)
            if not output_path.exists():
                raise FileNotFoundError(f"Output file not found: {output_filename}")
            
            # Use the existing JsonCleanerUtils for consistent behavior
            cleaner = JsonCleanerUtils(output_filename,output_folder)
            
            if cleaner.process_file():
                _logger.info("JSON validation successful", extra={
                    "validated_file": cleaner.output_file_path,
                    "original_file": output_filename
                })
                return True
            else:
                _logger.warning("JSON cleaning failed", extra={
                    "output_filename": output_filename
                })
                return False
                
        except Exception as e:
            if isinstance(e, CrewForgeException):
                raise
            else:
                raise wrap_external_exception(e, context, CrewForgeException)
    
    @staticmethod
    def clean_json_with_metrics(output_filename: str) -> Tuple[bool, Optional[str]]:
        """
        Clean and validate a JSON file and return both success status and output path.
        
        Args:
            output_filename: Path to the JSON file to be cleaned
            
        Returns:
            Tuple of (success_status, cleaned_file_path)
            - success_status: True if cleaning succeeded, False otherwise
            - cleaned_file_path: Path to the cleaned file if successful, None otherwise
            
        Raises:
            CrewForgeException: If file operations fail
        """
        _logger.info("Cleaning JSON file with metrics", extra={
            "output_filename": output_filename
        })
        
        context = ErrorContext("SharedJSONFileService", "clean_json_with_metrics")
        context.add_context("output_filename", output_filename)
        
        try:
            # Validate file exists
            output_path = Path(output_filename)
            if not output_path.exists():
                raise FileNotFoundError(f"Output file not found: {output_filename}")
            
            # Use the existing JsonCleanerUtils for consistent behavior
            cleaner = JsonCleanerUtils(output_filename)
            
            if cleaner.process_file():
                _logger.info("JSON validation successful", extra={
                    "validated_file": cleaner.output_file_path,
                    "original_file": output_filename
                })
                return True, cleaner.output_file_path
            else:
                _logger.warning("JSON cleaning failed", extra={
                    "output_filename": output_filename
                })
                return False, None
                
        except Exception as e:
            if isinstance(e, CrewForgeException):
                raise
            else:
                raise wrap_external_exception(e, context, CrewForgeException)
    
    @staticmethod
    def ensure_output_directory(output_path: str) -> Path:
        """
        Ensure that the output directory exists, creating it if necessary.
        
        Args:
            output_path: Path to the output file or directory
            
        Returns:
            Path object representing the directory
            
        Raises:
            CrewForgeException: If directory creation fails
        """
        context = ErrorContext("SharedJSONFileService", "ensure_output_directory")
        context.add_context("output_path", output_path)
        
        try:
            path = Path(output_path)
            
            # If it's a file path, get the parent directory
            if path.suffix:
                directory = path.parent
            else:
                directory = path
            
            # Create directory if it doesn't exist
            directory.mkdir(parents=True, exist_ok=True)
            _logger.debug("Directory ensured", extra={
                "directory": str(directory)
            })
            
            return directory
            
        except Exception as e:
            if isinstance(e, CrewForgeException):
                raise
            else:
                raise wrap_external_exception(e, context, CrewForgeException)
    
    @staticmethod
    def get_output_file_path(base_path: str, filename: str) -> str:
        """
        Construct a standardized output file path.
        
        Args:
            base_path: Base directory path
            filename: Name of the output file
            
        Returns:
            Full path to the output file
        """
        base_dir = Path(base_path)
        output_path = base_dir / filename
        
        # Ensure the directory exists
        SharedJSONFileService.ensure_output_directory(str(output_path.parent))
        
        return str(output_path)