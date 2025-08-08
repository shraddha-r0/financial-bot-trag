def package_result(exec_result: dict, max_groups: int = 20, max_detail_rows: int = 20) -> dict:
    """
    Turn raw executor result into a summary-friendly dict.
    """
    q_type = exec_result["type"]
    cols = exec_result["columns"]
    rows = exec_result["rows"]
    row_count = exec_result["row_count"]

    packaged = {
        "type": q_type,
        "columns": cols,
        "row_count": row_count,
        "elapsed_ms": exec_result["elapsed_ms"],
    }

    if q_type == "scalar_aggregate":
        # Expect 1 row, 1+ numeric columns
        packaged["data"] = rows[0] if rows else {}
    
    elif q_type == "grouped_aggregate":
        # Sort by first numeric column (if exists)
        numeric_col = None
        if len(cols) > 1:
            for c in cols[1:]:
                if isinstance(rows[0][c], (int, float)):
                    numeric_col = c
                    break
        if numeric_col:
            rows_sorted = sorted(rows, key=lambda r: r[numeric_col] or 0, reverse=True)
        else:
            rows_sorted = rows
        packaged["data"] = rows_sorted[:max_groups]
    
    else:  # detail
        preview = rows[:max_detail_rows]
        totals = {}
        for col in ("amount_clp", "expense", "income"):
            if col in cols:
                totals[f"total_{col}"] = sum(r[col] or 0 for r in rows if isinstance(r[col], (int, float)))
        packaged["data"] = {
            "preview": preview,
            "totals": totals,
        }

    return packaged