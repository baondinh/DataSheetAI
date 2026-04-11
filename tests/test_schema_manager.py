# tests/test_schema_manager.py

import pytest 
import pandas as pd
from pathlib import Path

from datasheetai.schema_manager.translator import SchemaTranslator
from datasheetai.schema_manager.manager import SchemaManager
from datasheetai.schema_manager.schema import TableSchema, ColumnSchema 
from datasheetai.exceptions import (
    SchemaManagerError,
    SchemaReadError, 
)

class TestSchemaManager:
    def test_schema_manager_initialization(self, schema_manager_config):
        manager = SchemaManager(schema_manager_config)
        assert manager.schema is None # hardcoded to None for testing