# datasheetai/schema_manager/translator.py

import logging
import pandas as pd

# from datasheetai.database.database_manager import DatabaseManager # Translator itself should not access database directly
from datasheetai.schema_manager.schema import TableSchema, ColumnSchema
from datasheetai.exceptions import SchemaTranslationError

logger = logging.getLogger(__name__)

# TODO: add more complex types and nullable handling
# DATATYPE_MAPPING = {
#     'int64': 'INTEGER',
#     'float64': 'REAL',
#     'object': 'TEXT'
# }

class SchemaTranslator:
    def translate(self, df: pd.DataFrame, table_name: str) -> TableSchema:
        # Check for empty df 
        if df.empty:
            logger.error(f"Error: Empty DataFrame - cannot translate {table_name} schema.")
            return TableSchema(table_name=table_name, columns=[])

        try:
            columns = []
            for column_name, dtype in df.dtypes.items():
                # TODO: improve type mapping logic
                if pd.api.types.is_integer_dtype(dtype):
                    sqlite_dtype = "INTEGER"
                elif pd.api.types.is_float_dtype(dtype):
                    sqlite_dtype = "REAL"
                elif pd.api.types.is_string_dtype(dtype):
                    sqlite_dtype = "TEXT"
                else:
                    raise SchemaTranslationError(
                        f"Error: Unsupported data type for column '{column_name}': {dtype}"
                    )
                columns.append(ColumnSchema(
                    column_name=column_name, 
                    sqlite_dtype=sqlite_dtype
                ))
            return TableSchema(table_name=table_name, columns=columns)
        except Exception as e:
            logger.error(f"Error: Unable to translate DataFrame to TableSchema - {e}")
            raise SchemaTranslationError(f"Error: Unable to translate DataFrame to TableSchema - {e}")