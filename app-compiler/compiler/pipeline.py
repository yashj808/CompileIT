"""
Pipeline orchestrator. Runs stages sequentially.
Each stage gets previous stage output as context.
"""
import asyncio
from dataclasses import dataclass, field
from typing import Optional
import time

from .stages.stage1_intent import run_stage1
from .stages.stage2_architecture import run_stage2
from .stages.stage3_schema import run_stage3
from .stages.stage4_refinement import run_stage4
from .validation.validator import validate_schema
from .validation.repair import repair_schema
from .schemas.refined_schema import RefinedSchemaModel

@dataclass
class PipelineResult:
    success: bool
    refined_schema: Optional[RefinedSchemaModel]
    stage_timings: dict = field(default_factory=dict)
    retries: int = 0
    failure_reason: Optional[str] = None
    total_tokens_used: int = 0

async def run_pipeline(user_prompt: str, max_retries: int = 2) -> PipelineResult:
    timings = {}
    total_tokens = 0
    retries = 0

    for attempt in range(max_retries + 1):
        try:
            t0 = time.time()
            intent = await run_stage1(user_prompt)
            timings["stage1"] = time.time() - t0

            t0 = time.time()
            architecture = await run_stage2(intent)
            timings["stage2"] = time.time() - t0

            t0 = time.time()
            app_schema = await run_stage3(intent, architecture)
            timings["stage3"] = time.time() - t0

            t0 = time.time()
            refined = await run_stage4(intent, architecture, app_schema)
            timings["stage4"] = time.time() - t0

            # Validate
            t0 = time.time()
            validation_result = validate_schema(refined.schema)
            timings["validation"] = time.time() - t0

            if not validation_result.is_valid:
                # Targeted repair — not full retry
                t0 = time.time()
                repaired = await repair_schema(refined, validation_result.errors)
                timings["repair"] = time.time() - t0
                refined = repaired
                retries += 1

            return PipelineResult(
                success=True,
                refined_schema=refined,
                stage_timings=timings,
                retries=retries,
                total_tokens_used=total_tokens
            )

        except Exception as e:
            retries += 1
            if attempt == max_retries:
                return PipelineResult(
                    success=False,
                    refined_schema=None,
                    failure_reason=str(e),
                    retries=retries
                )

    return PipelineResult(success=False, refined_schema=None, failure_reason="max retries exceeded")
