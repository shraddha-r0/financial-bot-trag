"""
Query Result Summarization Module

This module provides functionality to generate human-readable summaries of SQL query results
using a language model. It's designed to make database query results more accessible
and understandable to end users.
"""
import os
import json
from typing import Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

# Initialize the OpenAI client for Hugging Face inference
client = OpenAI(
    base_url="https://router.huggingface.co/v1",  # HF inference endpoint
    api_key=os.environ["HF_TOKEN"],  # Authentication token from environment
)

# Get the model name from environment or use a default
HF_MODEL = os.getenv("HF_MODEL", "openai/gpt-oss-20b")

# System prompt for the summarization model
SUMMARY_PROMPT = """\
You are a helpful financial assistant. Your task is to summarize database query results 
into clear, concise, and accurate 1-2 sentence summaries.

Guidelines:
- Use ONLY the numbers and data provided in the query results
- Include relevant totals, metrics, and date ranges when available
- Keep the summary factual, objective, and free from speculation
- Use natural language that a non-technical person would understand
- Never make up or assume information not present in the results
- For monetary values, include the currency (e.g., CLP for Chilean Pesos)
- If results are empty or show zero values, clearly state that no matching records were found
"""

def summarize_result(
    nl_question: str, 
    sql: str, 
    packaged_result: Dict[str, Any], 
    model: str = HF_MODEL
) -> str:
    """
    Generate a natural language summary of SQL query results.
    
    This function takes the raw query results and transforms them into a concise,
    human-readable summary using a language model. It handles different query types
    (detail, scalar_aggregate, grouped_aggregate) appropriately.
    
    Args:
        nl_question: The original natural language question that generated the query
        sql: The SQL query that was executed
        packaged_result: The processed query results from package_result()
        model: The name of the language model to use for summarization
        
    Returns:
        A string containing a natural language summary of the query results
        
    Raises:
        ValueError: If the input data is malformed or missing required fields
        RuntimeError: If there's an error communicating with the language model
    """
    if not all(key in packaged_result for key in ["type", "data"]):
        raise ValueError("packaged_result missing required fields")
    
    # Extract and format the data for the prompt
    q_type = packaged_result["type"]
    data_preview = packaged_result.get("data", {})
    
    # Format the data preview based on query type
    if q_type == "detail" and isinstance(data_preview, dict):
        # For detail queries, include both preview rows and totals
        preview = data_preview.get("preview", [])
        totals = data_preview.get("totals", {})
        
        # Format totals with currency symbols and proper formatting
        formatted_totals = {
            k: f"CLP {v:,.0f}" if isinstance(v, (int, float)) else v
            for k, v in totals.items()
        }
        
        data_str = (
            f"Query Type: Detailed transaction data\n"
            f"Preview Rows: {json.dumps(preview[:3], default=str)}\n"
            f"Totals: {formatted_totals}"
        )
    else:
        # For scalar or grouped aggregates, show the full result
        data_str = f"Query Type: {q_type}\nResults: {json.dumps(data_preview, default=str)}"

    try:
        # Construct the prompt for the language model
        messages = [
            {"role": "system", "content": SUMMARY_PROMPT},
            {
                "role": "user", 
                "content": (
                    f"Question: {nl_question}\n"
                    f"SQL Query: {sql}\n"
                    f"Query Results:\n{data_str}"
                )
            },
        ]

        # Call the language model to generate the summary
        response = client.chat.completions.create(
            model=model,
            temperature=0.2,  # Keep responses focused and deterministic
            messages=messages,
        )
        
        # Extract and clean the generated summary
        summary = response.choices[0].message.content.strip()
        return summary
        
    except Exception as e:
        # Provide a fallback summary if there's an error with the language model
        error_msg = (
            f"Error generating summary: {str(e)}. "
            "Here are the raw results instead."
        )
        return f"{error_msg}\n\n{data_str}"