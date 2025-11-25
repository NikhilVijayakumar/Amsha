"""
Configuration management for AI Code Audit
"""

import os
from pathlib import Path
from typing import Optional
from dataclasses import dataclass


@dataclass
class AuditConfig:
    """Configuration for AI code audit"""
    
    rules_file: Optional[Path] = None
    llm_config_path: Optional[Path] = None
    dependencies_file: Optional[Path] = None
    skip_audit: bool = False
    max_tokens_per_chunk: int = 14000
    
    @classmethod
    def from_cli_args(cls, args) -> "AuditConfig":
        """Create config from command-line arguments"""
        return cls(
            rules_file=Path(args.rules) if args.rules else None,
            llm_config_path=Path(args.config) if args.config else None,
            dependencies_file=Path(args.dependencies) if args.dependencies else None,
            skip_audit=args.skip,
            max_tokens_per_chunk=args.max_tokens
        )
    
    @classmethod
    def from_environment(cls) -> "AuditConfig":
        """Create config from environment variables"""
        return cls(
            rules_file=Path(os.environ['AMSHA_RULES_FILE']) if 'AMSHA_RULES_FILE' in os.environ else None,
            llm_config_path=Path(os.environ['AMSHA_LLM_CONFIG']) if 'AMSHA_LLM_CONFIG' in os.environ else None,
            dependencies_file=Path(os.environ['AMSHA_DEPENDENCIES_FILE']) if 'AMSHA_DEPENDENCIES_FILE' in os.environ else None,
            skip_audit=os.environ.get('SKIP_AI_AUDIT', '0') == '1',
        )


def find_config_file(filename: str, start_dir: Optional[Path] = None) -> Optional[Path]:
    """
    Search for configuration file in priority order:
    1. Current directory
    2. config/ subdirectory
    3. Parent directories (up to 3 levels)
    4. Home directory ~/.amsha/
    5. Package default
    """
    start_dir = start_dir or Path.cwd()
    
    # 1. Current directory
    if (start_dir / filename).exists():
        return start_dir / filename
    
    # 2. config/ subdirectory
    if (start_dir / "config" / filename).exists():
        return start_dir / "config" / filename
    
    # 3. Parent directories (up to 3 levels)
    current = start_dir
    for _ in range(3):
        current = current.parent
        if (current / filename).exists():
            return current / filename
        if (current / "config" / filename).exists():
            return current / "config" / filename
    
    # 4. Home directory
    home_config = Path.home() / ".amsha" / filename
    if home_config.exists():
        return home_config
    
    # 5. Package default (if it's a template)
    if filename.endswith('.md'):
        package_default = Path(__file__).parent / "templates" / filename
        if package_default.exists():
            return package_default
    
    return None


def resolve_config(config: AuditConfig) -> AuditConfig:
    """
    Resolve configuration by finding files if not explicitly set
    """
    # Find rules file
    if not config.rules_file:
        rules = find_config_file("AGENTS.md")
        if not rules:
            # Try alternative names
            rules = find_config_file("ARCHITECTURE.md") or find_config_file("RULES.md")
        config.rules_file = rules
    
    # Find LLM config
    if not config.llm_config_path:
        config.llm_config_path = find_config_file("llm_config.yaml")
    
    # Find dependencies file
    if not config.dependencies_file:
        config.dependencies_file = find_config_file("DEPENDENCIES.md")
    
    return config
