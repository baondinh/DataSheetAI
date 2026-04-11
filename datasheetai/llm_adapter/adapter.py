# datasheetai/llm_adapter/adapter.py

import logging
import pandas as pd

logging = logging.getLogger(__name__)

'''
TODO: Implement LLMAdapter class 
- Will take str natural language query 
- Will connect to LLM API and use env vars for authentication (secret management to be implemented later)
- Will send prompt to LLM and receive SQL response
- Needs to send response to validator to ensure SQL is safe (hardcode banned keywords for now)
- Will interact with DatabaseManager to execute queries and return results
- IMPORTANT: Do not allow direct execution of arbitrary SQL queries
'''