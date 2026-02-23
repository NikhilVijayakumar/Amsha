import logging
import os
from pathlib import Path
from nibandha.configuration.domain.models.export_config import ExportConfig
from nibandha.export.application.export_service import ExportService

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("amsha.export")

def export_paper():
    """Export the paper using the new combined export feature from Nibandha."""
    
    # 1. Base paths
    base_docs_dir = Path("/home/dell/PycharmProjects/Amsha/docs/paper")
    
    # Track target directories that actually contain .md files
    target_dirs = set()
    for root, _, files in os.walk(base_docs_dir):
        if any(f.endswith('.md') for f in files):
            target_dirs.add(Path(root))
            
    if not target_dirs:
        logger.warning(f"No markdown files found in {base_docs_dir} or any of its subdirectories.")
        return

    logger.info(f"Found {len(target_dirs)} directories containing markdown files.")

    # Iterate over each discovered directory and export
    for target_dir in target_dirs:
        output_dir = target_dir / "exports"
        
        config = ExportConfig(
            formats=["html", "docx"],
            style="default", # Or "professional"
            input_dir=target_dir,
            output_dir=output_dir
        )
        
        logger.info(f"\n--- Starting combined export for directory: {target_dir} ---")
        
        # 2. Initialize Service
        try:
            service = ExportService(config)
            
            # 3. Export all as one document
            generated_files = service.export_combined()
            
            if generated_files:
                 for file in generated_files:
                     logger.info(f"Successfully generated: {file}")
            else:
                 logger.warning(f"Export service ran but no files were generated for {target_dir}")
                
        except Exception as e:
            logger.error(f"Failed to export directory {target_dir}: {e}")

if __name__ == "__main__":
    export_paper()
