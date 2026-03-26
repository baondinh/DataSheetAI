# datasheetai/csv_loader/exceptions.py

class CSVLoaderError(Exception): 
    """Base exception for csv_loader errors."""
    pass

class FileNotFoundError(CSVLoaderError): 
    pass
