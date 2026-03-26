# datasheetai/config.py

import logging 
from pathlib import Path 

logger = logging.getLogger(__name__)

class SQLiteConfig: 
    path: str = "data/datasheetai.db"
