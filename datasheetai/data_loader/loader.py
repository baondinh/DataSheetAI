# datasheetai/data_loader/loader.py

import logging
import pandas as pd

from datasheetai.config import DataLoaderConfig
from datasheetai.data_loader.file_validator import FileValidator
from datasheetai.data_loader.parser import DataParser
from datasheetai.exceptions import UnsupportedFileTypeError

logger = logging.getLogger(__name__)

class DataLoader: 
    def __init__(self, config: DataLoaderConfig) -> None: 
        self.config = config
        self.validator = FileValidator(config)

    def load(self, file_path: str) -> pd.DataFrame: 
        logger.info(f"Loading data from {file_path}")
        # Validate file
        self.validator.validate(file_path)

        return