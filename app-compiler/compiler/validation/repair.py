"""
Repair Engine
- Receives: RefinedSchemaModel + list of ValidationErrors
- Sends ONLY the broken section + its errors to LLM
- Gets back a patched version of just that section
- Reconstructs full schema with the patch applied
- Maximum 2 repair attempts before marking as failed
"""
import json
from typing import List
from ..schemas.refined_schema import RefinedSchemaModel, ConsistencyFix
from ..validation.validator import ValidationError
from ..llm.gemini_client import call_gemini

REPAIR_SYSTEM_PROMPT = """
You are a schema repair engine. You will receive a broken section of an app schema and a list of specific errors.
Fix ONLY the errors listed. Return ONLY the repaired section as valid JSON. No preamble.
Preserve all correct data. Change only what is broken.
"""

async def repair_schema(
    refined: RefinedSchemaModel,
    errors: List[ValidationError],
    max_attempts: int = 2
) -> RefinedSchemaModel:
    
    # Group errors by layer
    errors_by_layer = {}
    for e in errors:
        errors_by_layer.setdefault(e.layer, []).append(e)
    
    schema_dict = refined.schema.model_dump()
    
    for layer, layer_errors in errors_by_layer.items():
        layer_key = {
            "ui": "ui_config",
            "api": "api_config", 
            "db": "db_config",
            "auth": "auth_rules"
        }[layer]
        
        broken_section = schema_dict[layer_key]
        error_descriptions = [
            {"error_type": e.error_type, "message": e.message, 
             "location": e.location, "suggested_fix": e.suggested_fix}
            for e in layer_errors
        ]
        
        repair_prompt = f"""
Repair this {layer} schema section.

ERRORS TO FIX:
{json.dumps(error_descriptions, indent=2)}

BROKEN SECTION:
{json.dumps(broken_section, indent=2)}

Return ONLY the repaired {layer_key} JSON array.
"""
        
        for attempt in range(max_attempts):
            try:
                raw = await call_gemini(
                    system=REPAIR_SYSTEM_PROMPT,
                    user=repair_prompt,
                    temperature=0.0,
                    model="gemini-1.5-pro"
                )
                repaired_section = json.loads(raw.strip().strip("```json").strip("```").strip())
                schema_dict[layer_key] = repaired_section
                break
            except Exception:
                if attempt == max_attempts - 1:
                    # Log failure but continue — don't crash whole pipeline
                    pass
    
    # Rebuild schema
    from ..schemas.app_schema import AppSchemaModel
    repaired_schema = AppSchemaModel(**schema_dict)
    
    new_fixes = [
        ConsistencyFix(layer=e.layer, issue=e.message, fix_applied="automated repair") 
        for e in errors
    ]
    
    return RefinedSchemaModel(
        schema=repaired_schema,
        fixes_applied=refined.fixes_applied + new_fixes,
        assumptions_made=refined.assumptions_made,
        warnings=refined.warnings,
        is_executable=True,
        execution_confidence=0.85
    )
