# DataSheetAI

DataSheetAI is a natural language SQL query system implemented as a Python CLI tool. The system translates a natural language query to SQL using Claude. The system also ensures that SQL returned from the LLM is a SELECT statement to prevent accidental changes to the SQLite database. 

## Architecture

DataSheetAI is broken up into multiple modules that are organized into two independent flows sharing a SQLite database:

```
Flow 1 — Ingestion
  CLI → DataLoader → SchemaManager → DatabaseManager → SQLite

Flow 2 — Query
  CLI → QueryService → LLMAdapter (Claude API) → SQLValidator → DatabaseManager → SQLite
```

![Architecture diagram](docs/assets/claude_architecture.png)

## Setup

DataSheetAI uses a `pyproject.toml` project configuration to simplify dependency management and project setup.

**Requirements:** Python 3.11+

```bash
# Install the package and all dependencies
pip install -e ".[dev]"
```

### API Key

Querying (Flow 2) requires an Anthropic API key to be set up as an environment variable.
Important: Never store or hard code key in config files or source code
`ANTHROPIC_API_KEY` environment variable name is referenced in `config.yaml`

```powershell
# PowerShell — current session
$env:ANTHROPIC_API_KEY = "sk-ant-..."

# PowerShell — persist across sessions (add to your profile)
notepad $PROFILE
# Add: $env:ANTHROPIC_API_KEY = "sk-ant-..."
```

```bash
# bash / zsh
export ANTHROPIC_API_KEY="sk-ant-..."
```

## Usage

### Flow 1 — Ingestion

```python
from datasheetai.config import load_config
from datasheetai.cli.commands.load_file import ingest_file

config = load_config("config.yaml")
result = ingest_file("data/employees.csv", table_name="employees", config=config)
# {"status": "created", "table": "employees", "rows": 42}
```

Use `overwrite=True` to replace an existing table with a different schema:

```python
result = ingest_file("data/employees_v2.csv", "employees", config, overwrite=True)
# {"status": "overwritten", "table": "employees", "rows": 45}
```

### Flow 2 — Query

```python
from datasheetai.config import load_config
from datasheetai.query_service import QueryService

config = load_config("config.yaml")
svc = QueryService(config)

results = svc.execute("Show all employees earning more than 80000")
# [{"id": 1, "name": "Alice", "salary": 90000.0}, ...]
```

## Modules

| Module | Responsibility |
|---|---|
| `config` | YAML → typed dataclasses; single `AppConfig` root object |
| `data_loader` | File validation, CSV/JSON/Excel parsing → DataFrame |
| `schema_manager` | DataFrame dtype → SQLite schema inference; reads live DB schema |
| `database` | SQLite CRUD: connect, create table, insert, query, drop |
| `llm_adapter` | Schema-aware prompt + Anthropic API call → raw SQL |
| `sql_validator` | Rejects non-SELECT and dangerous keywords before execution |
| `query_service` | Orchestrates Flow 2 end-to-end |
| `cli` | Entry points for both flows |

## Running Tests

GitHub actions setup to automatically run all tests under `tests/` folder whenever there is a new commit.
Note: Tests mimic Anthropic API and do not require API key to run. 

```bash
python -m pytest tests/ -v
```

## Configuration

Edit `config.yaml` to change defaults:

```yaml
llm:
  model: claude-sonnet-4-6   # Anthropic model
  max_tokens: 1000

query_service:
  max_rows_returned: 200     # cap on results returned

database:
  path: datasheetai.db       # SQLite file location
```
