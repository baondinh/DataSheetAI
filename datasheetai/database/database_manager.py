# datasheetai/database/database_manager.py

import logging
import sqlite3
import pandas as pd
from pathlib import Path

from datasheetai.config import DatabaseConfig
from datasheetai.exceptions import DatabaseTableCreationError, DatabaseInsertionError, DatabaseConnectionError

logger = logging.getLogger(__name__)

class DatabaseManager:
    """
    Manages interactions with SQLite database, including table creation and data insertion.
    Used by: 
        datasheetai/data_loader/loader.py -> DataLoader
        datasheetai/schema_manager/manager.py -> SchemaManager
    """

    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.connection = sqlite3.Connection | None = None

    # Connection management
    def connect(self) -> None:
        """Establishes a connection to the SQLite database."""
        try:
            self.connection = sqlite3.connect(
                self.config.path, 
                timeout=self.config.timeout
            )
            logger.debug(f"Connected to database at {self.config.path}")
        except sqlite3.Error as e:
            logger.error(f"Error: Database connection error - {e}")
            raise DatabaseConnectionError(f"Could not connect to database - {e}")
        
    def disconnect(self) -> None:
        """Disconnects from the database connection."""
        if self.connection:
            self.connection.close()
            logger.debug("Database connection closed.")    

    def check_connection(self) -> sqlite3.Connection:
        """Checks active database connection, connecting if not already connected."""
        if self.connection is None:
            raise DatabaseConnectionError("No active database connection. Call connect() first.")
        return self.connection

    # Schema management
    def get_table_names(self) -> list[str]:
        """Returns a list of all table names in the database."""
        conn = self.check_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        logger.debug(f"Retrieved table names: {tables}")
        return tables

    def create_table(self, table_name: str, columns: dict) -> None:
        """Creates a new table in the database with the specified columns."""
        try:
            column_defs = ", ".join([f"{col} {dtype}" for col, dtype in columns.items()])
            create_stmt = f"CREATE TABLE IF NOT EXISTS {table_name} ({column_defs});"
            self.connection.execute(create_stmt)
            self.connection.commit()
            logger.debug(f"Success: Table '{table_name}' created with columns [{', '.join(columns.keys())}]")
        except sqlite3.Error as e:
            logger.error(f"Error: Table creation error for '{table_name}' - {e}")
            raise DatabaseTableCreationError(f"Could not create table '{table_name}' - {e}")

    def insert_data(self, table_name: str, data: pd.DataFrame):
        """Inserts data from a DataFrame into the specified table."""
        try:
            data.to_sql(table_name, self.connection, if_exists='append', index=False)
            logger.debug(f"Success: Inserted {len(data)} rows into '{table_name}'")
        except Exception as e:
            logger.error(f"Error: Data insertion error for '{table_name}' - {e}")
            raise DatabaseInsertionError(f"Could not insert data into '{table_name}' - {e}")