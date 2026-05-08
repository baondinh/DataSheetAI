# datasheetai/database/database_manager.py

import logging
import sqlite3
import pandas as pd
from pathlib import Path

from datasheetai.config import DatabaseConfig
from datasheetai.schema_manager.schema import TableSchema
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
        self.connection: sqlite3.Connection | None = None

    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.disconnect()
        return False 

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

    def table_exists(self, table_name: str) -> bool:
        """Returns True if a table with the given name exists in the database."""
        conn = self.check_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?;",
            (table_name,),
        )
        return cursor.fetchone() is not None

    def create_table(self, schema: TableSchema) -> None:
        """Creates a new table from a TableSchema. No-op if the table already exists."""
        try:
            self.connection.execute(schema.to_sql())
            self.connection.commit()
            logger.debug(f"Table '{schema.table_name}' created with columns {schema.column_names()}")
        except sqlite3.Error as e:
            logger.error(f"Error: Table creation error for '{schema.table_name}' - {e}")
            raise DatabaseTableCreationError(f"Could not create table '{schema.table_name}' - {e}")

    def drop_table(self, table_name: str) -> None:
        """Drops a table from the database."""
        try:
            self.connection.execute(f"DROP TABLE IF EXISTS {table_name};")
            self.connection.commit()
            logger.debug(f"Table '{table_name}' dropped")
        except sqlite3.Error as e:
            logger.error(f"Error: Could not drop table '{table_name}' - {e}")
            raise DatabaseTableCreationError(f"Could not drop table '{table_name}' - {e}")

    def insert_data(self, table_name: str, data: pd.DataFrame) -> int:
        """Inserts data from a DataFrame into the specified table. Returns row count inserted."""
        try:
            data.to_sql(table_name, self.connection, if_exists='append', index=False)
            logger.debug(f"Inserted {len(data)} rows into '{table_name}'")
            return len(data)
        except Exception as e:
            logger.error(f"Error: Data insertion error for '{table_name}' - {e}")
            raise DatabaseInsertionError(f"Could not insert data into '{table_name}' - {e}")

    def execute_query(self, sql: str) -> list[dict]:
        """Executes a SELECT statement and returns results as a list of dicts."""
        conn = self.check_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(sql)
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            logger.debug(f"Query returned {len(rows)} rows")
            return [dict(zip(columns, row)) for row in rows]
        except sqlite3.Error as e:
            logger.error(f"Error executing query - {e}")
            raise DatabaseInsertionError(f"Query execution failed - {e}")