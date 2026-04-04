# datasheetai/config.py

import logging 
from datetime import datetime
from dataclasses import field
from typing import Literal
from pathlib import Path 
# import yaml

logger = logging.getLogger(__name__)


#---------------------
# Database
#---------------------
class DatabaseConfig: 
    """
    Controls where SQLite .db lives
    Used by: 
        datasheetai/db/connection.py -> DatabaseConnection
    """
    path: str = "data/datasheetai.db"
    echo: bool = False 

#---------------------
# Data Loder
#---------------------
class DataLoaderConfig: 
    """
    Controls how data files are parsed and written to database
    Used by: 
        datasheetai/data_loader/loader.py -> DataLoader
        datasheetai/data_loader/parser.py -> Parser
        datasheetai/db/initializer.py -> DatabaseInitializer

    """
    supported_extensions: list[str] = field(default_factory=lambda: [".csv"])
    infer_types: bool = True # if False, columns loaded as text
    skip_blank_rows: bool = True

#---------------------
# Schema Manager
#---------------------
class SchemaManagerConfig: 
    """
    Controls how schema metadata is read and formatted before being passed to LLM
    Used by: 
        datasheetai/schema_manager/manager.py -> SchemaManager
        datasheetai/llm_adapter/adapter.py -> LLMAdapter
    """
    include_row_counts: bool = True # includes row count in schema count
    include_sample_rows: int = 3    # rows sent to LLM -> 0 to disable

#---------------------
# LLM 
#---------------------
class LLMConfig: 
    """
    Controls LLM provider + model used to translate natural language to SQL
    Used by: 
        datasheetai/llm_adapter/adapter.py -> LLMAdapter
    """
    provider: Literal["anthropic", "openai"] = "anthropic"
    model: str = "claude-sonnet-4-20250514"
    max_takens: int = 1000
    timeout_seconds: int = 30
    api_key_env_var: str = "ANTHROPIC_API_KEY"

#---------------------
# Query Service 
#---------------------
class QueryServiceConfig: 
    """
    Control logic between CLI and LLM + database layers
    Used by: 
        datasheetai/query_service/service.py -> QueryService
        datasheetai/validator/sql_validator.py -> SQLValidator
    """
    max_retries: int = 2
    allow_write_queries: bool = False # Should not be able to INSERT/UPDATE/DROP
    max_rows_returned: int = 200

#---------------------
# Logging 
#---------------------
class LoggingConfig: 
    """
    Controls logging and output file 
    Used by: 
        datasheetai/logging_config.py -> setup_logging()
    """
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    file: str = f"logs/{datetime.now()}_datasheetai.log"
    max_bytes: int = 1_000_000

#---------------------
# AppConfig 
#---------------------
class LLMConfig: 
    """
    Root configuration object that CLI and tests instantiate directly
    Other config dataclasses are accessed as attributes through this object
    """
    database:       DatabaseConfig      =field()
    data_loader:    DataLoaderConfig    =field() 
    schema_manger:  SchemaManagerConfig =field()
    llm:            LLMConfig           =field()
    query_service:  QueryServiceConfig  =field()
    logging:        LoggingConfig       =field()