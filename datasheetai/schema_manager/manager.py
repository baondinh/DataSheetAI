# datasheetai/schema_manager/manager.py

import logging
import pandas as pd
import sqlite3

from datasheetai.config import SchemaManagerConfig
from datasheetai.schema_manager.schema import TableSchema, ColumnSchema 
from datasheetai.schema_manager.translator import SchemaTranslator
from datasheetai.exceptions import SchemaManagerError

logger = logging.getLogger(__name__)

class SchemaManager:
    def __init__(self, config: SchemaManagerConfig) -> None:
        self.config = config
        self.schema: TableSchema | None = None
        self.translator = SchemaTranslator() # ScehmaTranslator object only has one function and does not need config

    def translate_schema(self, df: pd.DataFrame, table_name: str) -> TableSchema:
        return self.translator.translate(df, table_name)
    
    # Database manager can read schema, but want to keep modules separate and also allow schema manager to read 
    def read_database_schema(self,
                             connection: sqlite3.Connection,
                             table_name: str) -> TableSchema:
        # Read column names and types from live database using SQLite PRAGMA
        try:
            schema_info = connection.execute(f"PRAGMA table_info({table_name})").fetchall()
            columns = []
            for row in schema_info: 
                column_name = row[1] # second column is name
                sqlite_dtype = row[2] # third column is type
                columns.append(ColumnSchema(
                    column_name=column_name, 
                    sqlite_dtype=sqlite_dtype
                ))
            return TableSchema(table_name=table_name, columns=columns)
        except Exception as e:
            logger.error(f"Error reading database schema for table '{table_name}': {e}")
            raise SchemaManagerError(f"Error reading database schema for table '{table_name}': {e}")