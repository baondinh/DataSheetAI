# datasheetai/llm_adapter/adapter.py

import os
import re
import logging
import anthropic

from datasheetai.config import LLMConfig
from datasheetai.schema_manager.schema import TableSchema
from datasheetai.sql_validator.validator import SQLValidator
from datasheetai.exceptions import LLMAdapterError

logger = logging.getLogger(__name__)


class LLMAdapter:
    """
    Translates natural language query into a valid SQL SELECT statement using Anthropic API.

    Used by:
        datasheetai/query_service/query_service.py -> QueryService
    """

    def __init__(self, config: LLMConfig, validator: SQLValidator) -> None:
        self.config = config
        self.validator = validator
        self._client: anthropic.Anthropic | None = None

    # Translate natural language query into valid SQL SELECT statement
    def translate(self, natural_language: str, schemas: list[TableSchema]) -> str:       
        if not natural_language or not natural_language.strip():
            raise LLMAdapterError("Natural language query cannot be empty.")

        if not schemas:
            raise LLMAdapterError(
                "No table schemas provided. Load data into the database before querying."
            )

        client = self._get_client()
        system_prompt = self._build_schema_prompt(schemas)

        logger.debug(f"Sending query to {self.config.model}: {natural_language!r}")

        try:
            response = client.messages.create(
                model=self.config.model,
                max_tokens=self.config.max_tokens,
                system=system_prompt,
                messages=[{"role": "user", "content": natural_language}],
            )
        except anthropic.APIConnectionError as e:
            raise LLMAdapterError(f"Connection to Anthropic API failed - {e}") from e
        except anthropic.AuthenticationError as e:
            raise LLMAdapterError(f"Anthropic API authentication failed - {e}") from e
        except anthropic.APIStatusError as e:
            raise LLMAdapterError(f"Anthropic API returned an error - {e}") from e

        raw_text = response.content[0].text
        logger.debug(f"Raw LLM response: {raw_text!r}")

        sql = self._extract_sql(raw_text)
        if not sql:
            raise LLMAdapterError(
                f"LLM response did not contain a SQL statement: {raw_text!r}"
            )

        # SQLValidatorError intentionally propagates — caller decides how to handle it
        validated_sql = self.validator.validate(sql)
        logger.info(f"Validated SQL: {validated_sql!r}")
        return validated_sql

    # ------------------------------------------------------------------
    # Helper methods
    # ------------------------------------------------------------------

    # Initialize Anthropic client using API key from env var specified in config
    def _get_client(self) -> anthropic.Anthropic:
        if self._client is None:
            api_key = os.environ.get(self.config.api_key_env_var)
            if not api_key:
                raise LLMAdapterError(
                    f"Anthropic API key not found. "
                    f"Set the '{self.config.api_key_env_var}' environment variable."
                )
            self._client = anthropic.Anthropic(api_key=api_key)
        return self._client

    # Pre built schema prompt to provide context and rules to LLM for SQL generation 
    def _build_schema_prompt(self, schemas: list[TableSchema]) -> str:
        schema_lines = []
        for table in schemas:
            schema_lines.append(f"Table: {table.table_name}")
            for col in table.columns:
                schema_lines.append(f"  - {col.column_name} ({col.sqlite_dtype})")

        schema_text = "\n".join(schema_lines)

        return (
            "Assume the role of a SQL assistant for a SQLite database.\n"
            "Given a database schema and a natural language question, generate a single "
            "valid SQLite SELECT statement that answers the question.\n\n"
            "Rules:\n"
            "- Return ONLY the raw SQL statement, no explanation, no markdown, and no code fences\n"
            "- Use only SELECT statements\n"
            "- Only reference tables and columns that exist in the schema below\n"
            "- Do not use INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, or any write operations\n\n"
            f"Available schema:\n{schema_text}"
        )

    # Return SQL SELECT statement from LLM response
    def _extract_sql(self, text: str) -> str:
        text = text.strip()
        # Regex to remove markdown code fences if present
        fenced = re.match(
            r"^```(?:sql)?\s*\n?(.*?)\n?```$", text, re.DOTALL | re.IGNORECASE
        )
        if fenced:
            return fenced.group(1).strip()
        return text
