# datasheetai/schema_manager/manager.py

import logging
import pandas as pd

from datasheetai.config import SchemaManagerConfig
from datasheetai.schema_manager.schema import TableSchema, ColumnSchema 
# TODO: create exceptions for schema 

logger = logging.getLogger(__name__)

class SchemaManager:
    def __init__(self):
        self.schema = None