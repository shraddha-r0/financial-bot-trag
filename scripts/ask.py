import sys
from pathlib import Path

# Add the project root to the Python path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)
import argparse
from app.sqlgen import generate_sql
from app.executor import run_sql
from app.packager import package_result
from app.summarizer import summarize_result
from app.logger import log_sql_call

def main():
    parser = argparse.ArgumentParser(description="Ask a natural language question about your finances.")
    parser.add_argument("question", help="The question to ask, in quotes.")
    parser.add_argument("--verbose", action="store_true", help="Show preview rows if available.")
    parser.add_argument("--db", default="data/clean/finances.db", help="Path to SQLite database.")
    args = parser.parse_args()

    # NL → SQL
    sql = generate_sql(args.question)
    
    # Execute
    exec_res = run_sql(sql, db_path=args.db)
    print(exec_res)
    # Package
    packaged = package_result(exec_res)
    
    # Summarize
    summary = summarize_result(args.question, sql, packaged)

    # Log
    row_count = len(exec_res["rows"]) if exec_res["rows"] else 0
    sample = exec_res["rows"][ :3] if exec_res["rows"] else []
    log_sql_call(args.question, sql, row_count, sample)
    
    # Output
    print("\n=== Answer ===")
    print(summary)
    print("\n=== SQL ===")
    print(sql)

    if args.verbose:
        print("\n=== Preview Rows ===")
        if packaged["type"] == "detail":
            for row in packaged["data"]["preview"]:
                print(row)
        else:
            print(packaged["data"])

if __name__ == "__main__":
    main()