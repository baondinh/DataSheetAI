# datasheetai/config.py

import logging 
from datetime import datetime
from dataclasses import field
from typing import Literal, Dict
from pathlib import Path 

import yaml
# from datasheetai.logging_config import LoggingConfig

logger = logging.getLogger(__name__)

#---------------------
# Database
#---------------------
# class DatabaseConfig: 
#     """
#     Controls where SQLite .db lives
#     Used by: 
#         datasheetai/db/connection.py -> DatabaseConnection
#     """
#     path: str = "data/datasheetai.db"
#     echo: bool = False 

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
    # supported_extensions: list[str] = field(default_factory=lambda: [".csv"])
    supported_extensions: Dict[str, str] = field(default_factory=lambda: {
        ".csv":     "csv",
        # ".json":    "json",
        # ".xlsx":    "excel",
    })
    default_encoding: str = "utf-8"
    max_file_size_mb: int = 100
    infer_headers: bool = True
    data_dir: str = "data"
    infer_types: bool = True # if False, columns loaded as text
    skip_blank_rows: bool = True

#---------------------
# Schema Manager
#---------------------
# class SchemaManagerConfig: 
#     """
#     Controls how schema metadata is read and formatted before being passed to LLM
#     Used by: 
#         datasheetai/schema_manager/manager.py -> SchemaManager
#         datasheetai/llm_adapter/adapter.py -> LLMAdapter
#     """
#     include_row_counts: bool = True # includes row count in schema count
#     include_sample_rows: int = 3    # rows sent to LLM -> 0 to disable

#---------------------
# LLM 
#---------------------
# class LLMConfig: 
#     """
#     Controls LLM provider + model used to translate natural language to SQL
#     Used by: 
#         datasheetai/llm_adapter/adapter.py -> LLMAdapter
#     """
#     provider: Literal["anthropic", "openai"] = "anthropic"
#     model: str = "claude-sonnet-4-20250514"
#     max_takens: int = 1000
#     timeout_seconds: int = 30
#     api_key_env_var: str = "ANTHROPIC_API_KEY"

#---------------------
# Query Service 
#---------------------
# class QueryServiceConfig: 
#     """
#     Control logic between CLI and LLM + database layers
#     Used by: 
#         datasheetai/query_service/service.py -> QueryService
#         datasheetai/validator/sql_validator.py -> SQLValidator
#     """
#     max_retries: int = 2
#     allow_write_queries: bool = False # Should not be able to INSERT/UPDATE/DROP
#     max_rows_returned: int = 200

#---------------------
# Logging 
#---------------------
# class LoggingConfig: 
#     """
#     Controls logging and output file 
#     Used by: 
#         datasheetai/logging_config.py -> setup_logging()
#     """
#     level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
#     file: str = f"logs/{datetime.now()}_datasheetai.log"
#     max_bytes: int = 1_000_000
class LoggingConfig:
    level: str = "DEBUG"
    log_dir: str = "logs"
    log_file: str = "datasheetai"
    max_bytes: int = 5_242_880  # 5 MB
    backup_count: int = 3
    format: str = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    date_format: str = "%Y-%m-%d %H:%M:%S"


#---------------------
# AppConfig 
#---------------------
class AppConfig: 
    """
    Root configuration object that CLI and tests instantiate directly
    Other config dataclasses are accessed as attributes through this object
    """
    logging:        LoggingConfig       = field(default_factory=LoggingConfig)
    data_loader:    DataLoaderConfig    = field(default_factory=DataLoaderConfig)
    # database:       DatabaseConfig      =field()
    # schema_manger:  SchemaManagerConfig =field()
    # llm:            LLMConfig           =field()
    # query_service:  QueryServiceConfig  =field()

def load_config(config_path: str | Path = "config.yaml") -> AppConfig:
    """
    Load config from YAML file and return AppConfig object
    """
    with open(config_path, "r") as f:
        config_dict = yaml.safe_load(f)

    # Convert nested dict to AppConfig dataclass
    app_config = AppConfig(
        logging=LoggingConfig(**config_dict.get("logging", {})),
        data_loader=DataLoaderConfig(**config_dict.get("data_loader", {})),
        # database=DatabaseConfig(**config_dict.get("database", {})),
        # schema_manger=SchemaManagerConfig(**config_dict.get("schema_manager", {})),
        # llm=LLMConfig(**config_dict.get("llm", {})),
        # query_service=QueryServiceConfig(**config_dict.get("query_service", {})),
    )

    logger.debug(f"Loaded config: {app_config}")
    return app_config