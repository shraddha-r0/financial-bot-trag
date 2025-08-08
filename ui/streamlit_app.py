import sys
from pathlib import Path

# Add the project root to the Python path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

import pandas as pd
import streamlit as st

from app.sqlgen import generate_sql
from app.executor import run_sql
from app.packager import package_result
from app.summarizer import summarize_result

st.set_page_config(page_title="Financial Bot — Tabular RAG", page_icon="💸", layout="centered")

st.title("💸 Financial Bot — Tabular RAG")
st.caption("Ask in plain English. I’ll generate SQL, run it on your SQLite DB, and summarize the result.")

with st.sidebar:
    st.header("Settings")
    db_path = st.text_input("SQLite DB path", "data/clean/finances.db")
    show_sql = st.checkbox("Show SQL", value=True)
    verbose = st.checkbox("Verbose preview", value=False)
    debug = st.checkbox("Debug schema print", value=False)
    st.markdown("---")
    st.caption("Make sure HF_TOKEN is set in your environment (or .env).")

q = st.text_input("Your question", "How much did I spend on takeout last month?")
ask = st.button("Ask")

def to_df(rows):
    if not rows: return pd.DataFrame()
    return pd.DataFrame(rows)

if ask:
    try:
        # NL -> SQL
        sql = generate_sql(q)
        # Execute
        exec_res = run_sql(sql, db_path=db_path)
        # Package
        packaged = package_result(exec_res)
        # Summarize
        answer = summarize_result(q, sql, packaged)

        st.subheader("Answer")
        st.write(answer)

        if show_sql:
            st.subheader("SQL")
            st.code(sql, language="sql")

        st.subheader("Result")
        st.write(f"Type: `{exec_res['type']}` · Rows: `{exec_res['row_count']}` · {exec_res['elapsed_ms']:.0f} ms")

        # Render preview
        data = packaged.get("data")
        if exec_res["type"] == "detail":
            preview = data.get("preview", [])
            totals = data.get("totals", {})
            if preview:
                st.dataframe(to_df(preview), use_container_width=True)
            if totals:
                st.caption("Totals")
                st.json(totals)
        else:
            # grouped/scalar
            if isinstance(data, list):
                st.dataframe(to_df(data), use_container_width=True)
            else:
                st.json(data)

    except Exception as e:
        st.error(str(e))