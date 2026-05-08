# datasheetai/query_service/query_service.py

import logging

from datasheetai.config import AppConfig
from datasheetai.database.database_manager import DatabaseManager
from datasheetai.schema_manager.manager import SchemaManager
from datasheetai.llm_adapter.adapter import LLMAdapter
from datasheetai.sql_validator.validator import SQLValidator
from datasheetai.exceptions import QueryServiceError

logger = logging.getLogger(__name__)

# Orchestrates Flow 2 for converting a natural language query to SQL and getting database results
class QueryService:
    """
    Sequence:
      1. Open database connection
      2. Read all table schemas from the database
      3. Pass schemas and natural language query to LLMAdapter to get a validated SQL SELECT statement
      4. Execute the SQL against database and return results as a list of dictionaries 

    Used by:
        datasheetai/cli/commands/query.py
    """

    def __init__(self, config: AppConfig) -> None:
        self.config = config
        validator = SQLValidator()
        self._adapter = LLMAdapter(config=config.llm, validator=validator)
        self._schema_manager = SchemaManager(config.schema_manager)

    # Translate a natural language query and execute against database
    def execute(self, natural_language: str) -> list[dict]:
        with DatabaseManager(self.config.database) as db:
            table_names = db.get_table_names()

            if not table_names:
                raise QueryServiceError(
                    "No tables found in the database. "
                    "Load data first using the ingest command."
                )

            schemas = [
                self._schema_manager.read_database_schema(db.connection, name)
                for name in table_names
            ]

            logger.info(f"Querying across {len(schemas)} table(s): {table_names}")

            sql = self._adapter.translate(natural_language, schemas)
            results = db.execute_query(sql)

            logger.info(f"Query returned {len(results)} row(s)")
            return results
