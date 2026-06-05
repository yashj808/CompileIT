"""
Stage 1: Intent Extraction
- Input: raw user prompt (string)
- Output: IntentModel (validated Pydantic object)
- Model: gemini-1.5-flash
- Temperature: 0.1 (deterministic)
- Must return valid JSON matching IntentModel schema
- Must identify and log ambiguities
- Must handle vague prompts by making documented assumptions
"""

import json
from ..schemas.intent import IntentModel
from ..llm.gemini_client import call_gemini
from ..prompts.stage1 import STAGE1_SYSTEM_PROMPT, build_stage1_user_prompt

async def run_stage1(user_prompt: str) -> IntentModel:
    messages = build_stage1_user_prompt(user_prompt)
    raw = await call_gemini(
        system=STAGE1_SYSTEM_PROMPT,
        user=messages,
        temperature=0.1,
        model="gemini-1.5-flash"
    )
    data = extract_json(raw)
    return IntentModel(**data)

def extract_json(text: str) -> dict:
    """Strip markdown fences, extract JSON. Raise ValueError if not parseable."""
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    text = text.strip().rstrip("```").strip()
    return json.loads(text)
