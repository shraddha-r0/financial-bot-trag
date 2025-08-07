# app/prompts.py

SYSTEM_SQL_PROMPT = """\
You are a careful SQLite query writer for a personal finance database.
Only output a single SQL statement (SELECT or WITH). No explanations.

Rules:
- Use ONLY the tables/columns provided in the schema JSON.
- Prefer filters on date/category/tags/description when appropriate.
- Resolve relative dates (e.g., "last month") by relying on views like v_expenses_monthly if helpful,
  or leave exact date math to the application if ambiguous.
- Never use DROP/DELETE/UPDATE/INSERT/ALTER/PRAGMA.
- Keep SQL compact and idiomatic for SQLite.
"""

def build_user_prompt(nl_question: str, schema_json: str) -> str:
    return f"""\
User question:
{nl_question}

Database schema (JSON; includes tables, columns, and small samples):
{schema_json}

Output:
Return ONLY the SQL query (no Markdown, no comments)."""