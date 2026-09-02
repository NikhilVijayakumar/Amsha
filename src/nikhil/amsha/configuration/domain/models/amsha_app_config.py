from pydantic import BaseModel, Field

class AmshaAppConfig(BaseModel):
    """
    Main Application Configuration for Amsha.
    Requires strict validation with no silent default fallbacks for critical paths.
    """
    domain_root_path: str = Field(..., description="Root path for domain configurations (e.g., crew_configs)")
    output_dir_path: str = Field(..., description="Path to output directory")
