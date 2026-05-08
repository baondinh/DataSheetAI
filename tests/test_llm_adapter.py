# tests/test_llm_adapter.py

import os
import pytest
from unittest.mock import MagicMock, patch

from datasheetai.config import LLMConfig
from datasheetai.llm_adapter import LLMAdapter, LLMAdapterError
from datasheetai.sql_validator.validator import SQLValidator
from datasheetai.exceptions import SQLValidatorError
from datasheetai.schema_manager.schema import TableSchema, ColumnSchema


# ---------------------------------------------------------------------------
# Shared fixtures
# TODO: Move fixtures to conftest.py
# ---------------------------------------------------------------------------

@pytest.fixture
def config():
    return LLMConfig(
        model="claude-sonnet-4-6",
        max_tokens=500,
        api_key_env_var="ANTHROPIC_API_KEY",
    )

@pytest.fixture
def validator():
    return SQLValidator()

@pytest.fixture
def adapter(config, validator):
    return LLMAdapter(config=config, validator=validator)

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

def _make_mock_response(sql: str) -> MagicMock:
    """Build a minimal mock that looks like an anthropic Messages response."""
    content_block = MagicMock()
    content_block.text = sql
    response = MagicMock()
    response.content = [content_block]
    return response


# ---------------------------------------------------------------------------
# translate() — happy path
# ---------------------------------------------------------------------------

class TestLLMAdapterTranslate:
    def test_returns_validated_sql(self, adapter, sample_schemas):
        expected_sql = "SELECT * FROM employees"
        mock_response = _make_mock_response(expected_sql)

        with patch("datasheetai.llm_adapter.adapter.anthropic.Anthropic") as MockClient:
            MockClient.return_value.messages.create.return_value = mock_response
            with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}):
                result = adapter.translate("Show all employees", sample_schemas)

        assert result == expected_sql

    def test_strips_markdown_code_fence(self, adapter, sample_schemas):
        mock_response = _make_mock_response("```sql\nSELECT id FROM employees\n```")

        with patch("datasheetai.llm_adapter.adapter.anthropic.Anthropic") as MockClient:
            MockClient.return_value.messages.create.return_value = mock_response
            with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}):
                result = adapter.translate("Get employee IDs", sample_schemas)

        assert result == "SELECT id FROM employees"

    def test_strips_plain_code_fence(self, adapter, sample_schemas):
        mock_response = _make_mock_response("```\nSELECT name FROM employees\n```")

        with patch("datasheetai.llm_adapter.adapter.anthropic.Anthropic") as MockClient:
            MockClient.return_value.messages.create.return_value = mock_response
            with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}):
                result = adapter.translate("Get names", sample_schemas)

        assert result == "SELECT name FROM employees"

    def test_passes_schemas_in_system_prompt(self, adapter, sample_schemas):
        """The system prompt must contain table and column names."""
        mock_response = _make_mock_response("SELECT * FROM employees")

        with patch("datasheetai.llm_adapter.adapter.anthropic.Anthropic") as MockClient:
            instance = MockClient.return_value
            instance.messages.create.return_value = mock_response
            with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}):
                adapter.translate("Show all", sample_schemas)

            call_kwargs = instance.messages.create.call_args.kwargs
            system_prompt = call_kwargs["system"]

        assert "employees" in system_prompt
        assert "name" in system_prompt
        assert "salary" in system_prompt

    def test_passes_natural_language_as_user_message(self, adapter, sample_schemas):
        mock_response = _make_mock_response("SELECT * FROM employees")
        question = "How many employees earn more than 50000?"

        with patch("datasheetai.llm_adapter.adapter.anthropic.Anthropic") as MockClient:
            instance = MockClient.return_value
            instance.messages.create.return_value = mock_response
            with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}):
                adapter.translate(question, sample_schemas)

            call_kwargs = instance.messages.create.call_args.kwargs
            messages = call_kwargs["messages"]

        assert messages[0]["role"] == "user"
        assert messages[0]["content"] == question

# Test propogation of SQLValidatorError when LLM returns unsafe SQL
class TestLLMAdapterValidationGuard:
    # LLM returns a DROP statement — must raise SQLValidatorError, not LLMAdapterError
    def test_propagates_sql_validator_error_on_unsafe_sql(self, adapter, sample_schemas):
        mock_response = _make_mock_response("DROP TABLE employees")

        with patch("datasheetai.llm_adapter.adapter.anthropic.Anthropic") as MockClient:
            MockClient.return_value.messages.create.return_value = mock_response
            with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}):
                with pytest.raises(SQLValidatorError):
                    adapter.translate("Delete all employees", sample_schemas)

    # LLM returns an INSERT statement — must raise SQLValidatorError, not LLMAdapterError
    def test_propagates_sql_validator_error_on_insert(self, adapter, sample_schemas):
        mock_response = _make_mock_response("INSERT INTO employees VALUES (1, 'Eve', 30, 70000)")

        with patch("datasheetai.llm_adapter.adapter.anthropic.Anthropic") as MockClient:
            MockClient.return_value.messages.create.return_value = mock_response
            with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}):
                with pytest.raises(SQLValidatorError):
                    adapter.translate("Add a new employee", sample_schemas)

# Test input validation for translate() method
class TestLLMAdapterInputValidation:
    def test_raises_on_empty_query(self, adapter, sample_schemas):
        with pytest.raises(LLMAdapterError, match="cannot be empty"):
            adapter.translate("", sample_schemas)

    def test_raises_on_whitespace_query(self, adapter, sample_schemas):
        with pytest.raises(LLMAdapterError, match="cannot be empty"):
            adapter.translate("   ", sample_schemas)

    def test_raises_on_empty_schemas(self, adapter):
        with pytest.raises(LLMAdapterError, match="No table schemas"):
            adapter.translate("Show all employees", [])

# Test API connection and response errors handling
class TestLLMAdapterClientErrors:
    def test_raises_on_missing_api_key(self, adapter, sample_schemas):
        env_without_key = {k: v for k, v in os.environ.items()
                          if k != "ANTHROPIC_API_KEY"}
        with patch.dict(os.environ, env_without_key, clear=True):
            with pytest.raises(LLMAdapterError, match="API key not found"):
                adapter.translate("Show all employees", sample_schemas)

    def test_raises_on_api_connection_error(self, adapter, sample_schemas):
        import anthropic as anthropic_lib

        with patch("datasheetai.llm_adapter.adapter.anthropic.Anthropic") as MockClient:
            MockClient.return_value.messages.create.side_effect = (
                anthropic_lib.APIConnectionError(request=MagicMock())
            )
            with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}):
                with pytest.raises(LLMAdapterError, match="Connection"):
                    adapter.translate("Show all employees", sample_schemas)

    def test_raises_on_empty_llm_response(self, adapter, sample_schemas):
        mock_response = _make_mock_response("   ")

        with patch("datasheetai.llm_adapter.adapter.anthropic.Anthropic") as MockClient:
            MockClient.return_value.messages.create.return_value = mock_response
            with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}):
                with pytest.raises((LLMAdapterError, SQLValidatorError)):
                    adapter.translate("Show all employees", sample_schemas)


# Test schema prompt construction for LLM context
class TestLLMAdapterSchemaPrompt:
    def test_prompt_contains_all_tables(self, adapter):
        schemas = [
            TableSchema("orders", [ColumnSchema("id", "INTEGER")]),
            TableSchema("products", [ColumnSchema("name", "TEXT")]),
        ]
        prompt = adapter._build_schema_prompt(schemas)
        assert "orders" in prompt
        assert "products" in prompt

    def test_prompt_contains_column_types(self, adapter):
        schemas = [
            TableSchema("sales", [
                ColumnSchema("amount", "REAL"),
                ColumnSchema("date", "TEXT"),
            ])
        ]
        prompt = adapter._build_schema_prompt(schemas)
        assert "REAL" in prompt
        assert "TEXT" in prompt

# Test SQL extraction from LLM response
class TestLLMAdapterExtractSQL:
    def test_plain_sql_unchanged(self, adapter):
        assert adapter._extract_sql("SELECT 1") == "SELECT 1"

    def test_strips_sql_fence(self, adapter):
        assert adapter._extract_sql("```sql\nSELECT 1\n```") == "SELECT 1"

    def test_strips_plain_fence(self, adapter):
        assert adapter._extract_sql("```\nSELECT 1\n```") == "SELECT 1"

    def test_strips_surrounding_whitespace(self, adapter):
        assert adapter._extract_sql("  SELECT 1  ") == "SELECT 1"
