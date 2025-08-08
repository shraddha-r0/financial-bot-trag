# app/sqlgen.py
import json
import os
import re
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

from .prompts import SYSTEM_SQL_PROMPT, build_user_prompt
from .sqlguard import sanitize_sql, apply_limit_policy

load_dotenv()  # loads HF_TOKEN from .env

HF_MODEL = os.environ["HF_MODEL"]
SCHEMA_PATH = Path(__file__).parent.parent / "data" / "clean" / "schema_snapshot.json"
MAX_RETRIES = 2
_FENCE = re.compile(r"^\s*```(?:sql)?\s*|\s*```\s*$", re.IGNORECASE)


SQL_KEYWORDS_FUNCS = {
    "select","from","where","and","or","as","group","by","order","limit","desc","asc",
    "on","join","inner","left","right","full","union","all","distinct","having",
    "sum","avg","count","min","max","date","strftime","now","start","of",
    "like","in","not","between","case","when","then","else","end"
}

# Create HF/OpenAI-compatible client
client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=os.environ["HF_TOKEN"],
)

def _strip_code_fences(s: str) -> str:
    return _FENCE.sub("", s).strip()
def _load_schema_json() -> str:
    if not SCHEMA_PATH.exists():
        raise FileNotFoundError(
            f"Schema snapshot not found at {SCHEMA_PATH}. "
            "Run: python -m scripts.snapshot_schema"
        )
    with SCHEMA_PATH.open(encoding="utf-8") as f:
        data = json.load(f)
    # truncate samples for smaller context window size
    for t in data.values():
        samples = t.get("samples", [])
        if len(samples) > 5:
            t["samples"] = samples[:5]
    return json.dumps(data, ensure_ascii=False)

def generate_sql(nl_question: str, model: str = HF_MODEL, temperature: float = 0.0) -> str:
    """
    Turn a natural language question into a single safe SQL statement using HF via OpenAI client.
    """
    schema_json = _load_schema_json()
    user_prompt = build_user_prompt(nl_question, schema_json)
    resp = client.chat.completions.create(
        model=model,
        temperature=temperature,
        messages=[
            {"role": "system", "content": SYSTEM_SQL_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    )
    sql = resp.choices[0].message.content or ""
    sql = _strip_code_fences(sql).strip()
    sql = sanitize_sql(sql)
    sql = apply_limit_policy(sql, nl_question, default_limit=500)

    return sql


def _get_allowed_identifiers(schema_json_str: str) -> set[str]:
    schema = json.loads(schema_json_str)
    allowed = set()
    for table, meta in schema.items():
        allowed.add(table.lower())
        for col in meta.get("columns", []):
            allowed.add(col["name"].lower())
    return allowed

def _find_invalid_identifiers(sql: str, allowed: set[str]):
    tokens = {t.lower() for t in re.split(r"[^\w]+", sql) if t}
    return [
        t for t in tokens
        if t not in allowed
        and t not in SQL_KEYWORDS_FUNCS
        and not t.isdigit()
    ]

# def generate_sql(nl_question: str) -> str:
#     schema_json = load_schema_json()
#     allowed = _get_allowed_identifiers(schema_json)

#     messages = [
#         {"role": "system", "content": SYSTEM_SQL_PROMPT},
#         {"role": "user", "content": build_user_prompt(nl_question, schema_json)},
#     ]

#     for attempt in range(MAX_RETRIES + 1):
#         resp = client.chat.completions.create(
#             model=HF_MODEL,
#             temperature=0,
#             messages=messages
#         )
#         sql = resp.choices[0].message.content.strip()

#         invalid = _find_invalid_identifiers(sql, allowed)

#         if not invalid:
#             return sql

#         if attempt < MAX_RETRIES:
#             print(f"⚠️ Invalid identifiers found: {invalid} — retrying...")
#             correction = (
#                 f"The SQL you wrote used invalid columns/tables: {invalid}.\n"
#                 f"Allowed identifiers: {sorted(list(allowed))}.\n"
#                 f"Rewrite the query so it ONLY uses the allowed identifiers."
#             )
#             messages.append({"role": "assistant", "content": sql})
#             messages.append({"role": "user", "content": correction})
#         else:
#             raise ValueError(f"Invalid identifiers after {MAX_RETRIES+1} attempts: {invalid}")

#     return sql