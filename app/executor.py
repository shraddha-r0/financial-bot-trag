"""
SQL Query Executor Module

This module handles the execution of SQL queries against the financial database.
It includes functionality to detect query types, execute SQL safely, and return
structured results with performance metrics.
"""
import sqlite3
import time
import re
from pathlib import Path
from typing import Dict, List, Any, Literal

# Default database path (relative to project root)
DB_PATH = Path("../data/clean/finances.db")

# Regular expressions for SQL query analysis
_AGG_FUNCS = re.compile(r"\b(SUM|AVG|COUNT|MIN|MAX)\s*\(", re.IGNORECASE)
_GROUP_BY = re.compile(r"\bGROUP\s+BY\b", re.IGNORECASE)

def detect_query_type(sql: str) -> Literal["scalar_aggregate", "grouped_aggregate", "detail"]:
    """
    Analyze SQL query to determine its type based on structure and clauses.
    
    Args:
        sql: The SQL query string to analyze
        
    Returns:
        str: Query type - one of:
            - 'scalar_aggregate': Queries with aggregate functions but no GROUP BY
            - 'grouped_aggregate': Queries with GROUP BY clause
            - 'detail': Simple SELECT queries without aggregation
            
    Example:
        >>> detect_query_type("SELECT SUM(amount) FROM expenses")
        'scalar_aggregate'
    """
    has_agg = bool(_AGG_FUNCS.search(sql))
    has_group = bool(_GROUP_BY.search(sql))

    if has_agg and not has_group:
        return "scalar_aggregate"
    if has_group:
        return "grouped_aggregate"
    return "detail"

def run_sql(sql: str, db_path: Path = DB_PATH, max_rows: int = 1000) -> Dict[str, Any]:
    """
    Execute SQL query against the database and return structured results.
    
    Args:
        sql: The SQL query to execute (must be a SELECT query)
        db_path: Path to the SQLite database file
        max_rows: Maximum number of rows to return for detail queries
        
    Returns:
        Dict containing:
            - type: Query type (scalar_aggregate, grouped_aggregate, or detail)
            - columns: List of column names in the result set
            - rows: List of result rows as dictionaries
            - row_count: Total number of rows in the full result set
            - elapsed_ms: Query execution time in milliseconds
            
    Raises:
        FileNotFoundError: If database file doesn't exist
        sqlite3.Error: For SQL execution errors
        ValueError: For invalid queries
    """
    # Validate database path
    db_path = Path(db_path)
    if not db_path.exists():
        raise FileNotFoundError(f"Database not found at {db_path.resolve()}")
        
    # Basic SQL validation
    sql = sql.strip().upper()
    if not (sql.startswith("SELECT") or sql.startswith("WITH")):
        raise ValueError("Only SELECT and WITH queries are allowed")

    # Execute query with timing
    start = time.time()
    try:
        with sqlite3.connect(str(db_path)) as conn:
            # Configure connection to return rows as dictionaries
            conn.row_factory = sqlite3.Row
            
            # Execute query and fetch results
            cur = conn.execute(sql)
            rows = cur.fetchall()
            columns = [desc[0] for desc in cur.description]
            
    except sqlite3.Error as e:
        raise ValueError(f"SQL execution error: {str(e)}")
        
    elapsed_ms = (time.time() - start) * 1000
    q_type = detect_query_type(sql)
    row_count = len(rows)
    
    # For detail queries, apply row limit to preview
    if q_type == "detail" and row_count > max_rows:
        preview_rows = rows[:max_rows]
    else:
        preview_rows = rows

    # Convert sqlite.Row objects to dictionaries
    preview_as_dicts = [dict(r) for r in preview_rows]

    return {
        "type": q_type,
        "columns": columns,
        "rows": preview_as_dicts,
        "row_count": row_count,
        "elapsed_ms": elapsed_ms,
    }