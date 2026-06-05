"""
Stage 4: Refinement
- Input: IntentModel + ArchitectureModel + AppSchemaModel
- Output: RefinedSchemaModel
- This stage explicitly checks and documents all cross-layer fixes
- It does NOT regenerate from scratch — it patches inconsistencies
"""

from ..schemas.intent import IntentModel
from ..schemas.architecture import ArchitectureModel
from ..schemas.app_schema import AppSchemaModel
from ..schemas.refined_schema import RefinedSchemaModel
from ..llm.gemini_client import call_gemini
from ..prompts.stage4 import STAGE4_SYSTEM_PROMPT, build_stage4_user_prompt
from .stage1_intent import extract_json

async def run_stage4(intent: IntentModel, arch: ArchitectureModel, schema: AppSchemaModel) -> RefinedSchemaModel:
    system = STAGE4_SYSTEM_PROMPT
    intent_json = intent.model_dump_json(indent=2)
    arch_json = arch.model_dump_json(indent=2)
    schema_json = schema.model_dump_json(indent=2)
    user = build_stage4_user_prompt(intent_json, arch_json, schema_json)
    
    raw = await call_gemini(
        system=system,
        user=user,
        temperature=0.1,
        model="gemini-1.5-flash"
    )
    data = extract_json(raw)
    return RefinedSchemaModel(**data)
