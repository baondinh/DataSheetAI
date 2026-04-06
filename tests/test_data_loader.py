# tests/test_data_loader.py

import pytest 
import pandas as pd
from pathlib import Path

from datasheetai.data_loader.file_validator import FileValidator
from datasheetai.data_loader.parser import DataParser
from datasheetai.data_loader.loader import DataLoader
from datasheetai.exceptions import (
    FileNotFoundError,
    UnsupportedFileTypeError, 
    FileTooLargeError, 
    FileParseError
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

class TestDataLoaderParser:
    def test_parse_valid_csv(self, data_loader_config, sample_csv):
        # Same sample data as in the CSV file for testing (infer headers and types are True)
        sample_df = pd.DataFrame(
            {
                "id": [1, 2, 3],
                "first": ["Alice", "Bob", "Charlie"],
                "last": ["Johnson", "Dylan", "Puth"],
                "age": [21, 25, 29],
                "score": [95.5, 87.0, 92.3]
            }
        )
        parser = DataParser(data_loader_config)
        df = parser.parse_csv(sample_csv)
        assert not df.empty
        pd.testing.assert_frame_equal(df, sample_df)

    # .txt is not invalid in itself, fixture updated to write byte to temp file make pd.read_csv() fail
    def test_parse_invalid_file(self, data_loader_config, invalid_file):
        parser = DataParser(data_loader_config)
        with pytest.raises(FileParseError):
            parser.parse_csv(invalid_file)

class TestDataLoader:
    def test_load_valid_csv(self, data_loader_config, sample_csv):
        loader = DataLoader(data_loader_config)
        df = loader.load(str(sample_csv))
        assert not df.empty
        assert isinstance(df, pd.DataFrame)

    def test_load_unsupported_file(self, data_loader_config, invalid_file):
        loader = DataLoader(data_loader_config)
        with pytest.raises(UnsupportedFileTypeError):
            loader.load(str(invalid_file))