from pydantic import BaseModel
from typing import List, Dict, Any
from .app_schema import AppSchemaModel

class ConsistencyFix(BaseModel):
    layer: str                         # "ui"|"api"|"db"|"auth"
    issue: str                         # what was wrong
    fix_applied: str                   # what was changed

class RefinedSchemaModel(BaseModel):
    schema: AppSchemaModel             # the corrected schema
    fixes_applied: List[ConsistencyFix]
    assumptions_made: List[str]
    warnings: List[str]
    is_executable: bool                # True if schema passes all validation
    execution_confidence: float        # 0.0 - 1.0
