# app/sqlguard.py
import re

ALLOWED_START = re.compile(r"^\s*(SELECT|WITH)\b", re.IGNORECASE)
DANGEROUS = re.compile(r"\b(DROP|DELETE|UPDATE|INSERT|ALTER|REPLACE|ATTACH|DETACH|VACUUM|PRAGMA)\b", re.IGNORECASE)
AGG_FUNCS = re.compile(r"\b(SUM|AVG|COUNT|MIN|MAX)\s*\(", re.IGNORECASE)

def sanitize_sql(sql: str) -> str:
    """
    Allow only a single SELECT/WITH statement.
    Strip trailing semicolons. Block dangerous keywords.
    """
    s = sql.strip()
    # Kill trailing semicolons and ensure single statement
    s = s.rstrip(";")
    if ";" in s:
        raise ValueError("Only a single SQL statement is allowed.")
    if not ALLOWED_START.match(s):
        raise ValueError("Only SELECT/WITH statements are allowed.")
    if DANGEROUS.search(s):
        raise ValueError("Destructive or unsafe SQL keyword detected.")
    return s

def has_group_by(sql: str) -> bool:
    return bool(re.search(r"\bGROUP\s+BY\b", sql, re.IGNORECASE))

def has_aggregate(sql: str) -> bool:
    return bool(AGG_FUNCS.search(sql))

def has_limit(sql: str) -> bool:
    return bool(re.search(r"\bLIMIT\s+\d+\b", sql, re.IGNORECASE))

def asked_for_all(nl: str) -> bool:
    return bool(re.search(r"\b(all|everything|entire)\b", nl.lower()))

_TOPK_PAT = re.compile(r"\btop\s+(\d+)\b|\bbottom\s+(\d+)\b|\bfirst\s+(\d+)\b|\blast\s+(\d+)\b", re.IGNORECASE)

def requested_k(nl: str) -> int | None:
    m = _TOPK_PAT.search(nl)
    if not m:
        return None
    # Return first captured int found
    for i in range(1, 5):
        if m.group(i):
            try:
                return int(m.group(i))
            except ValueError:
                pass
    return None

def apply_limit_policy(sql: str, nl_question: str, default_limit: int = 500) -> str:
    """
    LIMIT rules:
    - Scalar aggregates (agg, no GROUP BY): no LIMIT.
    - Grouped aggregates: only add LIMIT if user asked for top/bottom K and no LIMIT present.
    - Non-aggregates (detail rows): add LIMIT default_limit unless user asked for 'all'.
    """
    if has_limit(sql):
        return sql  # respect existing LIMIT

    agg = has_aggregate(sql)
    grp = has_group_by(sql)

    # Scalar aggregate: no limit
    if agg and not grp:
        return sql

    # Grouped aggregate
    if agg and grp:
        k = requested_k(nl_question)
        if k is not None:
            return f"{sql} LIMIT {max(1, k)}"
        # No explicit top/bottom -> no LIMIT
        return sql

    # Detail rows
    if asked_for_all(nl_question):
        return sql
    return f"{sql} LIMIT {default_limit}"