from typing import Optional
from pydantic import BaseModel, Field

class MongoConfig(BaseModel):
    uri: str = Field(..., description="MongoDB Connection URI")
    db_name: str = Field(..., description="MongoDB Database Name")

class AmshaAppConfig(BaseModel):
    """
    Main Application Configuration for Amsha.
    Requires strict validation with no silent default fallbacks for critical paths.
    """
    backend: str = Field(..., description="Repository backend type (e.g., 'mongo', 'file')")
    domain_root_path: str = Field(..., description="Root path for domain configurations (e.g., crew_configs)")
    output_dir_path: str = Field(..., description="Path to output directory")
    
    # Optional sections depending on backend
    mongo: Optional[MongoConfig] = Field(None, description="MongoDB configuration details, required if backend is 'mongo'")
