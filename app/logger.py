import csv
import os
from datetime import datetime
from pathlib import Path

LOG_PATH = Path(__file__).parent.parent / "logs" / "sql_calls.csv"

def log_sql_call(question: str, sql: str, row_count: int, sample_rows=None):
    """Append a single SQL generation/execution to logs/sql_calls.csv."""
    LOG_PATH.parent.mkdir(exist_ok=True)
    exists = LOG_PATH.exists()

    with open(LOG_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not exists:
            writer.writerow(["timestamp", "question", "sql", "row_count", "sample_rows"])
        writer.writerow([
            datetime.now().astimezone().isoformat(),
            question,
            sql,
            row_count,
            repr(sample_rows) if sample_rows else ""
        ])