# scripts/snapshot_schema.py
import json
from pathlib import Path
import sqlite3

DB_PATH = Path(__file__).parent.parent / "data" / "clean" / "finances.db"
OUT_PATH = Path(__file__).parent.parent / "data" / "clean" / "schema_snapshot.json"

# Hardcoded schema based on your DDL
SCHEMA = {
    "expenses": {
        "columns": [
            {"name": "date", "type": "DATE"},
            {"name": "category", "type": "TEXT"},
            {"name": "tags", "type": "TEXT"},
            {"name": "expense", "type": "REAL"},
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
            {"name": "income", "type": "REAL"},
            {"name": "amount_clp", "type": "REAL"},
            {"name": "description", "type": "TEXT"},
            {"name": "day", "type": "TEXT"}
        ]
    }
}

def get_sample_rows(table, limit=5):
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.execute(f"SELECT * FROM {table} LIMIT {limit}")
        return [dict(r) for r in cur.fetchall()]

def main():
    schema_with_samples = {}
    for table, meta in SCHEMA.items():
        schema_with_samples[table] = {
            "columns": meta["columns"],
            "samples": get_sample_rows(table)
        }
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(schema_with_samples, f, ensure_ascii=False, indent=2)
    print(f"✅ Wrote schema snapshot to {OUT_PATH}")

if __name__ == "__main__":
    main()