# datasheetai/database/database_manager.py

import logging
import sqlite3
import pandas as pd
from pathlib import Path

from datasheetai.config import DatabaseConfig
from datasheetai.schema_manager.schema import TableSchema
from datasheetai.exceptions import DatabaseError, DatabaseTableCreationError, DatabaseInsertionError, DatabaseConnectionError

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
    
    # ------------------------------------------------------------------
    # Connection management
    # ------------------------------------------------------------------
    
    # Establish SQLite database connection
    def connect(self) -> None:
        try:
            self.connection = sqlite3.connect(
                self.config.path, 
                timeout=self.config.timeout
            )
            logger.debug(f"Connected to database at {self.config.path}")
        except sqlite3.Error as e:
            logger.error(f"Error: Database connection error - {e}")
            raise DatabaseConnectionError(f"Could not connect to database - {e}")
        
    # Disconnect from database connection    
    def disconnect(self) -> None:
        if self.connection:
            self.connection.close()
            logger.debug("Database connection closed.")    

    # Check for active database connection
    def check_connection(self) -> sqlite3.Connection:
        if self.connection is None:
            raise DatabaseConnectionError("No active database connection. Call connect() first.")
        return self.connection

    # ------------------------------------------------------------------
    # Schema management
    # ------------------------------------------------------------------
    
    # Return a list of table names in database
    def get_table_names(self) -> list[str]:
        conn = self.check_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        logger.debug(f"Retrieved table names: {tables}")
        return tables

    # Check if a table with given name already exists
    def table_exists(self, table_name: str) -> bool:
        conn = self.check_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?;",
            (table_name,),
        )
        return cursor.fetchone() is not None

    # Create a new table from TableSchema only if table does not already exist
    def create_table(self, schema: TableSchema) -> None:
        try:
            self.connection.execute(schema.to_sql())
            self.connection.commit()
            logger.debug(f"Table '{schema.table_name}' created with columns {schema.column_names()}")
        except sqlite3.Error as e:
            logger.error(f"Error: Table creation error for '{schema.table_name}' - {e}")
            raise DatabaseTableCreationError(f"Could not create table '{schema.table_name}' - {e}")

    # Drops table from database
    def drop_table(self, table_name: str) -> None:
        try:
            self.connection.execute(f"DROP TABLE IF EXISTS {table_name};")
            self.connection.commit()
            logger.debug(f"Table '{table_name}' dropped")
        except sqlite3.Error as e:
            logger.error(f"Error: Could not drop table '{table_name}' - {e}")
            raise DatabaseError(f"Could not drop table '{table_name}' - {e}")

    # Insert data from DataFrame into specified table
    def insert_data(self, table_name: str, data: pd.DataFrame) -> int:
        try:
            data.to_sql(table_name, self.connection, if_exists='append', index=False)
            logger.debug(f"Inserted {len(data)} rows into '{table_name}'")
            return len(data)
        except Exception as e:
            logger.error(f"Error: Data insertion error for '{table_name}' - {e}")
            raise DatabaseInsertionError(f"Could not insert data into '{table_name}' - {e}")

    # Execute SQL SELECT statement and returns results as a list of dictionaries
    def execute_query(self, sql: str) -> list[dict]:
        conn = self.check_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(sql)
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            logger.debug(f"Query returned {len(rows)} rows")
            return [dict(zip(columns, row)) for row in rows]
        except sqlite3.Error as e:
            logger.error(f"Error: Query execution failed - {e}")
            raise DatabaseError(f"Query execution failed - {e}")