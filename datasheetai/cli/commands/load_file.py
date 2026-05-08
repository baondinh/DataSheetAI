# datasheetai/cli/commands/load_file.py

import logging
import pandas as pd

from datasheetai.config import AppConfig
from datasheetai.data_loader.loader import DataLoader
from datasheetai.schema_manager.manager import SchemaManager
from datasheetai.schema_manager.schema import TableSchema, ColumnSchema
from datasheetai.database.database_manager import DatabaseManager

logger = logging.getLogger(__name__)

def ingest_file(path: str, 
                table_name: str, 
                config: AppConfig, 
                overwrite: bool = False):
    # 1) DataLoader handles file validation and parsing, returns DataFrame
    logger.info(f"Starting ingestion for file: {path} into table: {table_name}")
    loader = DataLoader(config.data_loader)
    df = loader.load(file_path=path)

    # 2) SchemaManager handles schema inference and database schema reading
    sch_manager = SchemaManager(config.schema_manager) # var name needs to be different from config var
    incoming = sch_manager.translate_schema(df=df, table_name=table_name)

    # 3) DatabaseManager handles database interactions (checking table existence, creating tables, inserting data)
    with DatabaseManager(config.database) as db:   # owns the connection
        db.connect() # connection is established here
        db.disconnect()   # connection is disconnected here
        # if not db.table_exists(table_name):
        #     db.create_table(incoming)
        #     rows = db.insert_dataframe(df, incoming)
        #     return _result("created", table_name, rows)

    #     existing = schema_manager.read_from_db(db.connection, table_name)

    #     if incoming.matches(existing):
    #         rows = db.insert_dataframe(df, existing)
    #         return _result("appended", table_name, rows)

    #     if overwrite:
    #         db.drop_table(table_name)
    #         db.create_table(incoming)
    #         rows = db.insert_dataframe(df, incoming)
    #         return _result("overwritten", table_name, rows)

    #     schema_manager.assert_compatible(incoming, existing)