# datasheetai/data_loader/file_validator.py

import logging
from pathlib import Path

from datasheetai.config import DataLoaderConfig
from datasheetai.exceptions import FileNotFoundError, UnsupportedFileTypeError

logger = logging.getLogger(__name__)

class FileValidator: 
    def __init__(self, config: DataLoaderConfig) -> None: 
        self.config = config

    def validate(self, file_path: str) -> bool: 
        logger.info(f"Validating file: {file_path}")

        path = Path(file_path)

        # Check if file exists and is a file
        if not path.exists(): 
            raise FileNotFoundError(f"Error: File not found - {file_path}")
        
        if not path.is_file(): 
            raise ValueError(f"Error: Path is not a file - {file_path}")

        # Check file extension
        ext = path.suffix.lower()
        if ext not in self.config.supported_extensions:
            raise UnsupportedFileTypeError(
                f"Error: Unsupported file extension - {ext}"
                f"Supported extensions: {list(self.config.supported_extensions.keys())}"                
            )

        return True