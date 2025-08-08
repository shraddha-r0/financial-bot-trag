import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()  # Loads HF_TOKEN from .env

client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=os.environ["HF_TOKEN"],
)

HF_MODEL = os.environ["HF_MODEL"]

SUMMARY_PROMPT = """\
You are a financial assistant. Summarize the given query result in 1–2 sentences.
- Use only the numbers and data provided.
- Include relevant totals and date ranges if visible.
- Keep it short and factual.
- Do not hallucinate data.
"""

def summarize_result(nl_question: str, sql: str, packaged_result: dict, model: str = HF_MODEL) -> str:
    """
    Summarize the result package into a short, human-readable answer.
    """
    # We only send a compact preview to save tokens
    data_preview = packaged_result.get("data")
    if isinstance(data_preview, dict) and "preview" in data_preview:
        # For detail queries
        preview = data_preview["preview"]
        totals = data_preview.get("totals", {})
        data_str = f"Preview rows: {preview}\nTotals: {totals}"
    else:
        data_str = str(data_preview)

    messages = [
        {"role": "system", "content": SUMMARY_PROMPT},
        {"role": "user", "content": f"Question: {nl_question}\nSQL: {sql}\nResult: {data_str}"},
    ]

    resp = client.chat.completions.create(
        model=model,
        temperature=0.2,
        messages=messages,
    )
    return resp.choices[0].message.content.strip()