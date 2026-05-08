# datasheetai/cli/commands/load_file.py

import logging

from datasheetai.config import AppConfig
from datasheetai.data_loader.loader import DataLoader
from datasheetai.schema_manager.manager import SchemaManager
from datasheetai.database.database_manager import DatabaseManager
from datasheetai.exceptions import SchemaManagerError

logger = logging.getLogger(__name__)

# Load file into SQLite table
def ingest_file(path: str,
                table_name: str,
                config: AppConfig,
                overwrite: bool = False) -> dict:
    logger.info(f"Starting ingestion: {path} -> table '{table_name}'")

    # 1) Validate and parse file into a DataFrame
    loader = DataLoader(config.data_loader)
    df = loader.load(file_path=path)

    # 2) Infer schema from the DataFrame
    sch_manager = SchemaManager(config.schema_manager)
    incoming = sch_manager.translate_schema(df=df, table_name=table_name)

    # 3) Write to database
    with DatabaseManager(config.database) as db:
        if not db.table_exists(table_name):
            db.create_table(incoming)
            rows = db.insert_data(table_name, df)
            return {"status": "created", "table": table_name, "rows": rows}

        existing = sch_manager.read_database_schema(db.connection, table_name)

        if incoming.matches(existing):
            rows = db.insert_data(table_name, df)
            return {"status": "appended", "table": table_name, "rows": rows}

        if overwrite:
            db.drop_table(table_name)
            db.create_table(incoming)
            rows = db.insert_data(table_name, df)
            return {"status": "overwritten", "table": table_name, "rows": rows}

        raise SchemaManagerError(
            f"Schema mismatch for table '{table_name}'. "
            "Use --overwrite to replace the existing table."
        )