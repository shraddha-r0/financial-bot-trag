import sys
from app.sqlgen import generate_sql
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

def main():
    if len(sys.argv) < 2:
        print("Usage: python -m scripts.run_sqlgen \"your question here\"")
        sys.exit(1)
    question = " ".join(sys.argv[1:])
    sql = generate_sql(question)
    print(sql)

if __name__ == "__main__":
    main()