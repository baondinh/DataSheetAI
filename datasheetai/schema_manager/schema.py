# datasheetai/schema_manager/schema.py

from dataclasses import dataclass, field
from typing import List

@dataclass
class ColumnSchema: 
    column_name: str
    sqlite_dtype: str
    
@dataclass
class TableSchema: 
    table_name: str
    columns: List[ColumnSchema] = field(default_factory=list)

    def to_sql(self) -> str:
        # Double quote identifiers to handle spaces and other special characters
        column_defs = ", ".join(
            [f'"{column.column_name}" {column.sqlite_dtype}'
             for column in self.columns]
        )
        return f'CREATE TABLE IF NOT EXISTS "{self.table_name}" ({column_defs});'
    
    def column_names(self) -> List[str]: 
        return [column.column_name for column in self.columns]
    
    def matches(self, other: 'TableSchema') -> bool:
        # check length of columns for quick mismatch
        if len(self.columns) != len(other.columns):
            return False
        # check column names and types
        for col1, col2 in zip(self.columns, other.columns):
            if ((col1.column_name != col2.column_name) or 
                (col1.sqlite_dtype != col2.sqlite_dtype)):
                return False
        return True