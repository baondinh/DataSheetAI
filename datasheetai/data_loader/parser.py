# datasheetai/data_loader/parser.py

'''
Reading a provided CSV and inspecting data
Cannot use df.to_sql() -> Must implement schema creation and data insertion logic independently

Activities:
Manually create a table in SQLite.
Use pandas.read_csv() to load data.
Insert data into  SQLite
Run basic queries using sqlite3 or DB browser.

'''
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