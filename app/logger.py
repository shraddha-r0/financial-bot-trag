"""
Logging Module for SQL Query Tracking

This module provides functionality to log SQL queries and their execution details
for auditing, debugging, and analysis purposes. Logs are stored in CSV format
for easy processing and review.
"""
import csv
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Optional, Dict, List, Union

# Path to the log file
LOG_PATH = Path(__file__).parent.parent / "logs" / "sql_calls.csv"

def log_sql_call(question: str, sql: str, row_count: int, sample_rows: Optional[Any] = None) -> None:
    """
    Log SQL query execution details to a CSV file.
    
    This function appends a new entry to the SQL call log with the following information:
    - Timestamp of the query
    - Original user question
    - Generated SQL query
    - Number of rows returned
    - Sample of the returned rows (if provided)
    
    The log file is created if it doesn't exist, with appropriate headers.
    
    Args:
        question: The original natural language question that generated the SQL
        sql: The SQL query that was executed
        row_count: Number of rows returned by the query
        sample_rows: Optional sample of the returned rows (first few rows)
        
    Example:
        >>> log_sql_call(
        ...     question="Show me expenses over $100",
        ...     sql="SELECT * FROM expenses WHERE amount > 100",
        ...     row_count=5,
        ...     sample_rows=[{"date": "2023-01-01", "amount": 150.0}]
        ... )
    """
    try:
        # Ensure the logs directory exists
        LOG_PATH.parent.mkdir(exist_ok=True)
        
        # Check if we need to write headers (new file)
        file_exists = LOG_PATH.exists()
        
        with open(LOG_PATH, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            
            # Write headers if this is a new file
            if not file_exists:
                headers = ["timestamp", "question", "sql", "row_count", "sample_rows"]
                writer.writerow(headers)
            
            # Prepare the log entry
            log_entry = [
                datetime.now().astimezone().isoformat(),  # Timezone-aware timestamp
                question,                                 # Original question
                sql,                                      # Executed SQL
                row_count,                                # Number of rows returned
                repr(sample_rows) if sample_rows else ""   # Sample data (if any)
            ]
            
            # Write the log entry
            writer.writerow(log_entry)
            
    except Exception as e:
        # Log to stderr if file logging fails, but don't crash the application
        import sys
        print(f"Warning: Failed to log SQL call: {e}", file=sys.stderr)