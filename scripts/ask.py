"""
Command-line interface for the Financial Bot.

This script allows users to ask natural language questions about their finances
and get SQL-based answers. It's designed to be used as a command-line tool.
"""
import sys
import argparse
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add the project root to the Python path to enable local imports
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

# Import application modules
from app.sqlgen import generate_sql
from app.executor import run_sql
from app.packager import package_result
from app.summarizer import summarize_result
from app.logger import log_sql_call

def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments.
    
    Returns:
        Parsed command-line arguments
    """
    parser = argparse.ArgumentParser(
        description="Ask a natural language question about your finances.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "question",
        type=str,
        help="The question to ask, in quotes."
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show preview rows if available."
    )
    parser.add_argument(
        "--db",
        type=str,
        default="data/clean/finances.db",
        help="Path to SQLite database file."
    )
    return parser.parse_args()

def process_question(question: str, db_path: str) -> Dict[str, Any]:
    """
    Process a natural language question and return the results.
    
    Args:
        question: The natural language question to process
        db_path: Path to the SQLite database file
        
    Returns:
        Dictionary containing the SQL, execution results, and summary
    """
    try:
        # Step 1: Generate SQL from natural language
        sql = generate_sql(question)
        
        # Step 2: Execute the generated SQL
        exec_result = run_sql(sql, db_path=db_path)
        
        # Step 3: Package the results for display
        packaged_result = package_result(exec_result)
        
        # Step 4: Generate a natural language summary
        summary = summarize_result(question, sql, packaged_result)
        
        # Log the query for analytics
        row_count = len(exec_result["rows"]) if exec_result["rows"] else 0
        sample = exec_result["rows"][:3] if exec_result["rows"] else []
        log_sql_call(question, sql, row_count, sample)
        
        return {
            "sql": sql,
            "summary": summary,
            "packaged_result": packaged_result,
            "exec_result": exec_result
        }
    except Exception as e:
        print(f"Error processing question: {e}", file=sys.stderr)
        raise

def display_results(summary: str, sql: str, packaged_result: Dict[str, Any], verbose: bool = False) -> None:
    """
    Display the results of a query.
    
    Args:
        summary: Natural language summary of the results
        sql: The SQL query that was executed
        packaged_result: The packaged query results
        verbose: Whether to show detailed preview rows
    """
    print("\n=== Answer ===")
    print(summary)
    print("\n=== SQL ===")
    print(sql)
    
    if verbose:
        print("\n=== Preview Rows ===")
        if packaged_result["type"] == "detail":
            for row in packaged_result["data"]["preview"]:
                print(row)
        else:
            print(packaged_result["data"])

def main() -> None:
    """
    Main entry point for the command-line interface.
    
    This function:
    1. Parses command-line arguments
    2. Processes the user's question
    3. Displays the results
    """
    try:
        # Parse command-line arguments
        args = parse_arguments()
        
        # Process the question and get results
        results = process_question(args.question, args.db)
        
        # Display the results
        display_results(
            results["summary"],
            results["sql"],
            results["packaged_result"],
            args.verbose
        )
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()