"""
Stage 3: Full Schema Generation
- Input: IntentModel + ArchitectureModel
- Output: AppSchemaModel
- Model: gemini-1.5-flash (with structured output)
- Temperature: 0.05 (nearly deterministic)
"""

import json
from ..schemas.intent import IntentModel
from ..schemas.architecture import ArchitectureModel
from ..schemas.app_schema import AppSchemaModel
from ..llm.gemini_client import call_gemini
from ..prompts.stage3 import STAGE3_SYSTEM_PROMPT, build_stage3_user_prompt
from .stage1_intent import extract_json

async def run_stage3(intent: IntentModel, arch: ArchitectureModel) -> AppSchemaModel:
    system = STAGE3_SYSTEM_PROMPT
    intent_json = intent.model_dump_json(indent=2)
    arch_json = arch.model_dump_json(indent=2)
    user = build_stage3_user_prompt(intent_json, arch_json)
    
    raw = await call_gemini(
        system=system,
        user=user,
        temperature=0.05,
        model="gemini-1.5-flash"
    )
    data = extract_json(raw)
    return AppSchemaModel(**data)
