"""
Database Connection Module

This module provides a simple interface for interacting with a SQLite database.
It includes a context manager for handling database connections and a utility
function for running queries.
"""
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Iterator
import sqlite3

# Default path to the SQLite database file
DB_PATH = Path("../data/clean/finances.db")

@contextmanager
def connect(db_path: Path = DB_PATH) -> Iterator[sqlite3.Connection]:
    """
    Context manager for database connections.
    
    This context manager handles the lifecycle of a database connection,
    ensuring proper setup and teardown. It also configures the connection
    to return rows as dictionaries for easier data access.
    
    Args:
        db_path: Path to the SQLite database file. Defaults to DB_PATH.
        
    Yields:
        A SQLite connection object with row factory set to sqlite3.Row
        
    Example:
        >>> with connect() as conn:
        ...     cursor = conn.cursor()
        ...     cursor.execute("SELECT * FROM expenses LIMIT 1")
        ...     row = cursor.fetchone()
        ...     print(dict(row))
    """
    # Ensure the parent directory exists
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Establish connection and configure it
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row  # Allow dictionary-style access to columns
    
    try:
        yield conn
    finally:
        # Ensure the connection is always closed, even if an error occurs
        conn.close()

def run(sql: str, params: Tuple[Any, ...] = ()) -> Optional[List[Dict[str, Any]]]:
    """
    Execute a SQL query and return the results as a list of dictionaries.
    
    This is a convenience function for executing read-only queries that
    return result sets. For write operations or more complex transactions,
    use the connect() context manager directly.
    
    Args:
        sql: The SQL query to execute
        params: Parameters to substitute into the SQL query (default: empty tuple)
        
    Returns:
        A list of dictionaries representing the query results, where each
        dictionary maps column names to values. Returns None for queries
        that don't return results (e.g., INSERT, UPDATE, DELETE).
        
    Raises:
        sqlite3.Error: If there's an error executing the query
        
    Example:
        >>> results = run("SELECT * FROM expenses WHERE amount > ?", (1000,))
        >>> for row in results:
        ...     print(f"{row['date']}: {row['amount']} {row['currency']}")
    """
    with connect() as conn:
        cursor = conn.execute(sql, params)
        
        # For queries that don't return results (e.g., INSERT, UPDATE, DELETE)
        if cursor.description is None:
            return None
            
        # Convert rows to dictionaries for easier access
        return [dict(row) for row in cursor.fetchall()]