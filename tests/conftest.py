# tests/conftest.py

import pytest 
from pathlib import Path
from datasheetai.config import AppConfig, DataLoaderConfig

# Fixture path
DOCS_DATA = Path(__file__).parent.parent / "docs" / "data"

# config fixtures
@pytest.fixture
def app_config(): 
    return AppConfig(data_loader=DataLoaderConfig())

@pytest.fixture
def data_loader_config(): 
    return DataLoaderConfig()

# sample file fixtures (TODO: these files are currently gitignored but should be added back in for testing purposes)
@pytest.fixture
def sample_csv(): 
    return DOCS_DATA / "sample.csv"

@pytest.fixture
def empty_csv(): 
    return DOCS_DATA / "empty.csv"

@pytest.fixture
def invalid_file(tmp_path):
    invalid_file = tmp_path / "invalid.txt"
    invalid_file.write_bytes(b'\x89PNG\r\n\x1a\n\x00\x00')
    return invalid_file  

# @pytest.fixture
# def sample_json(): 
#     return DOCS_DATA / "sample_data.json"

# @pytest.fixture
# def sample_xlsx(): 
#     return DOCS_DATA / "sample_data.xlsx"
