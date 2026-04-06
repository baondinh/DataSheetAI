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
        self.parser = DataParser(config)

    def load(self, file_path: str) -> pd.DataFrame: 
        logger.info(f"Loading data from {file_path}")

        # Validate file
        validated_path = self.validator.validate(file_path)

        # Check file extension and select appropriate reader
        ext = validated_path.suffix.lower()
        # ext = self.config.supported_extensions[ext]

        if ext not in self.config.supported_extensions:
            raise UnsupportedFileTypeError(f"File type '{ext}' is not supported.")

        try: 
            if ext == ".csv":
                logger.debug(f"Using CSV parser for file: {validated_path}")
                df = self.parser.parse_csv(validated_path)
            # elif ext == ".json":
            #     logger.debug(f"Using JSON parser for file: {validated_path}")
            #     df = self.parser.parse_json(validated_path)
            # elif ext == ".xlsx":
            #     logger.debug(f"Using Excel parser for file: {validated_path}")   
            #     df = self.parser.parse_excel(validated_path)
            else:
                logger.error(f"Error: Unexpected error parsing {ext}")
                raise UnsupportedFileTypeError(f"File type '{ext}' is not supported.")
            return df
        except Exception as e:
            logger.error(f"Error: Could not load {validated_path} - {e}")
            raise e