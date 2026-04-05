# datasheetai/data_loader/loader.py

import logging
import pandas as pd
from datasheetai.config import DataLoaderConfig

logger = logging.getLogger(__name__)

class DataLoader: 
    def __init__(self, config: DataLoaderConfig) -> None: 
        self.config = config

    def load(self, file_path: str) -> pd.DataFrame: 
        logger.info(f"Loading data from {file_path}")
        # Check file extension
        ext = file_path.split(".")[-1].lower()
        if f".{ext}" not in self.config.supported_extensions:
            raise ValueError(f"Unsupported file extension: .{ext}")

        # Load CSV with pandas
        df = pd.read_csv(file_path)

        # Optionally skip blank rows
        if self.config.skip_blank_rows:
            df.dropna(how="all", inplace=True)

        # Optionally infer types (pandas does this by default)
        if not self.config.infer_types:
            df = df.astype(str)

        return df