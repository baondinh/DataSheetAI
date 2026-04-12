# datasheetai/schema_manager/manager.py

import logging
import pandas as pd
import sqlite3

from datasheetai.config import SchemaManagerConfig, DatabaseConfig
# from datasheetai.database.database_manager import DatabaseManager # Aim to keep modules separated
from datasheetai.schema_manager.schema import TableSchema, ColumnSchema 
from datasheetai.schema_manager.translator import SchemaTranslator
from datasheetai.exceptions import SchemaManagerError, SchemaTranslationError

logger = logging.getLogger(__name__)

class SchemaManager:
    def __init__(self, config: SchemaManagerConfig) -> None:
        self.config = config
        self.translator = SchemaTranslator() # This object only has one function handling translation logic and does not need config

    def translate_schema(self, df: pd.DataFrame, table_name: str) -> TableSchema:
        return self.translator.translate(df, table_name)
    
    # Although database manager is able to read schema, want to keep modules separate and also allow schema manager to read 
    def read_database_schema(self, 
                             connection: sqlite3.Connection, 
                             table_name: str) -> TableSchema:
        # Attempt to connect to database
        try: 
            cursor = connection.execute
        except Exception as e:
            logger.error(f"Error: Unable to connect to database - {e}")
            raise SchemaManagerError(f"Error: Unable to connect to database - {e}")

        try:
            schema_info = connection.execute(f"PRAGMA table_info({table_name})").fetchall()
            columns = []
            for column_name, sqlite_dtype in schema_info:
                columns.append(ColumnSchema(
                    column_name=column_name, 
                    sqlite_dtype=sqlite_dtype
                ))
            return TableSchema(table_name=table_name, columns=columns)
        except Exception as e:
            logger.error(f"Error reading database schema for table '{table_name}': {e}")
            raise SchemaManagerError(f"Error reading database schema for table '{table_name}': {e}")