# datasheetai/sql_validator/validator.py

import re
import logging

from datasheetai.exceptions import SQLValidatorError

logger = logging.getLogger(__name__)

# Following list generated with the help of generative AI, based on common SQL keywords and known attack vectors
# Write/destructive SQL operations that are banned
# PRAGMA is blocked because it can expose or modify database internals
# ATTACH / DETACH are blocked because they can open arbitrary database files
_BANNED_KEYWORDS = {
    "INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE",
    "TRUNCATE", "REPLACE", "ATTACH", "DETACH", "PRAGMA",
}

class SQLValidator:
    """
    Validates returned SQL string from LLM is safe and read-only SELECT statement
    before it is executed against the database.

    Used by:
        datasheetai/llm_adapter/adapter.py -> LLMAdapter
        datasheetai/query_service/query_service.py -> QueryService
    """
    def validate(self, sql: str) -> str:
        # Check for empty or whitespace input
        if not sql or not sql.strip():
            raise SQLValidatorError("SQL query cannot be empty.")

        cleaned = self._strip_comments(sql).strip()

        if not cleaned:
            raise SQLValidatorError("SQL query is empty after stripping comments.")

        cleaned = cleaned.rstrip(";").strip()

        # Call helper method checks
        self._check_single_statement(cleaned)
        self._check_starts_with_select(cleaned)
        self._check_banned_keywords(cleaned)

        logger.debug(f"SQL passed validation: {cleaned!r}")
        return cleaned

    # ------------------------------------------------------------------
    # Helper methods 
    # ------------------------------------------------------------------

    def _strip_comments(self, sql: str) -> str:
        # regex to remove comments from SQL string
        sql = re.sub(r"/\*.*?\*/", "", sql, flags=re.DOTALL)
        sql = re.sub(r"--[^\n]*", "", sql)
        return sql

    def _check_single_statement(self, sql: str) -> None:
        # strip semicolon instance
        stripped = sql.rstrip().rstrip(";")
        # Semicolon separators indicate multiple statements (single statement might end with semicolon)
        if ";" in stripped:
            raise SQLValidatorError(
                "Multiple SQL statements are not allowed. Submit one SELECT at a time."
            )

    def _check_starts_with_select(self, sql: str) -> None:
        # regex to find first word in SQL statement and reject non SELECT statements
        first_token = sql.split()[0].upper()
        if first_token != "SELECT":
            raise SQLValidatorError(
                f"Only SELECT statements are allowed. Got: '{first_token}'"
            )

    def _check_banned_keywords(self, sql: str) -> None:
        # regex to find and reject all banned keywords in SQL statement 
        tokens = set(re.findall(r"\b[A-Z_]+\b", sql.upper()))
        violations = tokens & _BANNED_KEYWORDS
        if violations:
            raise SQLValidatorError(
                f"SQL contains banned keyword(s): {', '.join(sorted(violations))}"
            )
