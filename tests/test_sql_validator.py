# tests/test_sql_validator.py

import pytest
from datasheetai.sql_validator import SQLValidator, SQLValidatorError

# @pytest.fixture
# def validator():
#     return SQLValidator()

# Test simple valid SELECT statements
class TestSQLValidatorValidQueries:
    def test_simple_select(self):
        validator = SQLValidator()
        sql = "SELECT * FROM users"
        assert validator.validate(sql) == sql

    def test_select_with_where(self):
        validator = SQLValidator()
        sql = "SELECT id, name FROM employees WHERE age > 30"
        assert validator.validate(sql) == sql

    def test_select_with_join(self):
        validator = SQLValidator()
        sql = "SELECT a.id, b.score FROM students a JOIN grades b ON a.id = b.student_id"
        assert validator.validate(sql) == sql

    def test_select_with_aggregation(self):
        validator = SQLValidator()
        sql = "SELECT department, COUNT(*) FROM employees GROUP BY department"
        assert validator.validate(sql) == sql

    def test_select_case_insensitive(self):
        validator = SQLValidator()
        sql = "select id from users"
        result = validator.validate(sql)
        assert result == sql

    def test_select_with_trailing_semicolon(self):
        validator = SQLValidator()
        result = validator.validate("SELECT 1;")
        assert result == "SELECT 1"

    def test_select_with_subquery(self):
        validator = SQLValidator()
        sql = "SELECT * FROM orders WHERE user_id IN (SELECT id FROM users)"
        assert validator.validate(sql) == sql

# Comments should be removed prior to returning statement
class TestSQLValidatorStripsComments:
    def test_strips_line_comment(self):
        validator = SQLValidator()
        sql = "SELECT id FROM users -- get all users"
        result = validator.validate(sql)
        assert "--" not in result
        assert "SELECT" in result

    def test_strips_block_comment(self):
        validator = SQLValidator()
        sql = "SELECT /* all columns */ * FROM users"
        result = validator.validate(sql)
        assert "/*" not in result
        assert "SELECT" in result

    def test_multiline_block_comment(self):
        validator = SQLValidator()
        sql = "SELECT *\n/* this comment\nspans lines */\nFROM users"
        result = validator.validate(sql)
        assert "/*" not in result

# Test empty and whitespace inputs are rejected
class TestSQLValidatorRejectsEmpty:
    def test_empty_string(self):
        validator = SQLValidator()
        with pytest.raises(SQLValidatorError, match="cannot be empty"):
            validator.validate("")

    def test_whitespace_only(self):
        validator = SQLValidator()
        with pytest.raises(SQLValidatorError, match="cannot be empty"):
            validator.validate("   ")

    def test_comment_only(self):
        validator = SQLValidator()
        with pytest.raises(SQLValidatorError, match="empty after stripping"):
            validator.validate("-- just a comment")

# Ensure valid SELECT statements
class TestSQLValidatorRejectsNonSelect:
    def test_rejects_insert(self):
        validator = SQLValidator()
        with pytest.raises(SQLValidatorError, match="Only SELECT"):
            validator.validate("INSERT INTO users VALUES (1, 'Alice')")

    def test_rejects_update(self):
        validator = SQLValidator()
        with pytest.raises(SQLValidatorError, match="Only SELECT"):
            validator.validate("UPDATE users SET name = 'Bob' WHERE id = 1")

    def test_rejects_delete(self):
        validator = SQLValidator()
        with pytest.raises(SQLValidatorError, match="Only SELECT"):
            validator.validate("DELETE FROM users WHERE id = 1")

    def test_rejects_drop(self):
        validator = SQLValidator()
        with pytest.raises(SQLValidatorError, match="Only SELECT"):
            validator.validate("DROP TABLE users")

    def test_rejects_create(self):
        validator = SQLValidator()
        with pytest.raises(SQLValidatorError, match="Only SELECT"):
            validator.validate("CREATE TABLE new_table (id INTEGER)")

    def test_rejects_alter(self):
        validator = SQLValidator()
        with pytest.raises(SQLValidatorError, match="Only SELECT"):
            validator.validate("ALTER TABLE users ADD COLUMN email TEXT")

# Ensure banned keywords are rejected even if embedded within SELECT statement
class TestSQLValidatorRejectsBannedKeywords:
    def test_rejects_drop_in_subquery(self):
        validator = SQLValidator()
        with pytest.raises(SQLValidatorError, match="Multiple SQL statements"):
            validator.validate("SELECT * FROM users; DROP TABLE users")

    def test_rejects_attach(self):
        validator = SQLValidator()
        with pytest.raises(SQLValidatorError, match="banned keyword"):
            validator.validate("SELECT * FROM users ATTACH DATABASE 'other.db' AS other")

    def test_rejects_pragma(self):
        validator = SQLValidator()
        with pytest.raises(SQLValidatorError, match="banned keyword"):
            validator.validate("SELECT PRAGMA table_info('users')")

# Ensure multiple statements are rejected
class TestSQLValidatorRejectsMultipleStatements:
    def test_rejects_two_selects(self):
        validator = SQLValidator()
        with pytest.raises(SQLValidatorError, match="Multiple SQL statements"):
            validator.validate("SELECT 1; SELECT 2")

    def test_rejects_select_then_drop(self):
        validator = SQLValidator()
        with pytest.raises(SQLValidatorError, match="Multiple SQL statements"):
            validator.validate("SELECT * FROM users; DROP TABLE users")
