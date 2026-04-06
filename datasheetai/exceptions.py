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

class FileTooLargeError(DataLoaderError): 
    """Raised when provided file exceeds maximum allowed size."""
    pass

class InvalidFileError(DataLoaderError): 
    """Raised when provided file is invalid or cannot be parsed."""
    pass

class FileParseError(DataLoaderError): 
    """Raised when an error occurs during file parsing."""
    pass

#---------------------
# Database
#---------------------
class DatabaseError(DataSheetAIError): 
    """Base exception for database errors."""
    pass

class DatabaseTableCreationError(DatabaseError): 
    """Raised when an error occurs during table creation."""
    pass

class DatabaseInsertionError(DatabaseError): 
    """Raised when an error occurs during data insertion."""
    pass

class DatabaseConnectionError(DatabaseError): 
    """Raised when a connection to the database cannot be established."""
    pass
#---------------------
# Schema Manager
#---------------------
class SchemaManagerError(DataSheetAIError): 
    """Base exception for schema_manager errors."""
    pass

class SchemaReadError(SchemaManagerError): 
    """Raised when an error occurs while reading schema metadata."""
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

