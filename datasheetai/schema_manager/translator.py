# datasheetai/schema_manager/translator.py

import logging
import pandas as pd

from datasheetai.database.database_manager import DatabaseManager
from datasheetai.exceptions import DatabaseInsertionError

class SchemaTranslator:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager