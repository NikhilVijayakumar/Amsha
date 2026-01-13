# src/nikhil/amsha/llm_factory/domain/model/llm_output_config.py
from typing import Optional
from pydantic import BaseModel, Field


class LLMOutputConfig(BaseModel):
    """
    Configuration for LLM output file organization and naming.
    
    Attributes:
        alias: Custom alias for output filename (e.g., "azure-key1" instead of model name)
        folder_name: Custom folder name for organizing outputs
        structure: Output structure - "flat" (default) or "folder" (nested)
        display_name: Human-readable name for UI display (not used in file paths)
    """
    alias: Optional[str] = Field(None, description="Custom alias for output filename")
    folder_name: Optional[str] = Field(None, description="Custom folder for outputs")
    structure: Optional[str] = Field("flat", description="Output structure: 'flat' or 'folder'")
    display_name: Optional[str] = Field(None, description="Display name for UI only")
