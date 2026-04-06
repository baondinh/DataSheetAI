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
        column_defs = ", ".join(
            [f"{column.column_name} {column.sqlite_dtype}" 
             for column in self.columns]
        )
        return f"CREATE TABLE IF NOT EXISTS {self.table_name} ({column_defs});"
    
    def column_names(self) -> List[str]: 
        return [column.column_name for column in self.columns]