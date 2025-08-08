"""
SQL Guard Module

This module provides security and safety checks for SQL queries to prevent
malicious or dangerous operations. It validates and sanitizes SQL queries
before they are executed against the database.

Key Features:
- Validates that only SELECT/WITH queries are allowed
- Blocks dangerous SQL operations (DROP, DELETE, etc.)
- Provides utilities for analyzing query structure
- Implements safety limits on result sets
"""
import re
from typing import Optional, Match, Pattern, Dict, Any, List, Tuple, Set, Union

# Regular expressions for SQL validation and analysis
ALLOWED_START = re.compile(r"^\s*(SELECT|WITH)\b", re.IGNORECASE)
DANGEROUS = re.compile(r"\b(DROP|DELETE|UPDATE|INSERT|ALTER|REPLACE|ATTACH|DETACH|VACUUM|PRAGMA)\b", re.IGNORECASE)
AGG_FUNCS = re.compile(r"\b(SUM|AVG|COUNT|MIN|MAX)\s*\(", re.IGNORECASE)

# Regular expression for detecting TOP N style queries in natural language
_TOPK_PAT = re.compile(
    r"\b(top|bottom|first|last)\s+(\d+)\b", 
    re.IGNORECASE
)

def sanitize_sql(sql: str) -> str:
    """
    Validate and sanitize a SQL query string.
    
    This function performs several security checks:
    1. Ensures the query is a single statement
    2. Validates the query starts with SELECT or WITH
    3. Blocks potentially dangerous SQL operations
    
    Args:
        sql: The SQL query string to validate
        
    Returns:
        The sanitized SQL string with trailing semicolons removed
        
    Raises:
        ValueError: If the query is invalid or contains dangerous operations
        
    Example:
        >>> sanitize_sql("SELECT * FROM table;")
        'SELECT * FROM table'
        
        >>> sanitize_sql("DROP TABLE users;")
        ValueError: Destructive or unsafe SQL keyword detected.
    """
    if not sql or not isinstance(sql, str):
        raise ValueError("SQL query must be a non-empty string")
        
    s = sql.strip()
    
    # Remove trailing semicolons and validate single statement
    s = s.rstrip(";")
    if ";" in s:
        raise ValueError("Only a single SQL statement is allowed.")
        
    # Validate query starts with allowed keywords
    if not ALLOWED_START.match(s):
        raise ValueError("Only SELECT/WITH statements are allowed.")
        
    # Block dangerous operations
    if DANGEROUS.search(s):
        raise ValueError("Destructive or unsafe SQL keyword detected.")
        
    return s

def has_group_by(sql: str) -> bool:
    """
    Check if the SQL query contains a GROUP BY clause.
    
    Args:
        sql: The SQL query string to check
        
    Returns:
        True if the query contains a GROUP BY clause, False otherwise
        
    Example:
        >>> has_group_by("SELECT category, SUM(amount) FROM expenses GROUP BY category")
        True
    """
    return bool(re.search(r"\bGROUP\s+BY\b", sql, re.IGNORECASE))


def has_aggregate(sql: str) -> bool:
    """
    Check if the SQL query contains any aggregate functions.
    
    Args:
        sql: The SQL query string to check
        
    Returns:
        True if the query contains aggregate functions (SUM, AVG, COUNT, etc.),
        False otherwise
        
    Example:
        >>> has_aggregate("SELECT AVG(amount) FROM expenses")
        True
    """
    return bool(AGG_FUNCS.search(sql))


def has_limit(sql: str) -> bool:
    """
    Check if the SQL query contains a LIMIT clause.
    
    Args:
        sql: The SQL query string to check
        
    Returns:
        True if the query contains a LIMIT clause with a numeric value,
        False otherwise
        
    Example:
        >>> has_limit("SELECT * FROM expenses LIMIT 10")
        True
    """
    return bool(re.search(r"\bLIMIT\s+\d+\b", sql, re.IGNORECASE))


def asked_for_all(nl: str) -> bool:
    """
    Check if the natural language query is requesting all results.
    
    Args:
        nl: The natural language query string
        
    Returns:
        True if the query contains words like 'all', 'everything', or 'entire',
        indicating the user wants all matching results
        
    Example:
        >>> asked_for_all("Show me all expenses")
        True
    """
    return bool(re.search(r"\b(all|everything|entire|complete|total|full)\b", nl.lower()))


def requested_k(nl: str) -> Optional[int]:
    """
    Extract a numeric limit from a natural language query.
    
    Looks for patterns like "top 10", "first 5", "last 3", etc.
    
    Args:
        nl: The natural language query string
        
    Returns:
        The numeric value from the query if found, otherwise None
        
    Example:
        >>> requested_k("Show me the top 5 expenses")
        5
        >>> requested_k("What are the last 3 transactions")
        3
    """
    # Look for patterns like "top 10", "first 5", etc.
    m = _TOPK_PAT.search(nl)
    if not m:
        return None
        
    # Extract the numeric value from the match
    try:
        # The first group is the word (top/bottom/first/last)
        # The second group is the number
        return int(m.group(2))
    except (IndexError, ValueError, AttributeError):
        return None


def apply_limit_policy(sql: str, nl_question: str, default_limit: int = 500) -> str:
    """
    Apply appropriate LIMIT to a SQL query based on the natural language question.
    
    This function applies the following rules:
    1. Preserves existing LIMIT clauses
    2. For scalar aggregates (with aggregation but no GROUP BY): no LIMIT
    3. For grouped aggregates: only add LIMIT if user asked for top/bottom K
    4. For detail rows: add default LIMIT unless user asked for 'all'
    
    Args:
        sql: The SQL query to modify
        nl_question: The original natural language question
        default_limit: Default limit to apply for detail queries (default: 500)
        
    Returns:
        The SQL query with appropriate LIMIT applied
        
    Example:
        >>> apply_limit_policy("SELECT * FROM expenses", "Show recent transactions")
        'SELECT * FROM expenses LIMIT 500'
    """
    # If query already has a LIMIT, leave it as is
    if has_limit(sql):
        return sql
        
    # Check query type
    has_agg = has_aggregate(sql)
    has_grp = has_group_by(sql)
    
    # Scalar aggregate (e.g., SELECT SUM(amount) FROM expenses): no limit
    if has_agg and not has_grp:
        return sql
        
    # Grouped aggregate (e.g., SELECT category, SUM(amount) FROM expenses GROUP BY category)
    if has_agg and has_grp:
        k = requested_k(nl_question)
        if k is not None:
            return f"{sql} LIMIT {max(1, k)}"
        # No explicit top/bottom -> no LIMIT
        return sql

    # Detail rows
    if asked_for_all(nl_question):
        return sql
    return f"{sql} LIMIT {default_limit}"