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

SCHEMA_PATH = Path("data/clean/schema_snapshot.json")
_FENCE = re.compile(r"^\s*```(?:sql)?\s*|\s*```\s*$", re.IGNORECASE)

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
    data = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    for t in data.values():
        samples = t.get("samples", [])
        if len(samples) > 5:
            t["samples"] = samples[:5]
    return json.dumps(data, ensure_ascii=False)

def generate_sql(nl_question: str, model: str = "openai/gpt-oss-20b", temperature: float = 0.1) -> str:
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