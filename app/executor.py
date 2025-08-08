import sqlite3
import time
import re
from pathlib import Path

DB_PATH = Path("../data/clean/finances.db")

_AGG_FUNCS = re.compile(r"\b(SUM|AVG|COUNT|MIN|MAX)\s*\(", re.IGNORECASE)
_GROUP_BY = re.compile(r"\bGROUP\s+BY\b", re.IGNORECASE)

def detect_query_type(sql: str) -> str:
    """
    Classify the SQL query type: scalar_aggregate, grouped_aggregate, or detail.
    """
    has_agg = bool(_AGG_FUNCS.search(sql))
    has_group = bool(_GROUP_BY.search(sql))

    if has_agg and not has_group:
        return "scalar_aggregate"
    if has_group:
        return "grouped_aggregate"
    return "detail"

def run_sql(sql: str, db_path: Path = DB_PATH, max_rows: int = 1000):
    """
    Execute SQL against the finances DB, return result package.
    Caps detail rows to max_rows.
    """
    if not Path(db_path).exists():
        raise FileNotFoundError(f"Database not found at {db_path.resolve()}")

    q_type = detect_query_type(sql)

    start = time.time()
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.execute(sql)
        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
    elapsed_ms = (time.time() - start) * 1000

    row_count = len(rows)
    # Cap preview for detail queries
    if q_type == "detail" and row_count > max_rows:
        preview_rows = rows[:max_rows]
    else:
        preview_rows = rows

    preview_as_dicts = [dict(r) for r in preview_rows]

    return {
        "type": q_type,
        "columns": columns,
        "rows": preview_as_dicts,
        "row_count": row_count,
        "elapsed_ms": elapsed_ms,
    }