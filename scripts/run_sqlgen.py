import sys
from app.sqlgen import generate_sql


def main():
    if len(sys.argv) < 2:
        print("Usage: python -m scripts.run_sqlgen \"your question here\"")
        sys.exit(1)
    question = " ".join(sys.argv[1:])
    sql = generate_sql(question)
    print(sql)

if __name__ == "__main__":
    main()