# tests/test_query_service.py

import os
import sqlite3
import pytest
from unittest.mock import MagicMock

from datasheetai.config import AppConfig, DatabaseConfig
from datasheetai.query_service import QueryService, QueryServiceError
from datasheetai.exceptions import SQLValidatorError


# ---------------------------------------------------------------------------
# Fixtures
# TODO: Move fixtures to conftest.py
# ---------------------------------------------------------------------------

@pytest.fixture
def in_memory_config(tmp_path):
    """AppConfig pointing at a temp SQLite file so tests don't share state."""
    db_path = str(tmp_path / "test.db")
    return AppConfig(database=DatabaseConfig(path=db_path))


@pytest.fixture
def seeded_config(tmp_path):
    """AppConfig with a pre-populated employees table."""
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

# Test execute() using MagicMock testing tool to mock Anthropic API
class TestQueryServiceExecute:
    def test_returns_list_of_dicts(self, seeded_config):
        svc = QueryService(seeded_config)
        svc._adapter.translate = MagicMock(return_value="SELECT * FROM employees")

        results = svc.execute("Show all employees")

        assert isinstance(results, list)
        assert len(results) == 3
        assert results[0] == {"id": 1, "name": "Alice", "salary": 90000.0}

    def test_result_keys_match_column_names(self, seeded_config):
        svc = QueryService(seeded_config)
        svc._adapter.translate = MagicMock(
            return_value="SELECT id, name FROM employees"
        )

        results = svc.execute("Get employee names")

        assert set(results[0].keys()) == {"id", "name"}

    def test_passes_table_schemas_to_adapter(self, seeded_config):
        svc = QueryService(seeded_config)
        svc._adapter.translate = MagicMock(return_value="SELECT * FROM employees")

        svc.execute("Show all employees")

        call_args = svc._adapter.translate.call_args
        schemas = call_args.args[1]
        assert len(schemas) == 1
        assert schemas[0].table_name == "employees"

    def test_passes_natural_language_to_adapter(self, seeded_config):
        svc = QueryService(seeded_config)
        svc._adapter.translate = MagicMock(return_value="SELECT * FROM employees")
        question = "Who earns more than 80000?"

        svc.execute(question)

        call_args = svc._adapter.translate.call_args
        assert call_args.args[0] == question

    def test_filtered_query_returns_subset(self, seeded_config):
        svc = QueryService(seeded_config)
        svc._adapter.translate = MagicMock(
            return_value="SELECT * FROM employees WHERE salary > 80000"
        )

        results = svc.execute("Employees earning over 80000")

        assert len(results) == 2
        names = {r["name"] for r in results}
        assert names == {"Alice", "Carol"}

    def test_empty_result_returns_empty_list(self, seeded_config):
        svc = QueryService(seeded_config)
        svc._adapter.translate = MagicMock(
            return_value="SELECT * FROM employees WHERE salary > 999999"
        )

        results = svc.execute("Employees earning over a million")

        assert results == []

# Test excecute() error cases
class TestQueryServiceErrors:
    def test_raises_when_database_is_empty(self, in_memory_config):
        svc = QueryService(in_memory_config)

        with pytest.raises(QueryServiceError, match="No tables found"):
            svc.execute("Show everything")

    def test_propagates_sql_validator_error(self, seeded_config):
        svc = QueryService(seeded_config)
        svc._adapter.translate = MagicMock(side_effect=SQLValidatorError("unsafe SQL"))

        with pytest.raises(SQLValidatorError):
            svc.execute("Drop all tables")
