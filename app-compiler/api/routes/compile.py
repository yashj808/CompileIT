"""
POST /compile
- Body: { "prompt": "string", "max_retries": 2 }
- Returns: PipelineResult with full refined schema
- Streams stage-by-stage progress via SSE (Server-Sent Events)
"""
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import json
import time
from typing import Optional, Dict, Any

router = APIRouter(prefix="/api")

class CompileRequest(BaseModel):
    prompt: str
    max_retries: int = 2

class CompileResponse(BaseModel):
    success: bool
    schema: Optional[Dict[str, Any]]
    stage_timings: Dict[str, float]
    retries: int
    failure_reason: Optional[str]
    total_latency_ms: float

@router.post("/compile", response_model=CompileResponse)
async def compile_prompt(request: CompileRequest):
    from compiler.pipeline import run_pipeline
    t0 = time.time()
    result = await run_pipeline(request.prompt, request.max_retries)
    latency = (time.time() - t0) * 1000

    return CompileResponse(
        success=result.success,
        schema=result.refined_schema.model_dump() if result.refined_schema else None,
        stage_timings=result.stage_timings,
        retries=result.retries,
        failure_reason=result.failure_reason,
        total_latency_ms=latency
    )

@router.post("/compile/stream")
async def compile_stream(request: CompileRequest):
    """SSE endpoint for real-time stage-by-stage streaming"""
    async def event_generator():
        from compiler.stages.stage1_intent import run_stage1
        from compiler.stages.stage2_architecture import run_stage2
        from compiler.stages.stage3_schema import run_stage3
        from compiler.stages.stage4_refinement import run_stage4

        yield f"data: {json.dumps({'stage': 'start', 'message': 'Pipeline starting'})}\n\n"
        
        try:
            intent = await run_stage1(request.prompt)
            yield f"data: {json.dumps({'stage': 1, 'name': 'intent_extraction', 'result': intent.model_dump()})}\n\n"

            arch = await run_stage2(intent)
            yield f"data: {json.dumps({'stage': 2, 'name': 'architecture_design', 'result': arch.model_dump()})}\n\n"

            schema = await run_stage3(intent, arch)
            yield f"data: {json.dumps({'stage': 3, 'name': 'schema_generation', 'result': schema.model_dump()})}\n\n"

            refined = await run_stage4(intent, arch, schema)
            yield f"data: {json.dumps({'stage': 4, 'name': 'refinement', 'result': refined.model_dump()})}\n\n"
            
            yield f"data: {json.dumps({'stage': 'done'})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'stage': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
