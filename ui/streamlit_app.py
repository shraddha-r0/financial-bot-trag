"""
Financial Bot — Tabular RAG Web Interface

A Streamlit-based web interface for the Financial Bot that allows users to ask
natural language questions about their financial data and get SQL-based answers.

Features:
- Natural language to SQL conversion
- Interactive data visualization
- Query result summarization
- SQL query inspection
"""
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

# Add the project root to the Python path to enable local imports
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

import pandas as pd
import streamlit as st

# Import application modules
from app.sqlgen import generate_sql
from app.executor import run_sql
from app.packager import package_result
from app.summarizer import summarize_result

def setup_page() -> None:
    """
    Configure the Streamlit page settings and display the header.
    """
    st.set_page_config(
        page_title="Financial Bot — Tabular RAG",
        page_icon="",
        layout="centered"
    )
    st.title("")
    st.caption("Ask in plain English. I'll generate SQL, run it on your SQLite DB, and summarize the result.")

def render_sidebar() -> Dict[str, Any]:
    """
    Render the sidebar with configuration options.
    
    Returns:
        Dictionary containing the user's settings
    """
    with st.sidebar:
        st.header("Settings")
        settings = {
            "db_path": st.text_input(
                "SQLite DB path",
                "data/clean/finances.db",
                help="Path to your SQLite database file"
            ),
            "show_sql": st.checkbox(
                "Show SQL",
                value=True,
                help="Display the generated SQL query"
            ),
            "verbose": st.checkbox(
                "Verbose preview",
                value=False,
                help="Show additional details in the preview"
            ),
            "debug": st.checkbox(
                "Debug mode",
                value=False,
                help="Enable debug output"
            )
        }
        
        st.markdown("---")
        st.caption("")
        
        return settings

def get_user_input() -> str:
    """
    Get the user's question via the UI.
    
    Returns:
        The user's question as a string
    """
    return st.text_input(
        "Your question",
        "How much did I spend on takeout last month?",
        help="Ask a question about your financial data in plain English"
    )

def convert_to_dataframe(rows: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Convert a list of dictionaries to a pandas DataFrame.
    
    Args:
        rows: List of dictionaries representing rows of data
        
    Returns:
        A pandas DataFrame containing the data
    """
    return pd.DataFrame(rows) if rows else pd.DataFrame()

def display_results(
    question: str,
    sql: str,
    packaged_result: Dict[str, Any],
    exec_result: Dict[str, Any],
    show_sql: bool = True
) -> None:
    """
    Display the query results in the Streamlit UI.
    
    Args:
        question: The original user question
        sql: The generated SQL query
        packaged_result: The packaged query results
        exec_result: The raw execution results
        show_sql: Whether to display the SQL query
    """
    # Display the natural language answer
    st.subheader("Answer")
    st.write(packaged_result.get("summary", "No summary available."))
    
    # Show the SQL query if enabled
    if show_sql:
        st.subheader("SQL")
        st.code(sql, language="sql")
    
    # Show result metadata
    st.subheader("Result")
    result_type = exec_result.get("type", "unknown")
    row_count = exec_result.get("row_count", 0)
    elapsed_ms = exec_result.get("elapsed_ms", 0)
    st.write(f"Type: `{result_type}` · Rows: `{row_count}` · {elapsed_ms:.0f} ms")
    
    # Display the actual data
    data = packaged_result.get("data", {})
    
    if result_type == "detail":
        # For detail queries, show a preview and totals if available
        preview = data.get("preview", [])
        totals = data.get("totals", {})
        
        if preview:
            st.dataframe(convert_to_dataframe(preview), use_container_width=True)
        
        if totals:
            st.caption("Totals")
            st.json(totals)
    else:
        # For grouped or scalar queries, display the results directly
        if isinstance(data, list):
            st.dataframe(convert_to_dataframe(data), use_container_width=True)
        else:
            st.json(data)

def process_question(question: str, db_path: str) -> Dict[str, Any]:
    """
    Process a natural language question and return the results.
    
    Args:
        question: The natural language question
        db_path: Path to the SQLite database file
        
    Returns:
        Dictionary containing the SQL, execution results, and packaged results
    """
    try:
        # Generate SQL from natural language
        sql = generate_sql(question)
        
        # Execute the SQL query
        exec_result = run_sql(sql, db_path=db_path)
        
        # Package the results for display
        packaged_result = package_result(exec_result)
        
        # Generate a natural language summary
        answer = summarize_result(question, sql, packaged_result)
        packaged_result["summary"] = answer
        
        return {
            "sql": sql,
            "exec_result": exec_result,
            "packaged_result": packaged_result
        }
    except Exception as e:
        st.error(f"Error processing your question: {str(e)}")
        raise

def main() -> None:
    """
    Main function to run the Streamlit application.
    """
    # Set up the page
    setup_page()
    
    # Get user settings from the sidebar
    settings = render_sidebar()
    
    # Get the user's question
    question = get_user_input()
    
    # Process the question when the button is clicked
    if st.button("Ask", key="ask_button"):
        with st.spinner("Processing your question..."):
            try:
                # Process the question and get results
                results = process_question(question, settings["db_path"])
                
                # Display the results
                display_results(
                    question=question,
                    sql=results["sql"],
                    packaged_result=results["packaged_result"],
                    exec_result=results["exec_result"],
                    show_sql=settings["show_sql"]
                )
                
                # Debug output if enabled
                if settings["debug"]:
                    with st.expander("Debug Information"):
                        st.json({
                            "question": question,
                            "settings": settings,
                            "exec_result": results["exec_result"]
                        })
                        
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                if settings["debug"]:
                    import traceback
                    st.text(traceback.format_exc())

if __name__ == "__main__":
    main()