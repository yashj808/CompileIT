"""
Stage 2: Architecture Design
- Input: IntentModel
- Output: ArchitectureModel
- Model: gemini-1.5-pro (higher reasoning for system design)
- Temperature: 0.1
- MUST generate db_tables for every entity mentioned in intent
- MUST generate API endpoints for every CRUD operation needed
- MUST generate a UI page for every feature
- MUST generate auth_config covering all roles
"""

from ..schemas.intent import IntentModel
from ..schemas.architecture import ArchitectureModel
from ..llm.gemini_client import call_gemini
from ..prompts.stage2 import STAGE2_SYSTEM_PROMPT, build_stage2_user_prompt
from .stage1_intent import extract_json

async def run_stage2(intent: IntentModel) -> ArchitectureModel:
    system = STAGE2_SYSTEM_PROMPT
    user = build_stage2_user_prompt(intent.model_dump_json(indent=2))
    raw = await call_gemini(system=system, user=user, temperature=0.1, model="gemini-1.5-pro")
    data = extract_json(raw)
    return ArchitectureModel(**data)
