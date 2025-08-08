
"""
SQL Generation Module

This module handles the conversion of natural language questions into SQL queries
using a language model. It ensures the generated SQL is safe, valid, and follows
project-specific conventions before execution.
"""
import json
import re
import os
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple

from dotenv import load_dotenv
from openai import OpenAI

from app.sqlguard import sanitize_sql, apply_limit_policy

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Configuration constants
HF_MODEL = os.getenv("HF_MODEL", "openai/gpt-oss-20b")
SCHEMA_PATH = Path(__file__).parent.parent / "data" / "clean" / "schema_snapshot.json"
MAX_RETRIES = 2

# Regular expression to extract SQL from markdown code blocks
_FENCE = re.compile(r"^\s*```(?:sql)?\s*|\s*```\s*$", re.IGNORECASE)

# SQL keywords and functions for validation
SQL_KEYWORDS_FUNCS = {
    # SQL keywords
    "select", "from", "where", "and", "or", "as", "group", "by", "order",
    "limit", "desc", "asc", "on", "join", "inner", "left", "right", "full",
    "union", "all", "distinct", "having", "like", "in", "not", "between",
    "case", "when", "then", "else", "end", "is", "null", "true", "false",
    # SQL functions
    "sum", "avg", "count", "min", "max", "date", "strftime", "now", "start",
    "of", "coalesce", "ifnull", "round", "cast", "substr", "trim", "upper",
    "lower", "replace", "datetime", "julianday", "date", "time", "strftime"
}


def _strip_code_fences(s: str) -> str:
    """
    Remove markdown code fences from a string.
    
    Args:
        s: Input string potentially containing markdown code fences
        
    Returns:
        String with code fences removed
        
    Example:
        >>> _strip_code_fences("```sql\nSELECT * FROM table\n```")
        'SELECT * FROM table'
    """
    return _FENCE.sub("", s).strip()


def _load_schema_json() -> str:
    """
    Load and prepare the database schema JSON for the language model.
    
    Returns:
        JSON string containing the database schema with sample data
        
    Raises:
        FileNotFoundError: If the schema file doesn't exist
        json.JSONDecodeError: If the schema file contains invalid JSON
    """
    if not SCHEMA_PATH.exists():
        raise FileNotFoundError(
            f"Schema file not found at {SCHEMA_PATH}. "
            "Run: python -m scripts.snapshot_schema"
        )
        
    try:
        with SCHEMA_PATH.open(encoding="utf-8") as f:
            data = json.load(f)
            
        # Truncate samples to reduce context window size
        for table_info in data.values():
            samples = table_info.get("samples", [])
            if len(samples) > 5:
                table_info["samples"] = samples[:5]
                
        return json.dumps(data, ensure_ascii=False)
        
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing schema file: {e}")
        raise


def generate_sql(
    nl_question: str, 
    model: str = HF_MODEL, 
    temperature: float = 0.0,
    max_retries: int = MAX_RETRIES
) -> str:
    """
    Generate a safe SQL query from a natural language question.
    
    This function handles the complete pipeline from natural language to validated SQL:
    1. Loads the database schema
    2. Constructs a prompt for the language model
    3. Generates SQL using the language model
    4. Validates and sanitizes the generated SQL
    5. Applies safety policies (query limits, etc.)
    
    Args:
        nl_question: The natural language question to convert to SQL
        model: The language model to use for SQL generation
        temperature: Controls randomness in the model's output (0.0 = deterministic)
        max_retries: Maximum number of retry attempts if initial SQL is invalid
        
    Returns:
        A valid, sanitized SQL query string
        
    Raises:
        ValueError: If the generated SQL cannot be validated after max_retries
        RuntimeError: If there's an error communicating with the language model
    """
    # Load schema and prepare prompt
    schema_json = _load_schema_json()
    user_prompt = build_user_prompt(nl_question, schema_json)
    
    # Initialize OpenAI client
    client = OpenAI(
        base_url="https://router.huggingface.co/v1",
        api_key=os.getenv("HF_TOKEN"),
    )
    
    attempt = 0
    last_error = None
    
    while attempt <= max_retries:
        try:
            # Generate SQL using the language model
            response = client.chat.completions.create(
                model=model,
                temperature=temperature,
                messages=[
                    {"role": "system", "content": SYSTEM_SQL_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
            )
            
            # Extract and clean the generated SQL
            sql = response.choices[0].message.content.strip()
            sql = _strip_code_fences(sql).strip()
            
            # Apply validation and safety checks
            sql = sanitize_sql(sql)
            sql = apply_limit_policy(sql, nl_question, default_limit=500)
            
            logger.info(f"Generated SQL (attempt {attempt + 1}): {sql}")
            return sql
            
        except Exception as e:
            last_error = str(e)
            logger.warning(f"Attempt {attempt + 1} failed: {last_error}")
            attempt += 1
            if attempt > max_retries:
                break
                
    # If we've exhausted all retries
    error_msg = (
        f"Failed to generate valid SQL after {max_retries + 1} attempts. "
        f"Last error: {last_error}"
    )
    logger.error(error_msg)
    raise ValueError(error_msg)


def _get_allowed_identifiers(schema_json_str: str) -> set[str]:
    schema = json.loads(schema_json_str)
    allowed = set()
    for table, meta in schema.items():
        allowed.add(table.lower())
        for col in meta.get("columns", []):
            allowed.add(col["name"].lower())
    return allowed

def _find_invalid_identifiers(sql: str, allowed: set[str]):
    tokens = {t.lower() for t in re.split(r"[^\w]+", sql) if t}
    return [
        t for t in tokens
        if t not in allowed
        and t not in SQL_KEYWORDS_FUNCS
        and not t.isdigit()
    ]

# def generate_sql(nl_question: str) -> str:
#     schema_json = load_schema_json()
#     allowed = _get_allowed_identifiers(schema_json)

#     messages = [
#         {"role": "system", "content": SYSTEM_SQL_PROMPT},
#         {"role": "user", "content": build_user_prompt(nl_question, schema_json)},
#     ]

#     for attempt in range(MAX_RETRIES + 1):
#         resp = client.chat.completions.create(
#             model=HF_MODEL,
#             temperature=0,
#             messages=messages
#         )
#         sql = resp.choices[0].message.content.strip()

#         invalid = _find_invalid_identifiers(sql, allowed)

#         if not invalid:
#             return sql

#         if attempt < MAX_RETRIES:
#             print(f"⚠️ Invalid identifiers found: {invalid} — retrying...")
#             correction = (
#                 f"The SQL you wrote used invalid columns/tables: {invalid}.\n"
#                 f"Allowed identifiers: {sorted(list(allowed))}.\n"
#                 f"Rewrite the query so it ONLY uses the allowed identifiers."
#             )
#             messages.append({"role": "assistant", "content": sql})
#             messages.append({"role": "user", "content": correction})
#         else:
#             raise ValueError(f"Invalid identifiers after {MAX_RETRIES+1} attempts: {invalid}")

#     return sql