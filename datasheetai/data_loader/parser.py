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

from typing import Any 
import logging
import pandas as pd
from datasheetai.exceptions import FileNotFoundError

class DataParser: 
    def parse(self, 
              filepath: str, 
              logger: logging.Logger): 
        df = pd.DataFrame()
        try: 
            df = pd.read_csv(filepath)
            logger.info("Success: Data parsed.")
        except Exception as e: 
            logger.error(f"Error: Unable to parse data from {filepath} - {e}")
            return "Work in progress"