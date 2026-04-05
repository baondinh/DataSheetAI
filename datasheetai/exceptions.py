# datasheetai/exceptions.py

#---------------------
# Base
#---------------------
class DataSheetAIError(Exception):
    """Root exception for all DataSheetAI errors."""

#---------------------
# Data Loader
#---------------------
class DataLoaderError(DataSheetAIError): 
    """Base exception for data_loader errors."""
    pass

class FileNotFoundError(DataLoaderError): 
    """Raised when a specified file cannot be found."""
    pass

class UnsupportedFileTypeError(DataLoaderError): 
    """Raised when provided file has an unsupported extension."""
    pass

#---------------------
# LLM Adapter
#---------------------
class LLMAdapterError(DataSheetAIError): 
    """Base exception for llm_adapter errors."""
    pass

#---------------------
# Query Service
#---------------------
class QueryServiceError(DataSheetAIError): 
    """Base exception for query_service errors."""
    pass

#---------------------
# SQL Validator
#---------------------
class SQLValidatorError(DataSheetAIError): 
    """Base exception for sql_validator errors."""
    pass

#---------------------
# CLI
#---------------------
class CLIError(DataSheetAIError): 
    """Base exception for cli errors."""
    pass

