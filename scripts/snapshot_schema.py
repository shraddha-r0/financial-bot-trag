
"""
Database Schema Snapshot Utility

This script generates a JSON snapshot of the database schema, including column definitions
and sample data. This snapshot is used by the financial bot to understand the database
structure when generating SQL queries from natural language questions.
"""
import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, TypedDict

# Define type hints for better code clarity
class ColumnDef(TypedDict):
    name: str
    type: str

class TableSchema(TypedDict):
    columns: List[ColumnDef]
    samples: List[Dict[str, Any]]

# Path to the SQLite database file
DB_PATH = Path(__file__).parent.parent / "data" / "clean" / "finances.db"

# Output path for the schema snapshot
OUT_PATH = Path(__file__).parent.parent / "data" / "clean" / "schema_snapshot.json"

# Hardcoded schema definition based on the database structure
# This defines the expected tables and their columns in the database
SCHEMA: Dict[str, Dict[str, List[ColumnDef]]] = {
    "expenses": {
        "columns": [
            {"name": "date", "type": "DATE"},
            {"name": "category", "type": "TEXT"},
            {"name": "tags", "type": "TEXT"},
            {"name": "amount_clp", "type": "REAL"},
            {"name": "description", "type": "TEXT"},
            {"name": "day", "type": "TEXT"}
        ]
    },
    "incomes": {
        "columns": [
            {"name": "date", "type": "DATE"},
            {"name": "category", "type": "TEXT"},
            {"name": "tags", "type": "TEXT"},
            {"name": "amount_clp", "type": "REAL"},
            {"name": "description", "type": "TEXT"},
            {"name": "day", "type": "TEXT"}
        ]
    }
}

def get_sample_rows(table: str, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Retrieve sample rows from a database table.
    
    Args:
        table: Name of the table to query
        limit: Maximum number of sample rows to return (default: 5)
        
    Returns:
        A list of dictionaries, where each dictionary represents a row
        with column names as keys and row values as values.
        
    Raises:
        sqlite3.Error: If there's an error executing the query
        ValueError: If the table doesn't exist or is not accessible
    """
    try:
        with sqlite3.connect(DB_PATH) as conn:
            # Configure connection to return rows as dictionaries
            conn.row_factory = sqlite3.Row
            
            # Use parameterized query to prevent SQL injection
            query = f"SELECT * FROM {sqlite3.quote_identifier(table)} LIMIT ?"
            cur = conn.execute(query, (limit,))
            
            # Convert rows to dictionaries for JSON serialization
            return [dict(r) for r in cur.fetchall()]
    except sqlite3.Error as e:
        raise ValueError(f"Error querying table '{table}': {e}")

def main() -> None:
    """
    Main function to generate and save a schema snapshot.
    
    This function:
    1. Retrieves sample data for each table defined in SCHEMA
    2. Combines the schema definition with sample data
    3. Saves the result as a JSON file
    
    The output file is used by the financial bot to understand the database structure
    when generating SQL queries from natural language questions.
    """
    try:
        schema_with_samples: Dict[str, TableSchema] = {}
        
        # Process each table in the schema
        for table, meta in SCHEMA.items():
            try:
                schema_with_samples[table] = {
                    "columns": meta["columns"],
                    "samples": get_sample_rows(table)
                }
                print(f"✓ Processed table: {table}")
            except Exception as e:
                print(f"⚠️  Warning: {e}")
                continue
        
        # Ensure the output directory exists
        OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        
        # Write the schema snapshot to a JSON file
        with open(OUT_PATH, "w", encoding="utf-8") as f:
            json.dump(schema_with_samples, f, ensure_ascii=False, indent=2)
            
        print(f"✅ Successfully wrote schema snapshot to {OUT_PATH}")
        
    except Exception as e:
        print(f"❌ Error generating schema snapshot: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    import sys
    main()