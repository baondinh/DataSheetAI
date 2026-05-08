# tests/conftest.py

import sqlite3
import pytest
from pathlib import Path

from datasheetai.config import (
    AppConfig,
    DataLoaderConfig,
    SchemaManagerConfig,
    DatabaseConfig,
    LLMConfig,
)
from datasheetai.llm_adapter.adapter import LLMAdapter
from datasheetai.sql_validator.validator import SQLValidator
from datasheetai.schema_manager.schema import TableSchema, ColumnSchema


# Shared path to test data files
DOCS_DATA = Path(__file__).parent.parent / "docs" / "data"


# ------------------------------------------------------------------
# Config fixtures
# ------------------------------------------------------------------

@pytest.fixture
def app_config():
    return AppConfig(data_loader=DataLoaderConfig())

@pytest.fixture
def data_loader_config():
    return DataLoaderConfig()

@pytest.fixture
def schema_manager_config():
    return SchemaManagerConfig()

@pytest.fixture
def database_manager_config():
    return DatabaseConfig()

@pytest.fixture
def llm_config():
    return LLMConfig(
        model="claude-sonnet-4-6",
        max_tokens=500,
        api_key_env_var="ANTHROPIC_API_KEY",
    )


# ------------------------------------------------------------------
# File fixtures
# ------------------------------------------------------------------

@pytest.fixture
def sample_csv():
    return DOCS_DATA / "sample.csv"

@pytest.fixture
def empty_csv():
    return DOCS_DATA / "empty.csv"

@pytest.fixture
def invalid_file(tmp_path):
    # Write binary PNG header bytes so pd.read_csv() raises a parse error
    invalid_file = tmp_path / "invalid.txt"
    invalid_file.write_bytes(b'\x89PNG\r\n\x1a\n\x00\x00')
    return invalid_file


# ------------------------------------------------------------------
# LLM adapter fixtures
# ------------------------------------------------------------------

@pytest.fixture
def validator():
    return SQLValidator()

@pytest.fixture
def adapter(llm_config, validator):
    return LLMAdapter(config=llm_config, validator=validator)

@pytest.fixture
def sample_schemas():
    return [
        TableSchema(
            table_name="employees",
            columns=[
                ColumnSchema("id", "INTEGER"),
                ColumnSchema("name", "TEXT"),
                ColumnSchema("age", "INTEGER"),
                ColumnSchema("salary", "REAL"),
            ],
        )
    ]


# ------------------------------------------------------------------
# Database fixtures
# ------------------------------------------------------------------

@pytest.fixture
def in_memory_config(tmp_path):
    # AppConfig pointing at a temp SQLite file so tests don't share state
    db_path = str(tmp_path / "test.db")
    return AppConfig(database=DatabaseConfig(path=db_path))

@pytest.fixture
def seeded_config(tmp_path):
    # AppConfig with a pre-populated employees table for query service tests
    db_path = str(tmp_path / "seeded.db")
    conn = sqlite3.connect(db_path)
    conn.execute("CREATE TABLE employees (id INTEGER, name TEXT, salary REAL)")
    conn.executemany(
        "INSERT INTO employees VALUES (?, ?, ?)",
        [(1, "Alice", 90000.0), (2, "Bob", 75000.0), (3, "Carol", 85000.0)],
    )
    conn.commit()
    conn.close()
    return AppConfig(database=DatabaseConfig(path=db_path))
