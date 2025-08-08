

"""
Prompt Engineering Module

This module contains the system and user prompts used to guide the language model in
generating valid SQL queries from natural language questions. The prompts are designed
to ensure the generated SQL is safe, efficient, and follows best practices.
"""
from typing import Dict, Any, List, Optional

# System prompt that guides the language model's behavior for SQL generation
SYSTEM_SQL_PROMPT = """\
You are a careful SQLite query writer for a personal finance database.

STRICT RULES:
1. Use ONLY the tables and columns from the provided schema JSON.
2. If unsure about a column or table, return the closest valid query using only the provided schema.
3. Never use DROP, DELETE, UPDATE, INSERT, ALTER, PRAGMA, or other destructive operations.
4. Always include a WHERE clause when filtering data for security and performance.
5. Use SQLite date functions for relative dates (e.g., 'last month', 'this year').
6. Always reference at least one of these required tables: expenses, incomes.
7. Never return a constant SELECT statement (e.g., SELECT 1).

GUIDELINES:
- Prefer filtering on date, category, tags, and description columns when relevant.
- Use existing views and functions from the schema when possible.
- Keep SQL queries compact and idiomatic for SQLite.
- Format currency values appropriately (e.g., CLP for Chilean Pesos).
- Use appropriate aggregate functions (SUM, AVG, COUNT, etc.) when summarizing data.
- Include comments only when necessary to explain complex logic.
"""

def build_user_prompt(nl_question: str, schema_json: str) -> str:
    """
    Construct a user prompt for the language model to generate SQL.
    
    This function formats the natural language question and database schema
    into a structured prompt that guides the model to generate valid SQL.
    
    Args:
        nl_question: The natural language question from the user
        schema_json: JSON string containing the database schema information
        
    Returns:
        A formatted string containing the user prompt
        
    Example:
        >>> schema = '{"tables": {"expenses": {"columns": ["amount", "date"]}}}'
        >>> build_user_prompt("Show recent expenses", schema)
        'User question:\nShow recent expenses\n\nDatabase schema...'
    """
    return f"""\
User question:
{nl_question}

Database schema (JSON; includes tables, columns, and small samples):
{schema_json}

Output:
Return ONLY the SQL query (no Markdown, no comments)."""