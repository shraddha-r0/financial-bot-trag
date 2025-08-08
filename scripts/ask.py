import sys
import argparse
from app.sqlgen import generate_sql
from app.executor import run_sql
from app.packager import package_result
from app.summarizer import summarize_result

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
    
    # Package
    packaged = package_result(exec_res)
    
    # Summarize
    summary = summarize_result(args.question, sql, packaged)

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