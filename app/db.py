from contextlib import contextmanager
from pathlib import Path
import sqlite3

DB_PATH = Path("../data/clean/finances.db")

@contextmanager
def connect(db_path: Path = DB_PATH):
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def run(sql: str, params: tuple = ()):
    with connect() as c:
        cur = c.execute(sql, params)
        if cur.description is None:
            return None
        return [dict(r) for r in cur.fetchall()]