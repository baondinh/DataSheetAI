# datasheetai/csv_loader/exceptions.py

class DataLoaderError(Exception): 
    """Base exception for csv_loader errors."""
    pass

class FileNotFoundError(DataLoaderError): 
    pass
