import pandas as pd

from datasheetai.config import DataLoaderConfig
from datasheetai.data_loader.file_validator import FileValidator

def config(): 
    return DataLoaderConfig()

def test_load_file(): 
    config = DataLoaderConfig()
    validator = FileValidator(config)
    validator.validate("data/sample_data.csv")
    assert True