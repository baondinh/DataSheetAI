# tests/test_data_loader.py

import pytest 
from pathlib import Path

from datasheetai.config import DataLoaderConfig
from datasheetai.data_loader.file_validator import FileValidator
from datasheetai.exceptions import (
    FileNotFoundError,
    UnsupportedFileTypeError, 
    FileTooLargeError, 
    InvalidFileError
)
class TestDataLoaderValidator:
    def test_validate_valid_path(self, data_loader_config, sample_csv):
        validator = FileValidator(data_loader_config)
        validated_path = validator.validate(str(sample_csv))
        assert isinstance(validated_path, Path)

    def test_validate_nonexistent_file(self, data_loader_config):
        validator = FileValidator(data_loader_config)
        with pytest.raises(FileNotFoundError):
            validator.validate("/nonexistent/file.csv")

    def test_validate_valid_csv(self, data_loader_config, sample_csv):
        validator = FileValidator(data_loader_config)
        validated_path = validator.validate(str(sample_csv))
        assert isinstance(validated_path, Path)
        assert validated_path.suffix == ".csv"

    def test_validate_unsupported_extension(self, data_loader_config, invalid_file):
        validator = FileValidator(data_loader_config)
        with pytest.raises(UnsupportedFileTypeError):
            validator.validate(str(invalid_file))

# def config(): 
#     return DataLoaderConfig()

# def test_load_file(): 
#     config = DataLoaderConfig()
#     validator = FileValidator(config)
#     validator.validate("data/sample_data.csv")
#     assert True