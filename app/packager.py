from typing import Dict, List, Any, TypedDict

# Type aliases for better code readability
QueryResult = Dict[str, Any]
PackagedResult = Dict[str, Any]

# Type definitions for structured returns
class DetailResult(TypedDict):
    preview: List[Dict[str, Any]]   
    totals: Dict[str, float]

def package_result(
    exec_result: QueryResult, 
    max_groups: int = 20, 
    max_detail_rows: int = 20
) -> PackagedResult:
    """
    Transform raw SQL execution results into a structured, analysis-ready format.
    
    Processes query results based on their type (detail, scalar_aggregate, or grouped_aggregate)
    and applies appropriate formatting, sorting, and summarization.
    
    Args:
        exec_result: Raw result from SQL execution containing:
            - type: Query type ('detail', 'scalar_aggregate', or 'grouped_aggregate')
            - columns: List of column names
            - rows: List of result rows as dictionaries
            - row_count: Total number of rows
            - elapsed_ms: Query execution time in milliseconds
        max_groups: Maximum number of groups to return for grouped_aggregate queries
        max_detail_rows: Maximum number of rows to return for detail queries
        
    Returns:
        Dict containing processed results with structure depending on query type:
        
        For 'detail' queries:
            - type: 'detail'
            - columns: List of column names
            - row_count: Total number of rows
            - elapsed_ms: Query execution time
            - data: {
                'preview': List of row dicts (up to max_detail_rows)
                'totals': Dict of column sums for numeric fields
              }
              
        For 'scalar_aggregate' queries:
            - type: 'scalar_aggregate'
            - columns: List of column names
            - row_count: Always 1
            - elapsed_ms: Query execution time
            - data: Single row result as a dict
            
        For 'grouped_aggregate' queries:
            - type: 'grouped_aggregate'
            - columns: List of column names
            - row_count: Number of groups (up to max_groups)
            - elapsed_ms: Query execution time
            - data: List of group result dicts, sorted by first numeric column
    """
    # Extract and validate input
    q_type = exec_result["type"]
    cols = exec_result["columns"]
    rows = exec_result["rows"]
    row_count = exec_result["row_count"]

    # Initialize base result structure
    packaged: PackagedResult = {
        "type": q_type,
        "columns": cols,
        "row_count": row_count,
        "elapsed_ms": exec_result["elapsed_ms"],
    }

    if q_type == "scalar_aggregate":
        # For scalar aggregates, return the single result row
        packaged["data"] = rows[0] if rows else {}
    
    elif q_type == "grouped_aggregate":
        # Find first numeric column for sorting (skipping the first column which is typically the group key)
        numeric_col = None
        if len(cols) > 1 and rows:
            for c in cols[1:]:  # Skip first column (likely group key)
                if isinstance(rows[0].get(c), (int, float)):
                    numeric_col = c
                    break
                    
        if numeric_col:
            # Sort groups by numeric column in descending order
            rows_sorted = sorted(
                rows, 
                key=lambda r: r.get(numeric_col, 0) or 0, 
                reverse=True
            )
        else:
            rows_sorted = rows
            
        # Apply group limit
        packaged["data"] = rows_sorted[:max_groups]
    
    else:  # detail query
        # Get preview rows (limited by max_detail_rows)
        preview = rows[:max_detail_rows]
        
        # Calculate totals for known numeric columns
        totals = {}
        for col in ("amount_clp", "expense", "income"):
            if col in cols and rows and isinstance(rows[0].get(col), (int, float)):
                totals[f"total_{col}"] = sum(
                    float(row.get(col, 0) or 0) 
                    for row in rows 
                    if isinstance(row.get(col), (int, float))
                )
                
        packaged["data"] = {
            "preview": preview,
            "totals": totals
        }

    return packaged