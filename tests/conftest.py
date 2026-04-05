# tests/conftest.py

import pytest 
from pathlib import Path
from datasheetai.config import AppConfig, DataLoaderConfig

# Fixture path
DOCS_DATA = Path(__file__).parent.parent / "docs" / "data"

@pytest.fixture
def app_config(): 
    return AppConfig(data_loader=DataLoaderConfig())

@pytest.fixture
def data_loader_config(): 
    return DataLoaderConfig()