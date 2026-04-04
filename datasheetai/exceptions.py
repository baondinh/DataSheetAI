# datasheetai/exceptions.py

#---------------------
# Base
#---------------------
class DatasheetAIError(Exception):
    """Root exception."""

#---------------------
# Data Loader
#---------------------
class DataLoaderError(DatasheetAIError): 
    """Base exception for data_loader errors."""
    pass

class FileNotFoundError(DataLoaderError): 
    pass

#---------------------
# LLM Adapter
#---------------------
class LLMAdapterError(DatasheetAIError): 
    """Base exception for llm_adapter errors."""
    pass

#---------------------
# Query Service
#---------------------
class QueryServiceError(DatasheetAIError): 
    """Base exception for query_service errors."""
    pass

#---------------------
# SQL Validator
#---------------------
class SQLValidatorError(DatasheetAIError): 
    """Base exception for sql_validator errors."""
    pass

#---------------------
# CLI
#---------------------
class CLIError(Exception): 
    """Base exception for cli errors."""
    pass

