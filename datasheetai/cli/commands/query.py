# datasheetai/cli/commands/query.py

import logging

from datasheetai.config import AppConfig
from datasheetai.query_service.query_service import QueryService

logger = logging.getLogger(__name__)

# Translate then execute natural language query against loaded SQLite database
def query_db(question: str, config: AppConfig) -> list[dict]:
    logger.info(f"Starting query: '{question}'")

    queryservice = QueryService(config)
    results = queryservice.execute(question) # translate built into execute function

    logger.info(f"Query complete: {len(results)} row(s) returned")
    return results
