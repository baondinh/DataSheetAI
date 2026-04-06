# datasheetai/data_loader/parser.py

import logging
import pandas as pd

from datasheetai.config import DataLoaderConfig
from datasheetai.exceptions import FileParseError

logger = logging.getLogger(__name__)

class DataParser: 
    def __init__(self, config: DataLoaderConfig) -> None: 
        self.config = config

    def parse_csv(self, file_path: str) -> pd.DataFrame: 
        try: 
            df = pd.read_csv(
                file_path, 
                encoding = self.config.default_encoding,
                header = 0 if self.config.infer_headers else None,
            )
            logger.info(f"Success: Data parsed from {file_path}")
        except Exception as e: 
            logger.error(f"Error: Unable to parse data from {file_path} - {e}")
            raise FileParseError(f"Error: Unable to parse data from {file_path} - {e}")
        
        logger.info(f"DataFrame shape: {df.shape}")
        return df
    
    # TODO: Implement parsing methods for other file types (.json, .xlsx, etc.)