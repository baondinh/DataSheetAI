# DataSheetAI
EC530 DataSheetAI Project

Objective: Design a natural language SQL query system that implements a CLI tool with two independent flows:
- Data ingestion 
- Query processing

Query Processing: 
A user can type something like "show me all customers from California" and the system:
- Sends that question to an LLM (Claude or OpenAI)
- LLM translates it to SQL
- System validates and safely executes the SQL on a SQLite database
- Returns the results to the user
 
Notes: 
- For this assignment, using Claude as Assistant/LLM Adapter 
- Recall CRUD: Create, Read, Update, Delete
- Use assistant to suggest project updates and code review

# Updated Architecture: 
![alt text](docs/assets/claude_architecture.png)

# Modules: 
- cli
- csv_loader
- llm_adapter
- query_service
- schema_manager
- sql_validator 
